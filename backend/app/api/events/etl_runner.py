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
}


def get_status() -> dict:
    with _lock:
        return dict(_state)


def is_running() -> bool:
    with _lock:
        return _state["status"] == ETLStatus.RUNNING


def run_etl_background() -> None:
    """
    Ejecuta el ETL en un hilo separado.
    Actualiza _state durante y después de la ejecución.
    Llama a esta función SOLO si is_running() devuelve False.
    """
    # Importación diferida para evitar import circular al arrancar la app
    from scripts.etl_events import run_etl

    with _lock:
        _state["status"] = ETLStatus.RUNNING
        _state["started_at"] = datetime.now(timezone.utc).isoformat()
        _state["finished_at"] = None
        _state["tokens"] = 0
        _state["errores"] = []
        _state["error"] = None
        _state["rss_no_disponible"] = False

    logger.info("ETL iniciado en background.")

    try:
        resultado = run_etl()

        with _lock:
            if resultado.get("ok"):
                _state["status"] = ETLStatus.COMPLETED
                _state["tokens"] = resultado.get("tokens", 0)
                _state["errores"] = resultado.get("errores", [])
                _state["rss_no_disponible"] = resultado.get("rss_no_disponible", False)
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
