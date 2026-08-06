from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    # Verifica la conexión antes de usarla — reconecta automáticamente si el servidor
    # cerró la conexión por inactividad (crítico para el ETL que puede tardar minutos).
    pool_pre_ping=True,
    # Recicla conexiones cada 30 minutos para evitar usar conexiones stale.
    pool_recycle=1800,
    # Tamaño del pool y overflow razonable para el workload actual.
    pool_size=5,
    max_overflow=10,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
