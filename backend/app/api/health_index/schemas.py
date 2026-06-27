from pydantic import BaseModel
from typing import List, Dict, Optional

# Pestaña 8 - Modulo 8
class DimensionISE(BaseModel):
    nombre: str
    score: float # 0-100
    peso: float # peso en la fórmula
    descripcion: str

class IndiceSaludEcosistema(BaseModel):
    score_global: float # 0-100
    nivel: str # Crítico | En desarrollo | Bueno | Excelente
    dimensiones: List[DimensionISE]
    # Cobertura * 0.25 + Diversidad * 0.20 + Inclusión * 0.20
    # + Alcance * 0.20 + Madurez * 0.15
