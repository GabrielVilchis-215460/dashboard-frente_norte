from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ── Programas ─────────────────────────────────────────────────────────────────

class ProgramaBase(BaseModel):
    nombre: Optional[str] = None
    organizacion_id: int
    descripcion: Optional[str] = None
    areas_stem: List[str] = []
    tipos_actividad: List[str] = []
    modalidad: Optional[str] = None
    poblacion_objetivo: Optional[str] = None
    nivel_educativo: Optional[str] = None
    pct_mujeres_rango: Optional[str] = None
    pct_mujeres_min: Optional[int] = None
    pct_mujeres_max: Optional[int] = None
    pct_mujeres_mid: Optional[float] = None
    zona: Optional[str] = None
    colonias_impacto: List[str] = []
    volumen_semestral: Optional[str] = None
    volumen_min: Optional[int] = None
    volumen_max: Optional[int] = None
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
    organizacion_id: Optional[int] = None


class ProgramaOut(ProgramaBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Organizaciones ────────────────────────────────────────────────────────────

class OrganizacionBase(BaseModel):
    nombre: str
    tipo: Optional[str] = None
    areas_stem: Optional[List[str]] = []
    enfoque_principal: Optional[str] = None
    descripcion: Optional[str] = None
    logo_url: Optional[str] = None
    contacto_nombre: Optional[str] = None
    contacto_email: Optional[str] = None
    contacto_telefono: Optional[str] = None
    sitio_web: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    direccion: Optional[str] = None
    zona: Optional[str] = None
    colonias: Optional[List[str]] = []
    activo: Optional[bool] = True
    fuente: Optional[str] = None


class OrganizacionCreate(OrganizacionBase):
    pass


class OrganizacionUpdate(OrganizacionBase):
    nombre: Optional[str] = None
    tipo: Optional[str] = None


class OrganizacionOut(OrganizacionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizacionMapPin(BaseModel):
    """Schema ligero solo para el mapa — evita cargar todos los campos."""
    id: int
    nombre: str
    tipo: Optional[str]
    areas_stem: List[str] = []
    latitud: Optional[float]
    longitud: Optional[float]
    zona: Optional[str]

    class Config:
        from_attributes = True
