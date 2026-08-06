from sqlalchemy.orm import Session
from app.api.STEM_offerings.schemas import OfertaSTEM, OrganizacionProgramas, ModalidadProgramas
import logging
from app.models.organizacion import Organizacion
from app.models.programa import Programa
from app.utils import ttl_cache

logger = logging.getLogger("stem_api.ofertas_stem")

_CACHE_KEY = "oferta_stem"
_CACHE_TTL = 300

def get_oferta_stem(db: Session) -> OfertaSTEM:
    cached = ttl_cache.get(_CACHE_KEY, _CACHE_TTL)
    if cached:
        return cached

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
    organizaciones = db.query(Organizacion).filter(Organizacion.activo == True).all()

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

    # Inicializamos con TODAS las organizaciones activas de la base de datos
    orgs_programas = {}
    for org in organizaciones:
        orgs_programas[org.nombre] = {
            "logo_url": org.logo_url,
            "enfoque_principal": org.enfoque_principal or "No especificado",
            "tipo_organizacion": org.tipo or "No especificado",
            "programas": []
        }

    # Asociamos los programas activos a sus respectivas organizaciones
    for p in programas:
        if p.organizacion:
            nombre_org = p.organizacion.nombre
            if nombre_org in orgs_programas and p.nombre:
                orgs_programas[nombre_org]["programas"].append(p.nombre)

    lista_orgs_programas = [
        OrganizacionProgramas(
            logo_url=datos["logo_url"],
            organizacion=nombre, 
            enfoque_principal=datos["enfoque_principal"],
            tipo_organizacion=datos["tipo_organizacion"],
            programas=datos["programas"]
        )
        for nombre, datos in orgs_programas.items()
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

    result = OfertaSTEM(
        programas_por_area=dict(sorted(areas.items(), key=lambda x: x[1], reverse=True)),
        tipos_actividad_ofrecidos=dict(sorted(actividades.items(), key=lambda x: x[1], reverse=True)),
        organizaciones_con_programas=lista_orgs_programas,
        modalidades_programas=lista_modalidades
    )
    ttl_cache.put(_CACHE_KEY, result)
    return result