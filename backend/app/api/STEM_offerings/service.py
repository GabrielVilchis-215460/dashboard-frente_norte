from sqlalchemy.orm import Session
from app.api.STEM_offerings.schemas import OfertaSTEM, OrganizacionProgramas, ModalidadProgramas
import logging
from app.models.organizacion import Organizacion
from app.models.programa import Programa

logger = logging.getLogger("stem_api.ofertas_stem")

def get_oferta_stem(db: Session) -> OfertaSTEM:
    """
    Calcula el análisis de oferta STEM del ecosistema.

    Agrega programas por área STEM y tipo de actividad, y organizaciones
    por área de especialización para la matriz heatmap.

    Args:
        db: Sesión activa de SQLAlchemy.

    Returns:
        OfertaSTEM: Distribuciones de programas y organizaciones por área.
    """
    logger.info("Calculando oferta STEM")
    programas = db.query(Programa).filter(Programa.activo == True).all()
    orgs = db.query(Organizacion).filter(Organizacion.activo == True).all()

    # Conteo de programas por área STEM (un programa puede tener múltiples áreas)
    areas: dict[str, int] = {}
    for p in programas:
        for area in (p.areas_stem or []):
            areas[area] = areas.get(area, 0) + 1

    # Conteo de programas por tipo de actividad
    actividades: dict[str, int] = {}
    for p in programas:
        for tipo in (p.tipos_actividad or []):
            actividades[tipo] = actividades.get(tipo, 0) + 1

    # Conteo de organizaciones por área de especialización (para heatmap)
    especialidad: dict[str, int] = {}
    for org in orgs:
        for area in (org.areas_stem or []):
            especialidad[area] = especialidad.get(area, 0) + 1

    orgs_programas = {}
    for p in programas: 
        nombre_org = p.organizacion.nombre if p.organizacion else "Organización Desconocida"

        if nombre_org not in orgs_programas:
            orgs_programas[nombre_org] = []

        if p.nombre:
            orgs_programas[nombre_org].append(p.nombre)

    lista_orgs_programas = [
        OrganizacionProgramas(organizacion=k, programas=v)
        for k, v in orgs_programas.items()
    ]

    modalidades_conteo = {}
    for p in programas:
        mod = getattr(p, 'modalidad', 'No especificada')
        if not mod: 
            mod = 'No especificada'
            
        modalidades_conteo[mod] = modalidades_conteo.get(mod, 0) + 1

    lista_modalidades = [
        ModalidadProgramas(name=k, value=v)
        for k, v in modalidades_conteo.items()
    ]

    return OfertaSTEM(
        programas_por_area=dict(sorted(areas.items(), key=lambda x: x[1], reverse=True)),
        tipos_actividad_ofrecidos=dict(sorted(actividades.items(), key=lambda x: x[1], reverse=True)),
        organizaciones_por_especialidad=dict(sorted(especialidad.items(), key=lambda x: x[1], reverse=True)),
        organizaciones_con_programas=lista_orgs_programas,
        modalidades_programas=lista_modalidades
    )
