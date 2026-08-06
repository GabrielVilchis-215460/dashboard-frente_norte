"""
Estado y ejecución en background del ETL de eventos.

Se mantiene en memoria (dict global dentro del proceso).
Garantiza que solo un job corra a la vez — el endpoint devuelve 409 si ya hay uno activo.
"""

import threading
import logging
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger("stem_api.etl_runner")


class ETLStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Estado compartido — acceso protegido por _lock
_lock = threading.Lock()
_state: dict = {
    "status": ETLStatus.IDLE,
    "started_at": None,
    "finished_at": None,
    "tokens": 0,
    "errores": [],
    "error": None,
    "rss_no_disponible": False,
    "phase": "",
    "phase_detail": None,
    "posts_encontrados": 0,
    "posts_analizados": 0,
    "eventos_añadidos": 0,
    "nuevos_ids": [],
}


def get_status() -> dict:
    with _lock:
        return dict(_state)


def is_running() -> bool:
    with _lock:
        return _state["status"] == ETLStatus.RUNNING


def try_start() -> bool:
    """Intenta arrancar el ETL de forma atómica. Retorna False si ya está corriendo."""
    with _lock:
        if _state["status"] == ETLStatus.RUNNING:
            return False
        _state["status"] = ETLStatus.RUNNING
        _state["started_at"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
        _state["finished_at"] = None
        _state["tokens"] = 0
        _state["errores"] = []
        _state["error"] = None
        _state["rss_no_disponible"] = False
        _state["phase"] = ""
        _state["phase_detail"] = None
        _state["posts_encontrados"] = 0
        _state["posts_analizados"] = 0
        _state["eventos_añadidos"] = 0
        _state["nuevos_ids"] = []
    return True


def run_etl_background() -> None:
    """
    Ejecuta el ETL en un hilo separado.
    Llamar solo tras un try_start() exitoso — el estado ya fue marcado RUNNING.
    """
    from scripts.etl_events import run_etl

    logger.info("ETL iniciado en background.")

    def _phase_callback(phase: str, detail=None):
        with _lock:
            _state["phase"] = phase
            _state["phase_detail"] = detail

    try:
        resultado = run_etl(phase_callback=_phase_callback)

        with _lock:
            if resultado.get("ok"):
                _state["status"] = ETLStatus.COMPLETED
                _state["tokens"] = resultado.get("tokens", 0)
                _state["errores"] = resultado.get("errores", [])
                _state["rss_no_disponible"] = resultado.get("rss_no_disponible", False)
                _state["phase"] = ""
                _state["phase_detail"] = None
                _state["posts_encontrados"] = resultado.get("posts_encontrados", 0)
                _state["posts_analizados"] = resultado.get("posts_analizados", 0)
                _state["eventos_añadidos"] = resultado.get("eventos_añadidos", 0)
                _state["nuevos_ids"] = resultado.get("nuevos_ids", [])
            else:
                _state["status"] = ETLStatus.FAILED
                _state["error"] = resultado.get("error", "Error desconocido")

    except Exception as exc:
        logger.exception("ETL falló con excepción no capturada: %s", exc)
        with _lock:
            _state["status"] = ETLStatus.FAILED
            _state["error"] = str(exc)

    finally:
        with _lock:
            _state["finished_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("ETL finalizado. Estado: %s", _state["status"])
