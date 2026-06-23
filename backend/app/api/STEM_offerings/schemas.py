from pydantic import BaseModel
from typing import List, Dict, Optional

# Pestaña 4 - Modulo 4
class OfertaSTEM(BaseModel):
    programas_por_area: Dict[str, int] # {Robótica: 5, IA: 3, ...}
    tipos_actividad_ofrecidos: Dict[str, int]  # {Talleres: 7, Mentorías: 3, ...}
    organizaciones_por_especialidad: Dict[str, int]