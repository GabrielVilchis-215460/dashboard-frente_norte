from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# CRUD de programas
class ProgramaBase(BaseModel):
    nombre: str
    organizacion_id: int
    descripcion: Optional[str] = None
    areas_stem: List[str] = []
    tipos_actividad: List[str] = []
    modalidad: Optional[str] = None
    poblacion_objetivo: Optional[str] = None
    nivel_educativo: Optional[str] = None
    pct_mujeres_rango: Optional[str] = None
    pct_mujeres_mid: Optional[float] = None
    zona: Optional[str] = None
    colonias_impacto: List[str] = []
    volumen_semestral: Optional[str] = None
    volumen_mid: Optional[int] = None
    temporalidad: Optional[str] = None
    madurez: Optional[str] = None
    casos_exito: Optional[str] = None
    siguiente_paso: Optional[str] = None
    activo: bool = True
    fuente: Optional[str] = None

class ProgramaCreate(ProgramaBase):
    pass

class ProgramaUpdate(ProgramaBase):
    nombre: Optional[str] = None
    organizacion_id: Optional[int] = None

class ProgramaOut(ProgramaBase):
    id: int
    fecha_registro: Optional[datetime] = None

    class Config:
        from_attributes = True

# CRUD de organizaciones/instituciones
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