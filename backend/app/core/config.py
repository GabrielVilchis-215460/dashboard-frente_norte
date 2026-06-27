from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── Base de datos ──────────────────────────────────────────────────────────
    DATABASE_URL: str

    # ── Seguridad JWT ──────────────────────────────────────────────────────────
    # SECRET_KEY: mínimo 32 caracteres en producción.
    # Genera uno seguro con: openssl rand -hex 32
    SECRET_KEY: str = "dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas

    # ── Credenciales del administrador ─────────────────────────────────────────
    # ADMIN_PASSWORD_HASH: hash bcrypt de la contraseña.
    # Genera uno con: python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('tu_contraseña'))"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = ""

    # ── Supabase ───────────────────────────────────────────────────────────────
    # Requeridas para usar la API REST de Supabase (Storage, RLS, Data API, etc.)
    SUPABASE_URL: str = ""
    SUPABASE_SECRET_KEY: str = ""

    # ── Entorno y CORS ─────────────────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"


settings = Settings()
