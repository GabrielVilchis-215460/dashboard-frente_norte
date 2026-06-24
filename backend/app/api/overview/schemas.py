from pydantic import BaseModel
from typing import List, Dict, Optional

# Pestaña 1 - Modulo 1
# Para el preview del mapa
class MapaPreview(BaseModel):
    id: int
    nombre: str
    latitud: float
    longitud: float
    logo_url: Optional[str] = None
    total_programas: int
    
class PanoramaGeneral(BaseModel):
    total_organizaciones: int
    total_programas_activos: int
    beneficiarios_semestre: int  # suma de volumen_mid de todos los programas
    colonias_impactadas: int
    organizaciones_por_tipo: Dict[str, int]   # {ONG: 5, Gobierno: 1, ...}
    areas_stem_representadas: List[str]
    top_organizaciones: List[str] # top 5 instituciones con mas programas (rodadora top 1)
    preview_mapa: List[MapaPreview]