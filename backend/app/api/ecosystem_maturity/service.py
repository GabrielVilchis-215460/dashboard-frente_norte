from app.models.organizacion import Organizacion
from app.models.programa import Programa
import logging
from sqlalchemy.orm import Session
from app.api.ecosystem_maturity.schemas import MadurezEcosistema, MadurezDetalle 
from app.utils.constants import MADUREZ_ORDEN
from app.utils.helpers import mid_volume

logger = logging.getLogger("stem_api.madurez_ecosistema")

def get_madurez(db: Session) -> MadurezEcosistema:
    logger.info("Calculando madurez del ecosistema desde el modelo de organizaciones")
    programas = db.query(Programa).filter(Programa.activo == True).all()
    orgs = db.query(Organizacion).filter(Organizacion.activo == True).all()

    por_etapa: dict[str, int] = {}
    beneficiarios_etapa: dict[str, int] = {}
    for p in programas:
        etapa = p.madurez or "Sin clasificar"
        por_etapa[etapa] = por_etapa.get(etapa, 0) + 1
        vol = mid_volume(p.volumen_semestral)
        beneficiarios_etapa[etapa] = beneficiarios_etapa.get(etapa, 0) + vol

    org_madurez_count: dict[str, int] = {}
    org_madurez_lista: dict[str, list[str]] = {}
    
    for org in orgs:
        etapa_org = org.nivel_madurez if org.nivel_madurez else "Sin clasificar"
            
        org_madurez_count[etapa_org] = org_madurez_count.get(etapa_org, 0) + 1
        
        if etapa_org not in org_madurez_lista:
            org_madurez_lista[etapa_org] = []
            
        nombre_org = org.nombre if org.nombre else "Organización Desconocida"
        org_madurez_lista[etapa_org].append(nombre_org)

    lista_organizaciones_madurez = [
        MadurezDetalle(
            etapa=etapa,
            cantidad=cantidad,
            organizaciones=org_madurez_lista.get(etapa, [])
        )
        for etapa, cantidad in org_madurez_count.items()
    ]

    return MadurezEcosistema(
        por_etapa=por_etapa,
        beneficiarios_por_etapa=beneficiarios_etapa,
        organizaciones_por_madurez=lista_organizaciones_madurez 
    )