import logging
from collections import Counter
from sqlalchemy.orm import Session
from app.models.programa import Programa
from app.api.beneficiary_profile.schemas import PerfilBeneficiarios
from app.utils.helpers import count_by_field

logger = logging.getLogger("stem_api.beneficiarios")

def get_perfil_beneficiarios(db: Session) -> PerfilBeneficiarios:
    """
    Calcula el perfil de beneficiarios del ecosistema STEM.

    Agrega programas activos por grupo etario (población objetivo),
    nivel educativo y zona geográfica.

    Args:
        db: Sesión activa de SQLAlchemy.

    Returns:
        PerfilBeneficiarios: Distribuciones por grupo etario, nivel y zona.
    """
    logger.info("Calculando perfil de beneficiarios")
    programas = db.query(Programa).filter(Programa.activo == True).all()

    return PerfilBeneficiarios(
        por_grupo_etario = count_by_field(programas, "poblacion_objetivo"),
        por_nivel_educativo = count_by_field(programas, "nivel_educativo"),
        por_zona = count_by_field(programas, "zona"),
    )
