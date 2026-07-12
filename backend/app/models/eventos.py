from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    ubicacion = Column(String(255), nullable=True) # esto puede cambiar a false maybe
    fecha = Column(Date, nullable=False, index=True) # para poder filtrar por los dias
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacion
    organizacion = relationship("Organizacion", back_populates="eventos")