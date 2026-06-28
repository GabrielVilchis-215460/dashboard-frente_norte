from app.models.organizacion import Organizacion
from app.models.programa import Programa
import logging
from sqlalchemy.orm import Session
from app.api.ecosystem_maturity.schemas import MadurezEcosistema
from app.utils.constants import MADUREZ_ORDEN
from app.utils.helpers import mid_volume

logger = logging.getLogger("stem_api.madurez_ecosistema")

def get_madurez(db: Session) -> MadurezEcosistema:
    """
    Calcula la madurez de programas y organizaciones del ecosistema STEM.

    La madurez de una organización se determina por el programa más avanzado
    que tenga activo (Escalamiento > Implementación > Exploración).

    Args:
        db: Sesión activa de SQLAlchemy.

    Returns:
        MadurezEcosistema: Distribución por etapa de madurez con beneficiarios.
    """
    logger.info("Calculando madurez del ecosistema")
    programas = db.query(Programa).filter(Programa.activo == True).all()
    orgs = db.query(Organizacion).filter(Organizacion.activo == True).all()

    # Distribución de programas y beneficiarios por etapa de madurez
    por_etapa: dict[str, int] = {}
    beneficiarios_etapa: dict[str, int] = {}
    for p in programas:
        etapa = p.madurez or "Sin clasificar"
        por_etapa[etapa] = por_etapa.get(etapa, 0) + 1
        vol = mid_volume(p.volumen_semestral)
        beneficiarios_etapa[etapa] = beneficiarios_etapa.get(etapa, 0) + vol

    # Madurez de cada organización = madurez del programa más avanzado
    org_madurez: dict[str, int] = {}
    for org in orgs:
        niveles = [p.madurez for p in org.programas if p.madurez and p.activo]
        if niveles:
            top = max(niveles, key=lambda x: MADUREZ_ORDEN.get(x, 0))
        else:
            top = "Sin clasificar"
        org_madurez[top] = org_madurez.get(top, 0) + 1

    return MadurezEcosistema(
        por_etapa=por_etapa,
        beneficiarios_por_etapa=beneficiarios_etapa,
        organizaciones_por_madurez=org_madurez,
    )
