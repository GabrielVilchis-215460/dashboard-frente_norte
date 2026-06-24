from pydantic import BaseModel, Field
from typing import List, Optional


class PinMapa(BaseModel):
    """Datos mínimos para renderizar un pin en el mapa interactivo."""
    id: int
    nombre: str
    tipo: str
    areas_stem: List[str] = []
    latitud: Optional[float]
    longitud: Optional[float]
    zona: Optional[str]
    total_programas: int = Field(default=0, description="Número de programas activos")

    class Config:
        from_attributes = True


class FichaActor(BaseModel):
    """Ficha descriptiva completa de un actor, mostrada al hacer clic en su pin."""
    id: int
    nombre: str
    tipo: str
    descripcion: Optional[str]
    areas_stem: List[str] = []
    enfoque_principal: Optional[str]
    sitio_web: Optional[str]
    contacto_nombre: Optional[str]
    contacto_email: Optional[str]
    contacto_telefono: Optional[str]
    direccion: Optional[str]
    zona: Optional[str]
    colonias: List[str] = []
    latitud: Optional[float]
    longitud: Optional[float]
    total_programas: int = 0
    programas: List[str] = Field(default=[], description="Nombres de los programas activos")

    class Config:
        from_attributes = True


class MapaEcosistema(BaseModel):
    """Respuesta completa del mapa: pins de actores."""
    total_actores: int
    actores_con_coordenadas: int
    pins: List[PinMapa]
