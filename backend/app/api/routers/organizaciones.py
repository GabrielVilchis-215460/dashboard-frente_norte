from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.organizacion import Organizacion
from app.schemas.organizacion import OrganizacionCreate, OrganizacionOut, OrganizacionMapPin

router = APIRouter(prefix="/organizaciones", tags=["Organizaciones"])


@router.get("/", response_model=List[OrganizacionOut])
def listar_organizaciones(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    zona: Optional[str] = Query(None, description="Filtrar por zona"),
    area_stem: Optional[str] = Query(None, description="Filtrar por área STEM"),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
):
    """Lista organizaciones con filtros opcionales."""
    q = db.query(Organizacion).filter(Organizacion.activo == True)
    if tipo:
        q = q.filter(Organizacion.tipo == tipo)
    if zona:
        q = q.filter(Organizacion.zona == zona)
    if area_stem:
        q = q.filter(Organizacion.areas_stem.any(area_stem))
    return q.offset(skip).limit(limit).all()


@router.get("/mapa", response_model=List[OrganizacionMapPin])
def pines_mapa(
    tipo: Optional[str] = None,
    area_stem: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retorna solo los campos necesarios para renderizar pines en el mapa."""
    q = db.query(Organizacion).filter(
        Organizacion.activo == True,
        Organizacion.latitud != None,
        Organizacion.longitud != None,
    )
    if tipo:
        q = q.filter(Organizacion.tipo == tipo)
    if area_stem:
        q = q.filter(Organizacion.areas_stem.any(area_stem))
    return q.all()


@router.get("/{org_id}", response_model=OrganizacionOut)
def detalle_organizacion(org_id: int, db: Session = Depends(get_db)):
    org = db.query(Organizacion).filter(Organizacion.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organización no encontrada")
    return org


@router.post("/", response_model=OrganizacionOut, status_code=201)
def crear_organizacion(data: OrganizacionCreate, db: Session = Depends(get_db)):
    org = Organizacion(**data.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.put("/{org_id}", response_model=OrganizacionOut)
def actualizar_organizacion(org_id: int, data: OrganizacionCreate,
                             db: Session = Depends(get_db)):
    org = db.query(Organizacion).filter(Organizacion.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organización no encontrada")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(org, k, v)
    db.commit()
    db.refresh(org)
    return org
