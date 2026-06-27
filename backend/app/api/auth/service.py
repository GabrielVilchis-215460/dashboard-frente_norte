"""
Servicio de autenticación y dependencia de FastAPI para proteger rutas.

La dependencia `get_current_admin` debe usarse en cualquier endpoint que
requiera acceso autenticado. Extrae y valida el JWT del header Authorization.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.security import decode_access_token, verify_password

# HTTPBearer extrae automáticamente el token del header Authorization: Bearer <token>
# y lo expone como un campo "Authorize" limpio en Swagger UI
bearer_scheme = HTTPBearer()


def authenticate_admin(username: str, password: str) -> bool:
    """
    Valida credenciales contra los valores configurados en .env.

    Returns:
        True si username y password son correctos, False en caso contrario.

    Raises:
        HTTPException 503 si ADMIN_PASSWORD_HASH no está configurado en producción.
    """
    if not settings.ADMIN_PASSWORD_HASH:
        if settings.ENVIRONMENT == "production":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El sistema de autenticación no está configurado correctamente.",
            )
        # En desarrollo, permite login sin hash para facilitar el setup inicial
        return username == settings.ADMIN_USERNAME and password == "dev-password"

    if username != settings.ADMIN_USERNAME:
        return False

    return verify_password(password, settings.ADMIN_PASSWORD_HASH)


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """
    Dependencia de FastAPI que valida el JWT en el header Authorization.

    Inyectar esta dependencia en cualquier endpoint del panel admin:
        @router.get("/ruta", dependencies=[Depends(get_current_admin)])

    Returns:
        El username del administrador autenticado.

    Raises:
        HTTPException 401 si el token es inválido o ha expirado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado. Por favor inicia sesión nuevamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = decode_access_token(credentials.credentials)
    if username is None:
        raise credentials_exception

    return username
