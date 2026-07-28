from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date, time
from typing import Optional, List

class DistribucionItem(BaseModel):
    label: str
    count: int
    porcentaje: float

class HistoricoTrimestralItem(BaseModel):
    trimestre: str
    eventos: int

class MetricasEventos(BaseModel):
    total_eventos_activos: int
    organizaciones_con_eventos_activos: int
    distribucion_eventos_enfoque: List[DistribucionItem]
    distribucion_eventos_tipo: List[DistribucionItem]
    historico_eventos_trimestral: List[HistoricoTrimestralItem]

class OrganizacionBasica(BaseModel):
    id: int
    nombre: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    logo_url: Optional[str] = None

    # Actualización a Pydantic V2
    model_config = ConfigDict(from_attributes=True)


class EventoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None
    fecha: date
    fecha_fin: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    enfoque: Optional[str] = None
    tipo: Optional[str] = None
    imagen_url: Optional[str] = None
    url_original: Optional[str] = None
    activo: bool
    organizacion: Optional[OrganizacionBasica] = None

    # Actualización a Pydantic V2
    model_config = ConfigDict(from_attributes=True)


class EventoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None
    fecha: date
    fecha_fin: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    enfoque: Optional[str] = None
    tipo: Optional[str] = None
    imagen_url: Optional[str] = None
    url_original: Optional[str] = None
    organizacion_id: Optional[int] = None

    @field_validator('fecha_fin')
    @classmethod
    def fecha_fin_after_fecha(cls, v, info):
        if v is not None and 'fecha' in info.data and info.data['fecha'] is not None:
            if v < info.data['fecha']:
                raise ValueError('fecha_fin debe ser igual o posterior a fecha')
        return v


class EventoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None
    fecha: Optional[date] = None
    fecha_fin: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    enfoque: Optional[str] = None
    tipo: Optional[str] = None
    imagen_url: Optional[str] = None
    url_original: Optional[str] = None
    organizacion_id: Optional[int] = None


class EventoMapPoint(BaseModel):
    organizacion_id: int
    organizacion_nombre: str
    latitud: float
    longitud: float
    total_eventos: int
    eventos: List[EventoResponse]