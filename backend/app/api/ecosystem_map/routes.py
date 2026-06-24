from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.ecosystem_map.schemas import FichaActor, MapaEcosistema
from app.api.ecosystem_map.service import obtener_ficha_actor, obtener_mapa

router = APIRouter(prefix="/mapa_ecosistema", tags=["Mapa del Ecosistema"])


@router.get(
    "/",
    response_model=MapaEcosistema,
    summary="Mapa interactivo del ecosistema STEM",
    description=(
        "Retorna los pins georreferenciados de todos los actores STEM "
        "con filtros opcionales para segmentar la visualización. "
        "Filtros de organización: tipo, area_stem, zona. "
        "Filtros de programa: madurez, nivel_educativo, poblacion, pct_mujeres_rango."
    ),
)
def mapa_ecosistema(
    tipo: Optional[str] = Query(None, description="Tipo de organización"),
    area_stem: Optional[str] = Query(None, description="Área STEM"),
    zona: Optional[str] = Query(None, description="Zona geográfica"),
    madurez: Optional[str] = Query(None, description="Nivel de madurez del programa"),
    nivel_educativo: Optional[str] = Query(None, description="Nivel educativo atendido"),
    poblacion: Optional[str] = Query(None, description="Población objetivo atendida"),
    pct_mujeres_rango: Optional[str] = Query(None, description="Rango de participación femenina, ej: '51-75'"),
    solo_con_coordenadas: bool = Query(False, description="Excluir actores sin coordenadas"),
    db: Session = Depends(get_db),
):
    return obtener_mapa(db, tipo, area_stem, zona, madurez, nivel_educativo, poblacion, pct_mujeres_rango, solo_con_coordenadas)


@router.get(
    "/actor/{org_id}",
    response_model=FichaActor,
    summary="Ficha descriptiva de un actor",
    description="Retorna los datos completos de un actor para mostrarlos al hacer clic en su pin.",
)
def ficha_actor(org_id: int, db: Session = Depends(get_db)):
    ficha = obtener_ficha_actor(db, org_id)
    if not ficha:
        raise HTTPException(status_code=404, detail="Actor no encontrado.")
    return ficha
