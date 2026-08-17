"""
Utilidades de seguridad: hashing de contraseñas y manejo de tokens JWT.
Estas funciones son el núcleo del sistema de autenticación y no deben
ser importadas directamente desde las rutas — usar las dependencias de FastAPI
definidas en app/api/auth/service.py.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

import bcrypt as _bcrypt
from jose import jwt

from app.core.config import settings

# Blacklist en memoria de JTIs revocados (jti → tiempo de expiración).
# Se limpia automáticamente al verificar tokens para no crecer indefinidamente.
_revoked_jtis: dict[str, datetime] = {}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _bcrypt.checkpw(plain_password.encode()[:72], hashed_password.encode())


def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode()[:72], _bcrypt.gensalt()).decode()


def create_access_token(subject: str, rol: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "rol": rol, "exp": expire, "jti": str(uuid.uuid4())}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def revoke_token(token: str) -> None:
    """Agrega el jti del token a la blacklist hasta que expire."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            _revoked_jtis[jti] = datetime.fromtimestamp(exp, tz=timezone.utc)
    except Exception:
        pass


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        rol = payload.get("rol")
        jti = payload.get("jti")
        if username is None or rol is None:
            return None

        # Limpiar jtis expirados y verificar blacklist
        now = datetime.now(timezone.utc)
        expired_jtis = [j for j, exp in _revoked_jtis.items() if exp <= now]
        for j in expired_jtis:
            del _revoked_jtis[j]

        if jti and jti in _revoked_jtis:
            return None

        return {"username": username, "rol": rol, "jti": jti}
    except Exception:
        return None
