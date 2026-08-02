"""
Servicio de autenticación y dependencias de FastAPI para proteger rutas.

- `get_current_user`: valida el JWT y devuelve (username, rol).
- `get_current_admin`: exige rol == "admin".
- `get_current_viewer_or_admin`: acepta cualquier rol autenticado (viewer o
  admin).
"""
from typing import Tuple
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session
from app.core.security import decode_access_token, verify_password

from app.db.session import get_db
from app.models.usuario import Usuario
# HTTPBearer extrae automáticamente el token del header Authorization: Bearer <token>
# y lo expone como un campo "Authorize" limpio en Swagger UI
bearer_scheme = HTTPBearer()


def authenticate_user(db: Session, username: str, password: str) -> Usuario | None:
    """
    Valida credenciales contra la tabla `usuarios`.

    Returns:
        La instancia de Usuario si las credenciales son correctas y el
        usuario está activo, None en caso contrario.
    """
    usuario = db.query(Usuario).filter(Usuario.username == username).first()
    if not usuario or not usuario.activo:
        return None
    if not verify_password(password, usuario.password_hash):
        return None
    return usuario


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Tuple[str, str]:
    """
    Dependencia base de FastAPI: valida el JWT en el header Authorization.

    Returns:
        Tupla (username, rol) del usuario autenticado.

    Raises:
        HTTPException 401 si el token es inválido o ha expirado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado. Por favor inicia sesión nuevamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception
    return payload["username"], payload["rol"]


def get_current_admin(user: Tuple[str, str] = Depends(get_current_user)) -> str:
    """
    Dependencia de FastAPI que exige rol == "admin".

    Inyectar en cualquier endpoint del panel admin / CRUD:
        @router.get("/ruta", dependencies=[Depends(get_current_admin)])

    Returns:
        El username del administrador autenticado.

    Raises:
        HTTPException 403 si el usuario autenticado no es admin.
    """
    username, rol = user
    if rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes para esta acción.",
        )
    return username


def get_current_viewer_or_admin(user: Tuple[str, str] = Depends(get_current_user)) -> str:
    """
    Dependencia de FastAPI que acepta cualquier rol autenticado (viewer o admin).

    Inyectar en los endpoints de solo-lectura del dashboard:
        @router.get("/ruta", dependencies=[Depends(get_current_viewer_or_admin)])

    Returns:
        El username del usuario autenticado.
    """
    username, _rol = user
    return username
