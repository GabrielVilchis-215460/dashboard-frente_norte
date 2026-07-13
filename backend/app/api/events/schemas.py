from pydantic import BaseModel
from datetime import date
from typing import Optional

class OrganizacionBasica(BaseModel):
    nombre: str

    class Config:
        from_attributes = True  

class EventoResponse(BaseModel):
    id: int
    nombre: str
    ubicacion: Optional[str] = None
    fecha: date
    enfoque: Optional[str] = None
    tipo: Optional[str] = None
    url_original: Optional[str] = None
    imagen_url: Optional[str] = None
    organizacion: OrganizacionBasica  

    class Config:
        from_attributes = True