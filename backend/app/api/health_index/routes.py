import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.health_index.schemas import EcosistemaResponse, IndiceSaludResponse
from app.api.health_index.service import calcular_brechas, get_indice
from app.models.ecosistema import Ecosistema
from app.models.indicadores import Indicador
from app.models.benchmark_valores import BenchmarkValor
from sqlalchemy import text

router = APIRouter(prefix="/indice_salud", tags=["Indice de Salud del Ecosistema"])

logger = logging.getLogger("stem_api.indice_salud")

@router.get("", response_model=IndiceSaludResponse)
def get_indice_salud(db: Session = Depends(get_db)):
    """
    Endpoint principal que obtiene los KPIs, evolución y benchmark 
    para el ecosistema Ciudad Juárez de forma automática.
    """
    return get_indice(db=db)

@router.get("/{ecosistema_id}/brechas", response_model=EcosistemaResponse)
def obtener_brechas(db: Session = Depends(get_db)):
    """
    Endpoint para consultar las brechas y fortalezas del ecosistema STEM 
    comparado con sus referentes.
    """
    return calcular_brechas(db=db)

@router.delete("/seed-test-data")
def limpiar_datos_sinteticos(db: Session = Depends(get_db)):
    """
    Elimina los ecosistemas y sus benchmarks, y reinicia los contadores 
    de ID de ambas tablas a 1, conservando intactos los indicadores[cite: 1, 2, 3].
    """
    try:
        # TRUNCATE con CASCADE limpia las tablas y RESTART IDENTITY reinicia los IDs a 1.
        # Respetamos la tabla 'indicadores' para que no sea tocada.
        db.execute(text("TRUNCATE TABLE benchmark_valores, ecosistemas RESTART IDENTITY CASCADE;"))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al limpiar y reiniciar IDs: {str(e)}")

    return {
        "mensaje": "¡Datos depurados con éxito y contadores de ID reiniciados a 1!"
    }