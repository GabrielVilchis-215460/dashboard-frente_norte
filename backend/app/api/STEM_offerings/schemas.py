from pydantic import BaseModel
from typing import List, Dict, Optional

# Pestaña 4 - Modulo 4
class ModalidadProgramas(BaseModel):
    name: str # Nombre de la modalidad (ej. "Presencial")
    value: int # Cantidad de programas (ej. 15)

class OrganizacionProgramas(BaseModel):
    organizacion: str
    programas: List[str]

class OfertaSTEM(BaseModel):
    programas_por_area: Dict[str, int] # {Robótica: 5, IA: 3, ...}
    tipos_actividad_ofrecidos: Dict[str, int]  # {Talleres: 7, Mentorías: 3, ...}
    #organizaciones_por_especialidad: Dict[str, int]
    organizaciones_con_programas: List[OrganizacionProgramas]
    modalidades_programas: List[ModalidadProgramas]