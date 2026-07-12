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
    
class TopOrganizacion(BaseModel):
    nombre: str
    total_programas: int

class PanoramaGeneral(BaseModel):
    total_organizaciones: int
    total_programas_activos: int
    total_eventos_activos: int
    beneficiarios_semestre: int  # suma de volumen_mid de todos los programas
    colonias_impactadas: int
    pct_mujeres_beneficiarias: float
    pct_programas_enfoque_integral: float
    organizaciones_por_tipo: Dict[str, int]   # {ONG: 5, Gobierno: 1, ...}
    areas_stem_representadas: Dict[str, int]
    top_organizaciones: List[TopOrganizacion] # top 5 instituciones con mas programas (rodadora top 1)
    preview_mapa: List[MapaPreview]