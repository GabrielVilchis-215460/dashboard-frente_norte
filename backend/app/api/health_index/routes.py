import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.health_index.schemas import IndiceSaludEcosistema
from app.api.health_index.service import get_indice_salud

router = APIRouter(prefix="/indice_salud", tags=["Indice de Salud del Ecosistema"])

logger = logging.getLogger("stem_api.indice_salud")

@router.get(
    "/indice-salud",
    response_model=IndiceSaludEcosistema,
    summary="Índice de Salud del Ecosistema STEM (ISE)",
    description="""
Calcula el Índice de Salud del Ecosistema STEM de Ciudad Juárez.

**Fórmula:**
`ISE = Cobertura×0.25 + Diversidad×0.20 + Inclusión×0.20 + Alcance×0.20 + Madurez×0.15`

**Niveles:**
- EXCELENTE: ≥ 75
- BUENO: ≥ 50
- EN DESARROLLO: ≥ 25
- CRÍTICO: < 25

Alimenta el **Módulo 8 — Índice de Salud** del dashboard.
    """,
    responses={
        200: {"description": "ISE calculado exitosamente"},
        500: {"description": "Error interno al calcular el ISE"},
    },
)
def indice_salud(db: Session = Depends(get_db)) -> IndiceSaludEcosistema:
    """Indicador estratégico — Índice de Salud del Ecosistema STEM."""
    try:
        return get_indice_salud(db)
    except Exception as exc:
        logger.error("Error en /metricas/indice-salud: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Error al calcular el Índice de Salud.")
