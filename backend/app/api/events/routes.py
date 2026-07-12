from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.session import get_db
from app.api.events.service import obtener_eventos_proximos
from app.api.events.schemas import EventoResponse
import logging

logger = logging.getLogger("stem_api.eventos")

router = APIRouter(prefix="/eventos", tags=["Eventos"])

@router.get("/proximos", response_model=List[EventoResponse])
def listar_eventos_proximos(
    fecha: Optional[date] = Query(None, description="Fecha a partir de la cual buscar (YYYY-MM-DD). Si se omite, busca desde hoy en adelante."),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de todos los próximos eventos. 
    Si no se envía fecha, automáticamente lista todos los eventos desde HOY hacia el futuro.
    """
    if not fecha:
        fecha = date.today()

    eventos = obtener_eventos_proximos(db, fecha)
    return eventos