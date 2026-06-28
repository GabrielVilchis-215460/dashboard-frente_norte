from pydantic import BaseModel
from typing import List, Dict, Optional

# Pestaña 6 - Modulo 6
class CoberturaColonia(BaseModel):
    nombre: str
    zona: Optional[str]
    latitud: Optional[float]
    longitud: Optional[float]
    num_programas: int
    nivel_oferta: str # Alto | Medio | Bajo | Sin oferta


class CoberturaTerritorial(BaseModel):
    total_colonias_impactadas: int
    por_zona: Dict[str, int]
    colonias_detalle: List[CoberturaColonia]
    zonas_baja_oferta: List[str]
