import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.territorial_coverage.schemas import CoberturaTerritorial
from app.api.territorial_coverage.service import get_cobertura

router = APIRouter(prefix="/cobertura_territorial", tags=["Cobertura Territorial"])

logger = logging.getLogger("stem_api.cobertura_territorial")

@router.get(
    "/",
    response_model=CoberturaTerritorial,
    summary="Cobertura territorial del ecosistema STEM",
    description="""
Retorna la cobertura del ecosistema STEM por colonia y zona de Ciudad Juárez.
Identifica zonas con baja oferta para priorización estratégica.

Alimenta el **Módulo 6 — Cobertura Territorial** del dashboard.
    """,
    responses={
        200: {"description": "Análisis de cobertura calculado"},
        500: {"description": "Error interno al calcular métricas"},
    },
)
def cobertura(db: Session = Depends(get_db)) -> CoberturaTerritorial:
    """Módulo 6 — Cobertura territorial del ecosistema."""
    try:
        return get_cobertura(db)
    except Exception as exc:
        logger.error("Error en /metricas/cobertura: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Error al calcular la cobertura territorial.")

