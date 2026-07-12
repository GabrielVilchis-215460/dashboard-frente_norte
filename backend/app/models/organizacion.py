"""
Modelo: Organización STEM
Fuente: Encuesta + datos complementarios de investigación

Tipos contemplados (ficha técnica PDF):
  - ONG / Asociación civil
  - Institución educativa
  - Gobierno
  - Empresa / Industria
  - Centro de investigación
  - Makerspace / Laboratorio
  - Centro comunitario
  - Incubadora / Aceleradora
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Organizacion(Base):
    __tablename__ = "organizaciones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)

    # Clasificación
    tipo = Column(String(100), nullable=True)
    # ONG / Asociación civil | Institución educativa | Gobierno |
    # Empresa / Industria | Centro de investigación |
    # Makerspace / Laboratorio | Centro comunitario | Incubadora / Aceleradora

    # Áreas STEM (array: Ciencia, Tecnología, Ingeniería, Matemáticas, Robótica, IA, Medio ambiente, Historia Natural)
    areas_stem = Column(ARRAY(String), nullable=True, default=[])

    # Enfoque principal 
    enfoque_principal = Column(String(255))
    # Educación / Capacitación técnica | Investigación / Desarrollo |
    # Articulación y políticas públicas | Incubación / Aceleración

    descripcion = Column(Text)
    logo_url = Column(String(500))
    contacto_nombre = Column(Text)
    contacto_email = Column(Text)
    contacto_telefono = Column(Text)
    sitio_web = Column(String(500))

    # Geolocalización para el mapa interactivo
    latitud = Column(Float)
    longitud = Column(Float)
    direccion = Column(String(500))

    # Cobertura territorial
    zona = Column(String(50))   # Urbana | Rural | Ambas
    colonias = Column(ARRAY(String), default=[])

    # Feed de RSS
    rss_url = Column(String(500), nullable=True)
    
    # Metadatos
    activo = Column(Boolean, default=True)
    fuente = Column(String(100))  # encuesta | investigacion_documental
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
)

    # Relación
    programas = relationship("Programa", back_populates="organizacion",cascade="all, delete-orphan")
    eventos = relationship("Evento", back_populates="organizacion", cascade="all, delete-orphan")