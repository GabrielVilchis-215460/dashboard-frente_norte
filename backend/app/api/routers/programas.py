from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.programa import Programa
from app.schemas.programa import ProgramaCreate, ProgramaOut

router = APIRouter(prefix="/programas", tags=["Programas"])


@router.get("/", response_model=List[ProgramaOut])
def listar_programas(
    madurez: Optional[str] = Query(None),
    nivel_educativo: Optional[str] = Query(None),
    poblacion: Optional[str] = Query(None),
    zona: Optional[str] = Query(None),
    area_stem: Optional[str] = Query(None),
    organizacion_id: Optional[int] = Query(None),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(Programa).filter(Programa.activo == True)
    if madurez:         q = q.filter(Programa.madurez == madurez)
    if nivel_educativo: q = q.filter(Programa.nivel_educativo == nivel_educativo)
    if poblacion:       q = q.filter(Programa.poblacion_objetivo == poblacion)
    if zona:            q = q.filter(Programa.zona == zona)
    if area_stem:       q = q.filter(Programa.areas_stem.any(area_stem))
    if organizacion_id: q = q.filter(Programa.organizacion_id == organizacion_id)
    return q.offset(skip).limit(limit).all()


@router.get("/{prog_id}", response_model=ProgramaOut)
def detalle_programa(prog_id: int, db: Session = Depends(get_db)):
    prog = db.query(Programa).filter(Programa.id == prog_id).first()
    if not prog:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    return prog


@router.post("/", response_model=ProgramaOut, status_code=201)
def crear_programa(data: ProgramaCreate, db: Session = Depends(get_db)):
    prog = Programa(**data.model_dump())
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return prog
