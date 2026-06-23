from pydantic import BaseModel
from typing import List, Dict, Optional

# Modulo 2 - pestaña 2
class PerfilBeneficiarios(BaseModel):
    por_grupo_etario: Dict[str, int]  # {Niñez: 3, Adolescentes: 2, ...}
    por_nivel_educativo: Dict[str, int]  # {Primaria: 4, Secundaria: 3, ...}
    por_zona: Dict[str, int]   # {Urbana: 6, Rural: 0, Ambas: 2}
