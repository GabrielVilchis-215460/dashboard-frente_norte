from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
from datetime import date
from typing import Optional, List, Tuple

from app.models.eventos import Evento
from app.models.organizacion import Organizacion
from app.api.events.schemas import EventoCreate, EventoUpdate, EventoMapPoint, EventoResponse


# ── Consultas públicas ────────────────────────────────────────────────────────

def obtener_eventos_proximos(db: Session, fecha_filtro: date) -> List[Evento]:
    return (
        db.query(Evento)
        .options(joinedload(Evento.organizacion))
        #.filter(Evento.fecha >= fecha_filtro, Evento.activo == True)
        .filter(
            Evento.activo == True,
            or_(
                Evento.fecha >= fecha_filtro,
                and_(Evento.fecha_fin.isnot(None), Evento.fecha_fin >= fecha_filtro)
            )
        )
        .order_by(Evento.fecha.asc())
        .all()
    )

def obtener_historial_eventos(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    organizacion_id: Optional[int] = None,
    tipo: Optional[str] = None,
    enfoque: Optional[str] = None,
) -> List[Evento]:
    fecha_hoy = date.today()
    q = (
        db.query(Evento)
        .options(joinedload(Evento.organizacion))
        .filter(Evento.fecha < fecha_hoy)
    )
    if organizacion_id:
        q = q.filter(Evento.organizacion_id == organizacion_id)
    if tipo:
        q = q.filter(Evento.tipo == tipo)
    if enfoque:
        q = q.filter(Evento.enfoque == enfoque)
    return q.order_by(Evento.fecha.desc()).offset(skip).limit(limit).all()

def obtener_eventos_mapa(db: Session) -> List[EventoMapPoint]:
    """Agrupa eventos próximos activos por organización (con coordenadas)."""
    fecha_hoy = date.today()
    eventos = (
        db.query(Evento)
        .options(joinedload(Evento.organizacion))
        .filter(
            Evento.activo == True,
            # próximo: aún no empieza, O ya empezó pero aún no termina
            or_(
                Evento.fecha >= fecha_hoy,
                and_(Evento.fecha_fin.isnot(None), Evento.fecha_fin >= fecha_hoy),
            ),
            # tiene coordenadas propias O viene de una org con coordenadas
            or_(
                and_(Evento.latitud.isnot(None), Evento.longitud.isnot(None)),
                Evento.organizacion_id.isnot(None),
            ),
        )
        .order_by(Evento.fecha.asc())
        .all()
    )

    grupos: dict[int, EventoMapPoint] = {}
    for ev in eventos:
        # Coordenadas: primero las del propio evento, luego las de la org
        lat = ev.latitud or (ev.organizacion.latitud if ev.organizacion else None)
        lng = ev.longitud or (ev.organizacion.longitud if ev.organizacion else None)
        if not lat or not lng:
            continue

        org = ev.organizacion
        org_id = org.id if org else ev.id * -1  # clave única si no hay org
        org_nombre = org.nombre if org else ev.nombre

        if org_id not in grupos:
            grupos[org_id] = EventoMapPoint(
                organizacion_id=org.id if org else None,
                organizacion_nombre=org_nombre,
                latitud=lat,
                longitud=lng,
                total_eventos=0,
                eventos=[],
            )
        grupos[org_id].total_eventos += 1
        grupos[org_id].eventos.append(EventoResponse.model_validate(ev))

    return list(grupos.values())

def obtener_metricas_eventos(db: Session) -> dict:
    """Agrupa los KPIs específicos del módulo de Eventos"""
    return {
        "total_eventos_activos": contar_eventos_activos(db),
        "organizaciones_con_eventos_activos": contar_organizaciones_con_eventos_activos(db),
        "distribucion_eventos_enfoque": obtener_distribucion(db, Evento.enfoque),
        "distribucion_eventos_tipo": obtener_distribucion(db, Evento.tipo),
        "historico_eventos_trimestral": obtener_historico_trimestral(db),
    }

def obtener_eventos_publico(
    db: Session,
    q: Optional[str] = None,
    tipo: Optional[str] = None,
    enfoque: Optional[str] = None,
    orden: str = "recientes",  # "recientes" | "populares"
    skip: int = 0,
    limit: int = 20,
) -> Tuple[int, List[Evento]]:
    """
    Listado público de eventos próximos (para la página /eventos).
    Siempre filtra activos y no vencidos. Devuelve (total, items) para
    poder mostrar el contador de resultados en la UI.
    """
    fecha_hoy = date.today()
 
    query = (
        db.query(Evento)
        .options(joinedload(Evento.organizacion))
        .filter(
            Evento.activo == True,
            or_(
                Evento.fecha >= fecha_hoy,
                and_(Evento.fecha_fin.isnot(None), Evento.fecha_fin >= fecha_hoy),
            ),
        )
    )
 
    if q:
        like = f"%{q}%"
        query = query.outerjoin(Evento.organizacion).filter(
            or_(Evento.nombre.ilike(like), Organizacion.nombre.ilike(like))
        )
    if tipo:
        query = query.filter(Evento.tipo == tipo)
    if enfoque:
        query = query.filter(Evento.enfoque == enfoque)
 
    total = query.count()
 
    if orden == "populares":
        query = query.order_by(Evento.vistas.desc(), Evento.fecha.asc())
    else:
        query = query.order_by(Evento.fecha.asc())
 
    items = query.offset(skip).limit(limit).all()
    return total, items
 
