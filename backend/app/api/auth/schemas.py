from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Nombre de usuario")
    password: str = Field(..., description="Contraseña")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token (siempre 'bearer')")
    expires_in: int = Field(..., description="Segundos hasta la expiración del token")
    rol: str = Field(..., description="Rol del usuario autenticado: 'admin' | 'viewer'")
