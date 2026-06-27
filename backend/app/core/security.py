"""
Utilidades de seguridad: hashing de contraseñas y manejo de tokens JWT.
Estas funciones son el núcleo del sistema de autenticación y no deben
ser importadas directamente desde las rutas — usar las dependencias de FastAPI
definidas en app/api/auth/service.py.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Contexto de hashing — bcrypt es el estándar recomendado para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña en texto plano contra su hash bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Genera el hash bcrypt de una contraseña. Usar solo en scripts de setup."""
    return pwd_context.hash(password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT firmado con el subject dado.

    Args:
        subject: Identificador del usuario (username).
        expires_delta: Tiempo de vida del token. Si no se proporciona,
                       usa ACCESS_TOKEN_EXPIRE_MINUTES de la configuración.

    Returns:
        Token JWT como string.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """
    Decodifica y valida un JWT.

    Returns:
        El subject (username) si el token es válido, None si expiró o es inválido.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None
