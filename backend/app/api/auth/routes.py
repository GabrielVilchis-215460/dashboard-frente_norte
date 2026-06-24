from fastapi import APIRouter, HTTPException, status

from app.api.auth.schemas import LoginRequest, TokenResponse
from app.api.auth.service import authenticate_admin
from app.core.config import settings
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión como administrador",
    description=(
        "Autentica las credenciales del administrador y retorna un JWT de acceso. "
        "El token debe enviarse en el header `Authorization: Bearer <token>` en todas "
        "las peticiones al panel de administración."
    ),
)
def login(credentials: LoginRequest):
    """
    Endpoint de autenticación. Valida usuario y contraseña, y emite un JWT.

    - **username**: nombre de usuario configurado en ADMIN_USERNAME (.env)
    - **password**: contraseña correspondiente al hash en ADMIN_PASSWORD_HASH (.env)
    """
    if not authenticate_admin(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=credentials.username)
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
    )
