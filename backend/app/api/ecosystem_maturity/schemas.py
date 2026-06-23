from pydantic import BaseModel
from typing import List, Dict, Optional

# Pestaña 5 - Modulo 5
class MadurezEcosistema(BaseModel):
    por_etapa: Dict[str, int] # {Exploración: 1, Implementación: 4, Escalamiento: 5}
    beneficiarios_por_etapa: Dict[str, int]
    organizaciones_por_madurez: Dict[str, int]
