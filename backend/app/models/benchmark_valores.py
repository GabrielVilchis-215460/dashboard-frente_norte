from app.db.session import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func


class BenchmarkValor(Base):
    __tablename__ = "benchmark_valores"
    __table_args__ = (
        UniqueConstraint("indicador_id", "ecosistema_id", "anio", name="uq_benchmark_valor_indicador_ecosistema_anio"),
    )
 
    id = Column(Integer, primary_key=True, index=True)
    indicador_id = Column(Integer, ForeignKey("indicadores.id"), nullable=False, index=True)
    ecosistema_id = Column(Integer, ForeignKey("ecosistemas.id"), nullable=False, index=True)
    anio = Column(Integer, nullable=False)
    valor = Column(Numeric(12, 4), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
 
    indicador = relationship("Indicador", back_populates="valores")
    ecosistema = relationship("Ecosistema", back_populates="valores")
 