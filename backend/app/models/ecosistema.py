from app.db.session import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String

class Ecosistema(Base):
    __tablename__ = "ecosistemas"
 
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    rol = Column(String(20), nullable=False) 
 
    valores = relationship("BenchmarkValor", back_populates="ecosistema", cascade="all, delete-orphan")