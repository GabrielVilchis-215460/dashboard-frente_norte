import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.beneficiary_profile.schemas import PerfilBeneficiarios
from app.api.beneficiary_profile.service import get_perfil_beneficiarios

router = APIRouter(prefix="/beneficiarios", tags=["Perfil de Beneficiarios"])

logger = logging.getLogger("stem_api.beneficiarios")

@router.get(
    "/",
    response_model=PerfilBeneficiarios,
    summary="Perfil de beneficiarios del ecosistema",
    description="""
Retorna la distribución de beneficiarios por grupo etario, nivel educativo y zona.

Alimenta el **Módulo 2 — Perfil de Beneficiarios** del dashboard.
    """,
    responses={
        200: {"description": "Perfil calculado exitosamente"},
        500: {"description": "Error interno al calcular métricas"},
    },
)
def perfil_beneficiarios(db: Session = Depends(get_db)) -> PerfilBeneficiarios:
    """Módulo 2 — Perfil de beneficiarios del ecosistema."""
    try:
        return get_perfil_beneficiarios(db)
    except Exception as exc:
        logger.error("Error en /metricas/beneficiarios: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Error al calcular el perfil de beneficiarios.")

