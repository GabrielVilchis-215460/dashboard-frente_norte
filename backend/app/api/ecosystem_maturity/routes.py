import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.ecosystem_maturity.service import get_madurez
from app.api.ecosystem_maturity.schemas import MadurezEcosistema

router = APIRouter(prefix="/madurez_ecosistema")

logger = logging.getLogger("stem_api.madurez_ecosistema")

@router.get(
    "/",
    response_model=MadurezEcosistema,
    summary="Madurez de los programas del ecosistema",
    description="""
Retorna la distribución de programas y organizaciones por etapa de madurez:
Exploración → Implementación → Escalamiento.

Alimenta el **Módulo 5 — Madurez del Ecosistema** del dashboard.
    """,
    responses={
        200: {"description": "Análisis de madurez calculado"},
        500: {"description": "Error interno al calcular métricas"},
    },
)
def madurez(db: Session = Depends(get_db)) -> MadurezEcosistema:
    """Módulo 5 — Madurez de los programas STEM."""
    try:
        return get_madurez(db)
    except Exception as exc:
        logger.error("Error en /metricas/madurez: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Error al calcular la madurez del ecosistema.")
