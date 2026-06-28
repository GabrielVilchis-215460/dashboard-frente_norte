from pydantic import BaseModel
from typing import List, Dict, Optional

class ProgramaDetalle(BaseModel):
    nombre: str
    organizacion: str
    pct_mujeres: float  
    descripcion: Optional[str] = None

class RangoParticipacion(BaseModel):
    rango: str   # Ej: "0% - 25%"
    cantidad: int # Ej: 21
    
# Pestaña 3 - Modulo 3
class InclusionFemenina(BaseModel):
    pct_promedio_mujeres: float
    total_ninas_adolescentes: int 
    total_enfocados_mujeres: int  
    distribucion_por_rango: List[RangoParticipacion] 
    por_nivel_educativo: Dict[str, float]
    carrusel_programas_destacados: List[ProgramaDetalle]