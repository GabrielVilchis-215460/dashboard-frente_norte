import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.STEM_offerings.schemas import OfertaSTEM
from app.api.STEM_offerings.service import get_oferta_stem

router = APIRouter(prefix="/oferta_stem", tags=["Oferta STEM del Ecosistema"])

logger = logging.getLogger("stem_api.ofertas_stem")

@router.get(
    "/",
    response_model=OfertaSTEM,
    summary="Análisis de la oferta STEM del ecosistema",
    description="""
Retorna la distribución de programas por área STEM, tipo de actividad
y la matriz de especialización de organizaciones.

Alimenta el **Módulo 4 — Oferta STEM** del dashboard.
    """,
    responses={
        200: {"description": "Análisis de oferta calculado"},
        500: {"description": "Error interno al calcular métricas"},
    },
)
def oferta_stem(db: Session = Depends(get_db)) -> OfertaSTEM:
    """Módulo 4 — Oferta STEM del ecosistema."""
    try:
        return get_oferta_stem(db)
    except Exception as exc:
        logger.error("Error en /metricas/oferta: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Error al calcular la oferta STEM.")

