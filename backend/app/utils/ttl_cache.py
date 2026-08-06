"""Cache en memoria simple con TTL. Se limpia al reiniciar el proceso."""
import time
from typing import Any

_store: dict[str, tuple[Any, float]] = {}


def get(key: str, ttl: float) -> Any | None:
    entry = _store.get(key)
    if entry and (time.time() - entry[1]) < ttl:
        return entry[0]
    return None


def put(key: str, value: Any) -> None:
    _store[key] = (value, time.time())


def delete(key: str) -> None:
    _store.pop(key, None)


def clear() -> None:
    _store.clear()
