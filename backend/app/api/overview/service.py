from sqlalchemy.orm import Session
from app.models.organizacion import Organizacion
from app.models.programa import Programa
from app.api.overview.schemas import PanoramaGeneral
from app.utils.helpers import count_by_field, mid_volume
import logging

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

    tipos_count = count_by_field(orgs, "tipo")

    # Unión de todas las áreas STEM presentes en los programas activos
    areas: set[str] = set()
    for p in programas:
        areas.update(p.areas_stem or [])

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
        beneficiarios_semestre=beneficiarios,
        colonias_impactadas=len(colonias),
        organizaciones_por_tipo=tipos_count,
        areas_stem_representadas=sorted(areas),
    )
