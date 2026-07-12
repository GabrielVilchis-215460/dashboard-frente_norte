from sqlalchemy.orm import Session
from datetime import date
from app.models.eventos import Evento

def obtener_eventos_proximos(db: Session, fecha_filtro: date):
    """
    Devuelve todos los eventos activos desde una fecha de inicio en adelante,
    ordenados del más cercano al más lejano.
    """
    return db.query(Evento).filter(
        Evento.fecha >= fecha_filtro,
        Evento.activo == True
    ).order_by(
        Evento.fecha.asc()
    ).all()

# Funcion auxiliar
def contar_eventos_activos(db: Session) -> int:
    """
    Cuenta cuántos eventos activos hay desde HOY en adelante.
    (No cuenta los eventos que ya pasaron).
    """
    fecha_hoy = date.today()
    return db.query(Evento).filter(
        Evento.fecha >= fecha_hoy,
        Evento.activo == True
    ).count()