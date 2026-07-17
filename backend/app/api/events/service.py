from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from datetime import date
from typing import Optional, List

from app.models.eventos import Evento
from app.models.organizacion import Organizacion
from app.api.events.schemas import EventoCreate, EventoUpdate, EventoMapPoint, EventoResponse


# ── Consultas públicas ────────────────────────────────────────────────────────

def obtener_eventos_proximos(db: Session, fecha_filtro: date) -> List[Evento]:
    return (
        db.query(Evento)
        .options(joinedload(Evento.organizacion))
        .filter(Evento.fecha >= fecha_filtro, Evento.activo == True)
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
            Evento.fecha >= fecha_hoy,
            Evento.activo == True,
            Evento.organizacion_id.isnot(None),
        )
        .order_by(Evento.fecha.asc())
        .all()
    )

    grupos: dict[int, EventoMapPoint] = {}
    for ev in eventos:
        org = ev.organizacion
        if not org or not org.latitud or not org.longitud:
            continue
        if org.id not in grupos:
            grupos[org.id] = EventoMapPoint(
                organizacion_id=org.id,
                organizacion_nombre=org.nombre,
                latitud=org.latitud,
                longitud=org.longitud,
                total_eventos=0,
                eventos=[],
            )
        grupos[org.id].total_eventos += 1
        grupos[org.id].eventos.append(EventoResponse.model_validate(ev))

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
        .filter(Evento.fecha >= fecha_hoy, Evento.activo == True)
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