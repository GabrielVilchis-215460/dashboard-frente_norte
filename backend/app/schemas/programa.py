from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


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
