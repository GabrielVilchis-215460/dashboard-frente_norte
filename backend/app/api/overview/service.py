from sqlalchemy.orm import Session
from app.models.organizacion import Organizacion
from app.models.programa import Programa
from app.api.overview.schemas import PanoramaGeneral, MapaPreview, TopOrganizacion
from app.utils.helpers import count_by_field, mid_volume, mid_pct
import logging
from sqlalchemy import func
from app.models.eventos import Evento

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
    # Contador para mostrar el total de eventos activos
    total_eventos = db.query(func.count(Evento.id)).filter(Evento.activo == True).scalar()

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
        beneficiarios_semestre=beneficiarios,
        colonias_impactadas=len(colonias),
        pct_mujeres_beneficiarias=pct_mujeres, 
        pct_programas_enfoque_integral=pct_integral, 
        organizaciones_por_tipo=tipos_count,
        areas_stem_representadas=dict(sorted(areas_conteo.items(), key=lambda x: x[1], reverse=True)), # MODIFICADO
        top_organizaciones=top_organizaciones,
        preview_mapa=preview_marcadores
    )
