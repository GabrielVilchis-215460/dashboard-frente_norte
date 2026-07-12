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
    url_original: Optional[str] = None
    organizacion: OrganizacionBasica  

    class Config:
        from_attributes = True