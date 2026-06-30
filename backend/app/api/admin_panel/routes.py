from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.organizacion import Organizacion
from app.models.programa import Programa
from app.api.admin_panel.schemas import (
    ProgramaBase,
    ProgramaOut,
    ProgramaCreate,
    ProgramaUpdate,
    OrganizacionBase,
    OrganizacionCreate,
    OrganizacionMapPin,
    OrganizacionOut,
    OrganizacionUpdate,
)
from app.api.auth.service import get_current_admin

# Todos los endpoints de este router requieren JWT válido
router = APIRouter(
    prefix="/panel_admin",
    tags=["Panel de Administración"],
    dependencies=[Depends(get_current_admin)],
)

@router.get("/organizaciones", response_model=List[OrganizacionOut])
def listar_organizaciones(
    tipo:      Optional[str] = Query(None),
    zona:      Optional[str] = Query(None),
    area_stem: Optional[str] = Query(None),
    activo:    Optional[bool] = Query(None, description="True=solo activas, False=solo inactivas, None=todas"),
    skip: int = 0, limit: int = 200,
    db: Session = Depends(get_db),
):
    """Lista organizaciones con filtros opcionales. Por defecto devuelve solo las activas."""
    q = db.query(Organizacion)
    if activo is not None:
        q = q.filter(Organizacion.activo == activo)
    if tipo: q = q.filter(Organizacion.tipo == tipo)
    if zona: q = q.filter(Organizacion.zona == zona)
    if area_stem: q = q.filter(Organizacion.areas_stem.any(area_stem))
    return q.order_by(Organizacion.nombre).offset(skip).limit(limit).all()

@router.get("/organizaciones/mapa", response_model=List[OrganizacionMapPin])
def pines_mapa(
    tipo:      Optional[str] = None,
    area_stem: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retorna solo los campos necesarios para renderizar pines en el mapa."""
    q = db.query(Organizacion).filter(
        Organizacion.activo == True,
        Organizacion.latitud != None,
        Organizacion.longitud != None,
    )
    if tipo:      q = q.filter(Organizacion.tipo == tipo)
    if area_stem: q = q.filter(Organizacion.areas_stem.any(area_stem))
    return q.all()

@router.get("/organizaciones/{org_id}", response_model=OrganizacionOut)
def detalle_organizacion(org_id: int, db: Session = Depends(get_db)):
    org = db.query(Organizacion).filter(Organizacion.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organización no encontrada")
    return org

@router.post("/organizaciones/create", response_model=OrganizacionOut, status_code=201)
def crear_organizacion(data: OrganizacionCreate, db: Session = Depends(get_db)):
    """Crea una organización nueva. El nombre debe ser único."""
    existente = db.query(Organizacion).filter(
        Organizacion.nombre.ilike(data.nombre)
    ).first()
    if existente:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe una organización con el nombre '{existente.nombre}' (id={existente.id})"
        )
    org = Organizacion(**data.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

@router.put("/organizaciones/{org_id}", response_model=OrganizacionOut)
def actualizar_organizacion(
    org_id: int, data: OrganizacionUpdate, db: Session = Depends(get_db)
):
    """Actualiza los campos de una organización existente (PATCH parcial)."""
    org = db.query(Organizacion).filter(Organizacion.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organización no encontrada")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(org, k, v)
    db.commit()
    db.refresh(org)
    return org

@router.patch("/organizaciones/{org_id}/toggle", response_model=OrganizacionOut)
def toggle_organizacion(org_id: int, db: Session = Depends(get_db)):
    """Activa o desactiva una organización (soft delete reversible)."""
    org = db.query(Organizacion).filter(Organizacion.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organización no encontrada")
    org.activo = not org.activo
    db.commit()
    db.refresh(org)
    return org

@router.get("/programas", response_model=List[ProgramaOut])
def listar_programas(
    organizacion_id: Optional[int]  = Query(None),
    madurez:         Optional[str]  = Query(None),
    nivel_educativo: Optional[str]  = Query(None),
    poblacion:       Optional[str]  = Query(None),
    zona:            Optional[str]  = Query(None),
    area_stem:       Optional[str]  = Query(None),
    activo:          Optional[bool] = Query(None),
    pct_mujeres_rango: Optional[str] = Query(None),
    skip: int = 0, limit: int = 200,
    db: Session = Depends(get_db),
):
    q = db.query(Programa)
    if activo is not None:
        q = q.filter(Programa.activo == activo)
    if organizacion_id: q = q.filter(Programa.organizacion_id == organizacion_id)
    if madurez: q = q.filter(Programa.madurez == madurez)
    if nivel_educativo: q = q.filter(Programa.nivel_educativo == nivel_educativo)
    if poblacion: q = q.filter(Programa.poblacion_objetivo == poblacion)
    if zona: q = q.filter(Programa.zona == zona)
    if area_stem: q = q.filter(Programa.areas_stem.any(area_stem))
    if pct_mujeres_rango: q = q.filter(Programa.pct_mujeres_rango == pct_mujeres_rango)
    return q.order_by(Programa.nombre).offset(skip).limit(limit).all()

@router.get("/programas/{prog_id}", response_model=ProgramaOut)
def detalle_programa(prog_id: int, db: Session = Depends(get_db)):
    prog = db.query(Programa).filter(Programa.id == prog_id).first()
    if not prog:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    return prog

@router.post("/programas/create", response_model=ProgramaOut, status_code=201)
def crear_programa(data: ProgramaCreate, db: Session = Depends(get_db)):
    """Crea un programa. Verifica que la organización padre exista."""
    from app.models.organizacion import Organizacion
    if not db.query(Organizacion).filter(Organizacion.id == data.organizacion_id).first():
        raise HTTPException(status_code=404, detail="Organización no encontrada")
    prog = Programa(**data.model_dump())
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return prog

@router.put("/programas/{prog_id}", response_model=ProgramaOut)
def actualizar_programa(
    prog_id: int, data: ProgramaUpdate, db: Session = Depends(get_db)
):
    """Actualiza los campos de un programa existente."""
    prog = db.query(Programa).filter(Programa.id == prog_id).first()
    if not prog:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(prog, k, v)
    db.commit()
    db.refresh(prog)
    return prog

@router.patch("/programas/{prog_id}/toggle", response_model=ProgramaOut)
def toggle_programa(prog_id: int, db: Session = Depends(get_db)):
    """Activa o desactiva un programa (soft delete reversible)."""
    prog = db.query(Programa).filter(Programa.id == prog_id).first()
    if not prog:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    prog.activo = not prog.activo
    db.commit()
    db.refresh(prog)
    return prog

