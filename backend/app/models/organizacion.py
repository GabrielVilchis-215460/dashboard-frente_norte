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

    id            = Column(Integer, primary_key=True, index=True)
    nombre        = Column(String(255), nullable=False, index=True)

    # Clasificación (tipo contemplado en el PDF y la encuesta)
    tipo          = Column(String(100), nullable=False)
    # ONG / Asociación civil | Institución educativa | Gobierno |
    # Empresa / Industria | Centro de investigación |
    # Makerspace / Laboratorio | Centro comunitario | Incubadora / Aceleradora

    # Áreas STEM (array: Ciencia, Tecnología, Ingeniería, Matemáticas,
    #             Robótica, IA, Medio ambiente, Historia Natural)
    areas_stem    = Column(ARRAY(String), nullable=False, default=[])

    # Enfoque principal (de la encuesta)
    enfoque_principal = Column(String(255))
    # Educación / Capacitación técnica | Investigación / Desarrollo |
    # Articulación y políticas públicas | Incubación / Aceleración

    descripcion   = Column(Text)
    logo_url      = Column(String(500))
    contacto      = Column(String(255))  # nombre + email + tel de la encuesta
    sitio_web     = Column(String(500))

    # Geolocalización (para el mapa interactivo)
    latitud       = Column(Float)
    longitud      = Column(Float)
    direccion     = Column(String(500))

    # Cobertura territorial
    zona          = Column(String(50))   # Urbana | Rural | Ambas
    colonias      = Column(ARRAY(String), default=[])

    # Metadatos
    activo        = Column(Boolean, default=True)
    fuente        = Column(String(100))  # encuesta | investigacion_documental
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación
    programas     = relationship("Programa", back_populates="organizacion",
                                  cascade="all, delete-orphan")
