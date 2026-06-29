import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.overview.schemas import PanoramaGeneral
from app.api.overview.service import get_panorama

logger = logging.getLogger("stem_api.panorama_general")

router = APIRouter(prefix="/panorama_general", tags=["Panorama General"])

@router.get(
    "/",
    response_model=PanoramaGeneral,
    summary="Indicadores generales del ecosistema",
    description="""
Retorna los 8 KPIs principales del ecosistema STEM de Ciudad Juárez.

Alimenta el **Módulo 1 — Panorama General** del dashboard.

Incluye:
- Total de organizaciones y programas activos
- Beneficiarios estimados en el semestre
- Porcentaje de beneficiarias mujeres
- Porcentaje de programas con enfoque integral
- Colonias impactadas
- Distribución de organizaciones por tipo
- Conteo de organizaciones por área STEM
- Top organizaciones con mas programas activos
- Preview del mapa con logos de las instituciones
    """,
    responses={
        200: {"description": "Indicadores calculados exitosamente"},
        500: {"description": "Error interno al calcular métricas"},
    },
)
def panorama(db: Session = Depends(get_db)) -> PanoramaGeneral:
    """Módulo 1 — KPIs generales del ecosistema STEM."""
    try:
        return get_panorama(db)
    except Exception as exc:
        logger.error("Error en /metricas/panorama: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Error al calcular el panorama general.")