def incrementar_vistas(db: Session, evento_id: int) -> None:
    """Incrementa en 1 el contador de vistas de un evento."""
    db.query(Evento).filter(Evento.id == evento_id).update(
        {Evento.vistas: Evento.vistas + 1}
    )
    db.commit()
 
# ── CRUD administrativo ───────────────────────────────────────────────────────
def crear_evento(db: Session, data: EventoCreate) -> Evento:
    evento = Evento(**data.model_dump())
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


def actualizar_evento(db: Session, evento_id: int, data: EventoUpdate) -> Optional[Evento]:
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        return None
    cambios = data.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(evento, campo, valor)
    db.commit()
    db.refresh(evento)
    return evento


def toggle_evento(db: Session, evento_id: int) -> Optional[Evento]:
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        return None
    evento.activo = not evento.activo
    db.commit()
    db.refresh(evento)
    return evento


def obtener_evento_por_id(db: Session, evento_id: int) -> Optional[Evento]:
    return (
        db.query(Evento)
        .options(joinedload(Evento.organizacion))
        .filter(Evento.id == evento_id)
        .first()
    )


def listar_todos_eventos_admin(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    solo_activos: Optional[bool] = None,
    organizacion_id: Optional[int] = None,
) -> List[Evento]:
    q = db.query(Evento).options(joinedload(Evento.organizacion))
    if solo_activos is not None:
        q = q.filter(Evento.activo == solo_activos)
    if organizacion_id:
        q = q.filter(Evento.organizacion_id == organizacion_id)
    return q.order_by(Evento.fecha.desc()).offset(skip).limit(limit).all()


# ── Auxiliares (usados internamente para las métricas) ─────────────────────────

def contar_eventos_activos(db: Session) -> int:
    fecha_hoy = date.today()
    return db.query(Evento).filter(
        Evento.fecha >= fecha_hoy, Evento.activo == True
    ).count()


def contar_organizaciones_con_eventos_activos(db: Session) -> int:
    fecha_hoy = date.today()
    return (
        db.query(Evento.organizacion_id)
        .filter(
            Evento.activo == True,
            or_(
                Evento.fecha >= fecha_hoy,
                and_(Evento.fecha_fin.isnot(None), Evento.fecha_fin >= fecha_hoy)
            )
        )
        .distinct()
        .count()
    )

def obtener_distribucion(db: Session, columna_modelo):
    total = db.query(Evento).filter(
        columna_modelo.isnot(None), Evento.activo == True
    ).count()
    if total == 0:
        return []
    resultados = db.query(columna_modelo, func.count(Evento.id)).filter(
        columna_modelo.isnot(None), Evento.activo == True
    ).group_by(columna_modelo).all()
    return [
        {"label": nombre, "count": cnt, "porcentaje": round(cnt / total * 100, 2)}
        for nombre, cnt in resultados
    ]

def obtener_historico_trimestral(db: Session):
    hoy = date.today()
    trimestres_info = []
    for i in range(4):
        mes_calculo = hoy.month - (3 * i)
        año_calculo = hoy.year
        while mes_calculo <= 0:
            mes_calculo += 12
            año_calculo -= 1
        trimestre_num = (mes_calculo - 1) // 3 + 1
        mes_inicio = (trimestre_num - 1) * 3 + 1
        mes_fin = trimestre_num * 3
        fecha_inicio_q = date(año_calculo, mes_inicio, 1)
        fecha_fin_q = (
            date(año_calculo + 1, 1, 1) if mes_fin == 12
            else date(año_calculo, mes_fin + 1, 1)
        )
        trimestres_info.append({
            "label": f"Q{trimestre_num} {año_calculo}",
            "inicio": fecha_inicio_q,
            "fin": fecha_fin_q,
        })
    trimestres_info.reverse()
    return [
        {
            "trimestre": q["label"],
            "eventos": db.query(Evento).filter(
                Evento.fecha >= q["inicio"],
                Evento.fecha < q["fin"],
                Evento.activo == True,
            ).count(),
        }
        for q in trimestres_info
    ]