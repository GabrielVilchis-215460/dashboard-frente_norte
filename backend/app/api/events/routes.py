import uuid
import logging
import threading
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.auth.service import get_current_admin
from app.api.events import service, etl_runner
from app.api.events.service import eliminar_evento, limpiar_inactivos, detectar_duplicados_activos
from app.api.events.schemas import (
    EventoResponse, EventoCreate, EventoUpdate, EventoMapPoint,
    MetricasEventos, EventosPublicoResponse, ETLStatusResponse,
)
from app.core.config import settings
from app.utils.view_dedup import ya_visto_recientemente

logger = logging.getLogger("stem_api.eventos")

router = APIRouter(prefix="/eventos", tags=["Eventos"])


# ── Endpoints públicos ────────────────────────────────────────────────────────

@router.get("/metricas", response_model=MetricasEventos)
def metricas_eventos(db: Session = Depends(get_db)):
    """Retorna los KPIs específicos del módulo de Eventos"""
    return service.obtener_metricas_eventos(db)


@router.get("/proximos", response_model=List[EventoResponse])
def listar_proximos(
    fecha: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD). Por defecto: hoy."),
    db: Session = Depends(get_db),
):
    return service.obtener_eventos_proximos(db, fecha or date.today())


@router.get("/historial", response_model=List[EventoResponse])
def listar_historial(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    organizacion_id: Optional[int] = Query(None),
    tipo: Optional[str] = Query(None),
    enfoque: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return service.obtener_historial_eventos(db, skip, limit, organizacion_id, tipo, enfoque)


@router.get("/mapa", response_model=List[EventoMapPoint])
def eventos_mapa(db: Session = Depends(get_db)):
    return service.obtener_eventos_mapa(db)


@router.get("/publico", response_model=EventosPublicoResponse)
def listar_publico(
    q: Optional[str] = Query(None, description="Búsqueda por nombre de evento u organización"),
    tipo: Optional[str] = Query(None),
    enfoque: Optional[str] = Query(None),
    orden: str = Query("recientes", pattern="^(recientes|populares)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total, items = service.obtener_eventos_publico(db, q, tipo, enfoque, orden, skip, limit)
    return EventosPublicoResponse(total=total, items=items)


_TRUSTED_PROXIES = {"127.0.0.1", "::1"}

def _obtener_ip_cliente(request: Request) -> str:
    client_host = request.client.host if request.client else None
    # Solo confiar en X-Forwarded-For si la conexión viene de un proxy de confianza
    if client_host in _TRUSTED_PROXIES:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
    return client_host or "unknown"


@router.get("/{evento_id}", response_model=EventoResponse)
def detalle_evento(evento_id: int, request: Request, db: Session = Depends(get_db)):
    ev = service.obtener_evento_por_id(db, evento_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
 
    ip_cliente = _obtener_ip_cliente(request)
    if not ya_visto_recientemente(ip_cliente, evento_id):
        service.incrementar_vistas(db, evento_id)
        db.refresh(ev)
 
    return ev


# ── Endpoints administrativos (requieren JWT) ─────────────────────────────────

@router.get("/admin/todos", response_model=List[EventoResponse])
def admin_listar_eventos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    solo_activos: Optional[bool] = Query(None),
    organizacion_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    return service.listar_todos_eventos_admin(db, skip, limit, solo_activos, organizacion_id)


@router.post("/admin", response_model=EventoResponse, status_code=status.HTTP_201_CREATED)
def admin_crear_evento(
    data: EventoCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    try:
        return service.crear_evento(db, data)
    except Exception as e:
        logger.error("Error al crear evento: %s", e)
        raise HTTPException(status_code=500, detail="Error al crear el evento")


@router.put("/admin/{evento_id}", response_model=EventoResponse)
def admin_actualizar_evento(
    evento_id: int,
    data: EventoUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    ev = service.actualizar_evento(db, evento_id, data)
    if not ev:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return ev


@router.patch("/admin/{evento_id}/toggle", response_model=EventoResponse)
def admin_toggle_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    ev = service.toggle_evento(db, evento_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return ev


@router.delete("/admin/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_eliminar_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    """Elimina permanentemente un evento de la BD."""
    if not eliminar_evento(db, evento_id):
        raise HTTPException(status_code=404, detail="Evento no encontrado")


@router.delete("/admin/limpiar/inactivos", status_code=status.HTTP_200_OK)
def admin_limpiar_inactivos(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    """Elimina permanentemente todos los eventos inactivos para depurar duplicados."""
    eliminados = limpiar_inactivos(db)
    return {"eliminados": eliminados}


@router.get("/admin/duplicados", status_code=status.HTTP_200_OK)
def admin_ver_duplicados(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
):
    """Detecta eventos activos con nombre similar en la misma fecha."""
    return detectar_duplicados_activos(db)


@router.post("/admin/etl/run", response_model=ETLStatusResponse, status_code=status.HTTP_202_ACCEPTED)
def admin_run_etl(_: str = Depends(get_current_admin)):
    """
    Lanza el ETL de eventos en background.
    Solo se permite un job a la vez — devuelve 409 si ya hay uno en ejecución.
    Se recomienda ejecutar una vez por semana (cada lunes).
    """
    if not etl_runner.try_start():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El ETL ya está en ejecución. Espera a que termine antes de lanzarlo de nuevo.",
        )

    hilo = threading.Thread(target=etl_runner.run_etl_background, daemon=True)
    hilo.start()
    return etl_runner.get_status()


@router.get("/admin/etl/status", response_model=ETLStatusResponse)
def admin_etl_status(_: str = Depends(get_current_admin)):
    """Devuelve el estado actual del último job ETL."""
    return etl_runner.get_status()


@router.post("/admin/upload-imagen")
async def admin_upload_imagen(
    file: UploadFile = File(...),
    _: str = Depends(get_current_admin),
):
    import os, aiofiles

    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Formato no permitido. Usa JPG, PNG o WebP.")

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="La imagen no debe superar 5 MB")

    _CONTENT_TYPE_EXT = {
        "image/jpeg": "jpg", "image/png": "png",
        "image/webp": "webp", "image/gif": "gif",
    }
    ext = _CONTENT_TYPE_EXT.get(file.content_type, "jpg")
    nombre_archivo = f"{uuid.uuid4()}.{ext}"

    # Guardar en /app/imagenes/eventos/ (volumen Docker compartido con Nginx)
    directorio = "/app/imagenes/eventos"
    os.makedirs(directorio, exist_ok=True)
    ruta_disco = os.path.join(directorio, nombre_archivo)

    try:
        async with aiofiles.open(ruta_disco, "wb") as f_out:
            await f_out.write(contents)
    except Exception as e:
        logger.error("Error al guardar imagen en disco: %s", e)
        raise HTTPException(status_code=500, detail="Error al guardar la imagen")

    # URL pública servida por Nginx en /imagenes/eventos/<archivo>
    base_url = settings.IMAGES_BASE_URL.rstrip("/")
    public_url = f"{base_url}/eventos/{nombre_archivo}"
    return {"url": public_url}