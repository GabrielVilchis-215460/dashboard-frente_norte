from app.db.session import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String


class Indicador(Base):
    __tablename__ = "indicadores"
 
    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(50), unique=True, nullable=False, index=True)  
    nombre = Column(String(200), nullable=False)
    unidad = Column(String(30), nullable=False)  
 
    valores = relationship("BenchmarkValor", back_populates="indicador", cascade="all, delete-orphan")