"""
Modelo: Colonia de Ciudad Juárez
Para el módulo de Cobertura Territorial y el mapa de calor (heatmap).
El nivel_oferta se calcula dinámicamente por el servicio de métricas.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.session import Base


class Colonia(Base):
    __tablename__ = "colonias"

    id              = Column(Integer, primary_key=True, index=True)
    nombre          = Column(String(255), nullable=False, index=True)
    zona            = Column(String(50))   # Norte | Sur | Poniente | Oriente | Centro
    latitud         = Column(Float)        # centroide de la colonia
    longitud        = Column(Float)
    # nivel_oferta se calcula en runtime: Alto | Medio | Bajo | Sin oferta
