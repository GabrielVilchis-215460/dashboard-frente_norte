from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.api.auth.schemas import LoginRequest, TokenResponse
from app.api.auth.service import authenticate_user
from app.core.config import settings
from app.core.security import create_access_token, revoke_token
from app.core.limiter import limiter
from app.db.session import get_db

_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description=(
        "Autentica las credenciales del usuario y retorna un JWT de acceso. "
        "El token debe enviarse en el header `Authorization: Bearer <token>` en todas "
        "las peticiones protegidas. El token incluye el rol del usuario ('admin' o "
        "'viewer'), que determina el nivel de acceso. "
        "Limitado a **5 intentos por minuto** por IP para prevenir fuerza bruta."
    ),
)
@limiter.limit("5/minute")
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint de autenticación. Valida usuario y contraseña contra la tabla
    `usuarios`, y emite un JWT que incluye el rol del usuario.
    """
    usuario = authenticate_user(db, credentials.username, credentials.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=usuario.username, rol=usuario.rol)
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        rol=usuario.rol,
    )


@router.post("/logout", summary="Cerrar sesión", status_code=status.HTTP_204_NO_CONTENT)
def logout(credentials: HTTPAuthorizationCredentials = Depends(_bearer)):
    """Invalida el token JWT actual antes de que expire."""
    if credentials:
        revoke_token(credentials.credentials)

