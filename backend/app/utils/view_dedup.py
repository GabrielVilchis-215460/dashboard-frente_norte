"""
Dedup simple en memoria (por proceso) para evitar que refrescar la página
o un script incremente las vistas de un evento repetidamente.
"""

import time
from threading import Lock

_VENTANA_SEGUNDOS = 12 * 60 * 60  # 12 horas
_registro: dict[tuple[str, int], float] = {}
_lock = Lock()


def ya_visto_recientemente(ip: str, evento_id: int) -> bool:
    """
    Retorna True si esta IP ya generó una vista de este evento dentro de la
    ventana de tiempo. Si retorna False, además registra la vista actual.
    """
    clave = (ip, evento_id)
    ahora = time.time()

    with _lock:
        _limpiar_expirados(ahora)
        ultima_vista = _registro.get(clave)
        if ultima_vista is not None and (ahora - ultima_vista) < _VENTANA_SEGUNDOS:
            return True
        _registro[clave] = ahora
        return False


def _limpiar_expirados(ahora: float) -> None:
    """Housekeeping simple para que el dict no crezca indefinidamente."""
    expirados = [k for k, t in _registro.items() if (ahora - t) >= _VENTANA_SEGUNDOS]
    for k in expirados:
        del _registro[k]