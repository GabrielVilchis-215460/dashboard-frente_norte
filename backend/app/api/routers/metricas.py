from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.metricas import (
    PanoramaGeneral, PerfilBeneficiarios, InclusionFemenina,
    OfertaSTEM, MadurezEcosistema, CoberturaTerritorial, IndiceSaludEcosistema,
)
from app.services import metricas_service as svc

router = APIRouter(prefix="/metricas", tags=["Métricas del Dashboard"])


@router.get("/panorama", response_model=PanoramaGeneral)
def panorama(db: Session = Depends(get_db)):
    """Módulo 1 — KPIs generales del ecosistema."""
    return svc.get_panorama(db)


@router.get("/beneficiarios", response_model=PerfilBeneficiarios)
def perfil_beneficiarios(db: Session = Depends(get_db)):
    """Módulo 2 — Perfil de beneficiarios."""
    return svc.get_perfil_beneficiarios(db)


@router.get("/inclusion", response_model=InclusionFemenina)
def inclusion_femenina(db: Session = Depends(get_db)):
    """Módulo 3 — Inclusión y participación femenina."""
    return svc.get_inclusion_femenina(db)


@router.get("/oferta", response_model=OfertaSTEM)
def oferta_stem(db: Session = Depends(get_db)):
    """Módulo 4 — Oferta STEM del ecosistema."""
    return svc.get_oferta_stem(db)


@router.get("/madurez", response_model=MadurezEcosistema)
def madurez(db: Session = Depends(get_db)):
    """Módulo 5 — Madurez de programas."""
    return svc.get_madurez(db)


@router.get("/cobertura", response_model=CoberturaTerritorial)
def cobertura(db: Session = Depends(get_db)):
    """Módulo 6 — Cobertura territorial."""
    return svc.get_cobertura(db)


@router.get("/indice-salud", response_model=IndiceSaludEcosistema)
def indice_salud(db: Session = Depends(get_db)):
    """Indicador estratégico — Índice de Salud del Ecosistema STEM."""
    return svc.get_indice_salud(db)
