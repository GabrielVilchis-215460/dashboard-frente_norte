from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # -- Base de datos --
    DATABASE_URL: str = ""
    POSTGRES_USER: str = "root"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "stem_db"

    # ── Seguridad JWT ──────────────────────────────────────────────────────────
    # SECRET_KEY: mínimo 32 caracteres en producción.
    # Genera uno seguro con: openssl rand -hex 32
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hora

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

    # Google Gemini API (opcional en desarrollo, requerida para ETL de eventos RSS)
    GEMINI_API_KEY: str = ""
    NIM_BASE_URL: str = ""
    NVIDIA_API_KEY: str = ""

    # ETL de eventos: URL del bundle RSS unificado de RSS.app
    # Si no se configura, el ETL usará el archivo local de respaldo.
    ETL_BUNDLE_URL: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
