"""
Utilidades de seguridad: hashing de contraseñas y manejo de tokens JWT.
Estas funciones son el núcleo del sistema de autenticación y no deben
ser importadas directamente desde las rutas — usar las dependencias de FastAPI
definidas en app/api/auth/service.py.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt as _bcrypt
from jose import jwt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _bcrypt.checkpw(plain_password.encode()[:72], hashed_password.encode())


def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode()[:72], _bcrypt.gensalt()).decode()


def create_access_token(subject: str, rol: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT firmado con el subject (username) y el rol del usuario.

    Args:
        subject: Identificador del usuario (username).
        rol: Rol del usuario ("admin" | "viewer"), embebido como claim.
        expires_delta: Tiempo de vida del token. Si no se proporciona,
                       usa ACCESS_TOKEN_EXPIRE_MINUTES de la configuración.

    Returns:
        Token JWT como string.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "rol": rol, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un JWT.

    Returns:
        Un dict {"username": str, "rol": str} si el token es válido,
        None si expiró o es inválido.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        rol = payload.get("rol")
        if username is None or rol is None:
            return None
        return {"username": username, "rol": rol}
    except Exception:
        return None
