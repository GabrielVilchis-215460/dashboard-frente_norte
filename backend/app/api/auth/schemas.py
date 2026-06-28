from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Nombre de usuario del administrador")
    password: str = Field(..., description="Contraseña del administrador")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token (siempre 'bearer')")
    expires_in: int = Field(..., description="Segundos hasta la expiración del token")
