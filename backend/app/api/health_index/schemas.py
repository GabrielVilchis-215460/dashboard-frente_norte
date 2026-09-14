from pydantic import BaseModel
from typing import List, Literal, Optional

# Pestaña 8 - Modulo 8
# KPIs
class KPIIndicador(BaseModel):
    clave: str
    nombre: str
    valor_actual: float
    unidad: str
    cambio_porcentual: Optional[float] = None

# Graficas
class PuntoEvolucionAnio(BaseModel):
    anio: int
    valor: float

class SlideEvolucionIndicador(BaseModel):
    indicador_clave: str
    indicador_nombre: str
    unidad: str
    serie_historica: List[PuntoEvolucionAnio]

class ValorBenchmarkEcosistema(BaseModel):
    ecosistema: str
    rol: str
    valor: float

class SlideBenchmarkIndicador(BaseModel):
    indicador_clave: str
    indicador_nombre: str
    unidad: str
    comparativa_ecosistemas: List[ValorBenchmarkEcosistema]

# Apartado de brechas y oportunidades
class AnalisisItem(BaseModel):
    indicador_clave: str
    indicador_nombre: str
    tipo: Literal["brecha", "fortaleza"]
    valor_actual: float
    valor_referente: float
    referente: str
    diferencia: float
    mensaje: str

    class Config:
        from_attributes = True

# Responses
class EcosistemaResponse(BaseModel):
    ecosistema: str
    rol: str
    anio: int
    analisis: List[AnalisisItem]

    class Config:
        from_attributes = True

class IndiceSaludResponse(BaseModel):
    ecosistema_actual: str
    kpis: List[KPIIndicador]
    carrusel_evolucion: List[SlideEvolucionIndicador]
    carrusel_benchmark: List[SlideBenchmarkIndicador]

    class Config:
        from_attributes = True