from pydantic import BaseModel
from typing import List, Dict, Optional

# Pestaña 3 - Modulo 3
class InclusionFemenina(BaseModel):
    pct_promedio_mujeres: float  # promedio de pct_mujeres_mid
    programas_enfocados_mujeres: int # programas con pct > 75%
    programas_ninas_adolescentes: int  # población objetivo = niñez o adolescentes
    por_nivel_educativo: Dict[str, float]