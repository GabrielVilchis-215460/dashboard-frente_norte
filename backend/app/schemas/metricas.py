"""
Schemas de respuesta para los endpoints de métricas y el Índice de Salud.
Cada campo corresponde a un KPI o visualización del dashboard (PDF pág. 3-7).
"""
from pydantic import BaseModel
from typing import List, Dict, Optional


# ── Panorama General (módulo 1) ───────────────────────────────
class PanoramaGeneral(BaseModel):
    total_organizaciones: int
    total_programas_activos: int
    beneficiarios_semestre: int          # suma de volumen_mid de todos los programas
    colonias_impactadas: int
    organizaciones_por_tipo: Dict[str, int]   # {ONG: 5, Gobierno: 1, ...}
    areas_stem_representadas: List[str]


# ── Perfil de Beneficiarios (módulo 2) ────────────────────────
class PerfilBeneficiarios(BaseModel):
    por_grupo_etario: Dict[str, int]     # {Niñez: 3, Adolescentes: 2, ...}
    por_nivel_educativo: Dict[str, int]  # {Primaria: 4, Secundaria: 3, ...}
    por_zona: Dict[str, int]             # {Urbana: 6, Rural: 0, Ambas: 2}


# ── Inclusión y Participación Femenina (módulo 3) ─────────────
class InclusionFemenina(BaseModel):
    pct_promedio_mujeres: float          # promedio de pct_mujeres_mid
    programas_enfocados_mujeres: int     # programas con pct > 75%
    programas_ninas_adolescentes: int    # población objetivo = niñez o adolescentes
    por_nivel_educativo: Dict[str, float]


# ── Oferta STEM (módulo 4) ────────────────────────────────────
class OfertaSTEM(BaseModel):
    programas_por_area: Dict[str, int]      # {Robótica: 5, IA: 3, ...}
    tipos_actividad_ofrecidos: Dict[str, int]  # {Talleres: 7, Mentorías: 3, ...}
    organizaciones_por_especialidad: Dict[str, int]


# ── Madurez (módulo 5) ────────────────────────────────────────
class MadurezEcosistema(BaseModel):
    por_etapa: Dict[str, int]            # {Exploración: 1, Implementación: 4, Escalamiento: 5}
    beneficiarios_por_etapa: Dict[str, int]
    organizaciones_por_madurez: Dict[str, int]


# ── Cobertura Territorial (módulo 6) ─────────────────────────
class CoberturaColonia(BaseModel):
    nombre: str
    zona: Optional[str]
    latitud: Optional[float]
    longitud: Optional[float]
    num_programas: int
    nivel_oferta: str                    # Alto | Medio | Bajo | Sin oferta


class CoberturaTerritorial(BaseModel):
    total_colonias_impactadas: int
    por_zona: Dict[str, int]
    colonias_detalle: List[CoberturaColonia]
    zonas_baja_oferta: List[str]


# ── Índice de Salud del Ecosistema STEM (indicador estratégico) ──
class DimensionISE(BaseModel):
    nombre: str
    score: float          # 0-100
    peso: float           # peso en la fórmula
    descripcion: str


class IndiceSaludEcosistema(BaseModel):
    score_global: float                  # 0-100
    nivel: str                           # Crítico | En desarrollo | Bueno | Excelente
    dimensiones: List[DimensionISE]
    # Cobertura * 0.25 + Diversidad * 0.20 + Inclusión * 0.20
    # + Alcance * 0.20 + Madurez * 0.15
