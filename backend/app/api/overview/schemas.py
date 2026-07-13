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

class DistribucionItem(BaseModel):
    label: str
    count: int
    porcentaje: float

class HistoricoTrimestralItem(BaseModel):
    trimestre: str
    eventos: int

class PanoramaGeneral(BaseModel):
    total_organizaciones: int
    total_programas_activos: int
    total_eventos_activos: int
    organizaciones_con_eventos_activos: int
    beneficiarios_semestre: int  # suma de volumen_mid de todos los programas
    colonias_impactadas: int
    pct_mujeres_beneficiarias: float
    pct_programas_enfoque_integral: float
    organizaciones_por_tipo: Dict[str, int]   # {ONG: 5, Gobierno: 1, ...}
    areas_stem_representadas: Dict[str, int]
    distribucion_eventos_enfoque: List[DistribucionItem] # Para gráfica de pastel
    distribucion_eventos_tipo: List[DistribucionItem]    # Para gráfica de pastel
    historico_eventos_trimestral: List[HistoricoTrimestralItem] # Para gráfica de línea
    top_organizaciones: List[TopOrganizacion] # top 5 instituciones con mas programas (rodadora top 1)
    preview_mapa: List[MapaPreview]