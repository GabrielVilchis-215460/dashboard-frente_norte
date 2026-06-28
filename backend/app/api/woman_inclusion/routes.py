import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.woman_inclusion.schemas import InclusionFemenina
from app.api.woman_inclusion.service import get_inclusion_femenina

router = APIRouter(prefix="/inclusion", tags=["Inclusion Femenina al Ecosistema"])

logger = logging.getLogger("stem_api.inclusion_femenina")

@router.get(
    "/",
    response_model=InclusionFemenina,
    summary="Indicadores de inclusión y participación femenina",
    description="""
Retorna los indicadores de inclusión de mujeres en el ecosistema STEM.

Alimenta el **Módulo 3 — Inclusión y Género** del dashboard.

Incluye:
- Porcentaje promedio de mujeres en los programas
- Cantidad de programas con >75% de participación femenina
- Distribución por nivel educativo
    """,
    responses={
        200: {"description": "Indicadores de inclusión calculados"},
        500: {"description": "Error interno al calcular métricas"},
    },
)
def inclusion_femenina(db: Session = Depends(get_db)) -> InclusionFemenina:
    """Módulo 3 — Inclusión y participación femenina."""
    try:
        return get_inclusion_femenina(db)
    except Exception as exc:
        logger.error("Error en /metricas/inclusion: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Error al calcular indicadores de inclusión.")
