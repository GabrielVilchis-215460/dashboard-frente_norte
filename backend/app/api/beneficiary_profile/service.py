import logging
from collections import Counter
from sqlalchemy.orm import Session
from app.models.programa import Programa
from app.api.beneficiary_profile.schemas import PerfilBeneficiarios
from app.utils.helpers import count_by_field
from app.utils import ttl_cache

logger = logging.getLogger("stem_api.beneficiarios")

_CACHE_KEY = "perfil_beneficiarios"
_CACHE_TTL = 300

def get_perfil_beneficiarios(db: Session) -> PerfilBeneficiarios:
    cached = ttl_cache.get(_CACHE_KEY, _CACHE_TTL)
    if cached:
        return cached

    logger.info("Calculando perfil de beneficiarios")
    programas = db.query(Programa).filter(Programa.activo == True).all()

    result = PerfilBeneficiarios(
        por_grupo_etario = count_by_field(programas, "poblacion_objetivo"),
        por_nivel_educativo = count_by_field(programas, "nivel_educativo"),
        por_zona = count_by_field(programas, "zona"),
    )
    ttl_cache.put(_CACHE_KEY, result)
    return result
