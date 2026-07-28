from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    ubicacion = Column(String(255), nullable=True)

    # Fecha única o rango (multi-día)
    fecha = Column(Date, nullable=False, index=True)
    fecha_fin = Column(Date, nullable=True)       # None = evento de un solo día

    # Horario (opcional)
    hora_inicio = Column(Time, nullable=True)
    hora_fin = Column(Time, nullable=True)

    # Clasificación
    enfoque = Column(String(100), nullable=True)
    tipo = Column(String(100), nullable=True)

    # Media y enlace
    imagen_url = Column(Text, nullable=True)
    url_original = Column(Text, nullable=True)

    # Relación con organización
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=True)

    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organizacion = relationship("Organizacion", back_populates="eventos")
