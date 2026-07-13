from sqlalchemy.orm import Session
from app.models.organizacion import Organizacion
from app.models.programa import Programa
from app.api.overview.schemas import PanoramaGeneral, MapaPreview, TopOrganizacion, DistribucionItem, HistoricoTrimestralItem
from app.utils.helpers import count_by_field, mid_volume, mid_pct
import logging
from sqlalchemy import func
from app.models.eventos import Evento
from app.api.events.service import contar_eventos_activos
from datetime import date

logger = logging.getLogger("stem_api.panorama_general")

#  Módulo 1: Panorama General 

def get_panorama(db: Session) -> PanoramaGeneral:
    """
    Calcula y retorna los indicadores generales del ecosistema STEM.

    Consulta organizaciones y programas activos para agregar los KPIs
    principales que se muestran en el módulo Panorama General.

    Args:
        db: Sesión activa de SQLAlchemy.

    Returns:
        PanoramaGeneral: Schema con los 6 KPIs y las distribuciones.

    Raises:
        Exception: Cualquier error de consulta a la BD.
    """

    orgs = db.query(Organizacion).filter(Organizacion.activo == True).all()
    programas = db.query(Programa).filter(Programa.activo == True).all()

    fecha_hoy = date.today()
    # Contador para mostrar el total de eventos activos
    #total_eventos = contar_eventos_activos(db)
    total_eventos = db.query(Evento).filter(Evento.fecha >= fecha_hoy, Evento.activo == True).count()
    
    orgs_con_eventos = (
        db.query(Evento.organizacion_id)
        .filter(Evento.fecha >= fecha_hoy, Evento.activo == True)
        .distinct()
        .count()
    )

    # Distribución de Enfoque (%) para Gráfica de Pastel
    total_enfoques = db.query(Evento).filter(Evento.enfoque.isnot(None), Evento.activo == True).count()
    eventos_por_enfoque = []
    
    if total_enfoques > 0:
        res_enfoque = (
            db.query(Evento.enfoque, func.count(Evento.id))
            .filter(Evento.enfoque.isnot(None), Evento.activo == True)
            .group_by(Evento.enfoque).all()
        )
        eventos_por_enfoque = [
            DistribucionItem(label=row[0], count=row[1], porcentaje=round((row[1] / total_enfoques) * 100, 1))
            for row in res_enfoque
        ]

    # Distribución de Tipo (%) para Gráfica de Pastel
    total_tipos = db.query(Evento).filter(Evento.tipo.isnot(None), Evento.activo == True).count()
    eventos_por_tipo = []

    if total_tipos > 0:
        res_tipo = (
            db.query(Evento.tipo, func.count(Evento.id))
            .filter(Evento.tipo.isnot(None), Evento.activo == True)
            .group_by(Evento.tipo).all()
        )
        eventos_por_tipo = [
            DistribucionItem(label=row[0], count=row[1], porcentaje=round((row[1] / total_tipos) * 100, 1))
            for row in res_tipo
        ]

    # Histórico de 4 Trimestres para Gráfica de Línea
    historico_linea = []
    trimestres_aux = []

    for i in range(4):
        mes_calc = fecha_hoy.month - (3 * i)
        anio_calc = fecha_hoy.year
        while mes_calc <= 0:
            mes_calc += 12
            anio_calc -= 1
        q_num = (mes_calc - 1) // 3 + 1
        
        start_date = date(anio_calc, (q_num - 1) * 3 + 1, 1)
        end_date = date(anio_calc + 1, 1, 1) if q_num == 4 else date(anio_calc, q_num * 3 + 1, 1)
        
        trimestres_aux.append({"label": f"Q{q_num} {anio_calc}", "start": start_date, "end": end_date})
    
    trimestres_aux.reverse() # Ordenar cronológicamente en el eje X
    for q in trimestres_aux:
        cant = db.query(Evento).filter(Evento.fecha >= q["start"], Evento.fecha < q["end"], Evento.activo == True).count()
        historico_linea.append(HistoricoTrimestralItem(trimestre=q["label"], eventos=cant))

    top_orgs = (
        db.query(
            Organizacion.nombre,
            func.count(Programa.id).label('total_programas') 
        )
        .join(Programa, Organizacion.id == Programa.organizacion_id)
        .filter(Organizacion.activo == True, Programa.activo == True)
        .group_by(Organizacion.id, Organizacion.nombre)
        .order_by(func.count(Programa.id).desc())
        .limit(5)
        .all()
    )

    mapa = (
        db.query(
            Organizacion.id,
            Organizacion.nombre,
            Organizacion.latitud,
            Organizacion.longitud,
            Organizacion.logo_url,
            func.count(Programa.id).label("total_programas")
        )
        .outerjoin(Programa, (Organizacion.id == Programa.organizacion_id) & (Programa.activo == True))
        .filter(
            Organizacion.activo == True,
            Organizacion.latitud.isnot(None),
            Organizacion.longitud.isnot(None)
        )
        .group_by(Organizacion.id)
        .order_by(func.count(Programa.id).desc()) # Traer las que tienen más impacto primero
        .limit(15) # Límite para el preview por el momento
        .all()
    )

    preview_marcadores = [
        MapaPreview(
            id=row.id,
            nombre=row.nombre,
            latitud=row.latitud,
            longitud=row.longitud,
            logo_url=row.logo_url,
            total_programas=row.total_programas
        )
        for row in mapa
    ]

    top_organizaciones = [
        TopOrganizacion(nombre=row.nombre, total_programas=row.total_programas)
        for row in top_orgs
    ]

    tipos_count = count_by_field(orgs, "tipo")

    pcts_mujeres = [mid_pct(p.pct_mujeres_rango) for p in programas if p.pct_mujeres_rango]
    pct_mujeres = round(sum(pcts_mujeres) / len(pcts_mujeres), 1) if pcts_mujeres else 0.0

    integrales_count = sum(1 for p in programas if p.areas_stem and len(p.areas_stem) > 1)
    pct_integral = round((integrales_count / len(programas)) * 100, 1) if programas else 0.0

    areas_conteo: dict[str, int] = {}
    for org in orgs:
        for area in (org.areas_stem or []):
            areas_conteo[area] = areas_conteo.get(area, 0) + 1

    # Unión de todas las colonias impactadas
    colonias: set[str] = set()
    for p in programas:
        colonias.update(p.colonias_impacto or [])

    # Suma de beneficiarios usando el valor medio de cada rango
    beneficiarios = sum(mid_volume(p.volumen_semestral) for p in programas)

    logger.info(
        "Panorama: %d orgs, %d programas, %d beneficiarios, %d colonias",
        len(orgs), len(programas), beneficiarios, len(colonias),
    )

    return PanoramaGeneral(
        total_organizaciones=len(orgs),
        total_programas_activos=len(programas),
        total_eventos_activos=total_eventos,
        organizaciones_con_eventos_activos=orgs_con_eventos,
        beneficiarios_semestre=beneficiarios,
        colonias_impactadas=len(colonias),
        pct_mujeres_beneficiarias=pct_mujeres, 
        pct_programas_enfoque_integral=pct_integral, 
        organizaciones_por_tipo=tipos_count,
        areas_stem_representadas=dict(sorted(areas_conteo.items(), key=lambda x: x[1], reverse=True)), # MODIFICADO
        top_organizaciones=top_organizaciones,
        distribucion_eventos_enfoque=eventos_por_enfoque, 
        distribucion_eventos_tipo=eventos_por_tipo,       
        historico_eventos_trimestral=historico_linea,
        preview_mapa=preview_marcadores
    )
