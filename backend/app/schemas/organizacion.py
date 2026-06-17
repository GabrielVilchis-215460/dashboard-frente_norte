from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class OrganizacionBase(BaseModel):
    nombre: str
    tipo: str
    areas_stem: List[str] = []
    enfoque_principal: Optional[str] = None
    descripcion: Optional[str] = None
    logo_url: Optional[str] = None
    contacto: Optional[str] = None
    sitio_web: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    direccion: Optional[str] = None
    zona: Optional[str] = None
    colonias: List[str] = []
    activo: bool = True
    fuente: Optional[str] = None


class OrganizacionCreate(OrganizacionBase):
    pass


class OrganizacionUpdate(OrganizacionBase):
    nombre: Optional[str] = None
    tipo: Optional[str] = None


class OrganizacionOut(OrganizacionBase):
    id: int
    fecha_registro: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizacionMapPin(BaseModel):
    """Schema ligero solo para el mapa — evita cargar todos los campos"""
    id: int
    nombre: str
    tipo: str
    areas_stem: List[str]
    latitud: Optional[float]
    longitud: Optional[float]
    zona: Optional[str]

    class Config:
        from_attributes = True
