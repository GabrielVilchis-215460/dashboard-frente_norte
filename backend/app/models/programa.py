"""
Modelo: Programa STEM
Fuente: CSV Rodadora (13 programas) + CSV Encuesta (8 orgs con sus programas)

Columnas derivadas de ambos CSVs más la ficha técnica del PDF:
  - Tipos de actividad: Talleres/Cursos/Bootcamps, Eventos/Conferencias,
    Mentorías/Programas de largo plazo, Incubación/Aceleración,
    Investigación/Proyectos, Visualización/Divulgación
  - Madurez: Exploración | Implementación | Escalamiento
  - Población: Niñez (6-12) | Adolescentes (13-17) | Jóvenes |
               Profesionistas/Docentes/Emprendedores | Público general
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Programa(Base):
    __tablename__ = "programas"

    id                  = Column(Integer, primary_key=True, index=True)
    organizacion_id     = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    nombre              = Column(String(255), nullable=False, index=True)
    descripcion         = Column(Text)

    # Áreas STEM que cubre el programa
    areas_stem          = Column(ARRAY(String), default=[])

    # Tipo de actividades que ofrece (puede ser múltiple)
    tipos_actividad     = Column(ARRAY(String), default=[])
    # Talleres/Cursos/Bootcamps | Eventos/Conferencias |
    # Mentorías/Programas de largo plazo | Incubación/Aceleración |
    # Investigación/Proyectos | Visualización/Divulgación

    modalidad           = Column(String(50))   # Presencial | Virtual | Híbrido

    # Perfil de beneficiarios
    poblacion_objetivo  = Column(String(100))
    # Niñez (6-12) | Adolescentes (13-17) | Jóvenes |
    # Profesionistas/Docentes/Emprendedores | Público general

    nivel_educativo     = Column(String(100))
    # Preescolar | Primaria | Secundaria | Preparatoria |
    # Superior | Público general

    # Participación femenina (rango del CSV)
    pct_mujeres_rango   = Column(String(20))   # 0-25 | 26-50 | 51-75 | 76-100
    pct_mujeres_mid     = Column(Float)        # valor medio calculado (12.5, 37.5, 62.5, 88)

    # Alcance
    zona                = Column(String(50))   # Urbana | Rural | Ambas
    colonias_impacto    = Column(ARRAY(String), default=[])
    volumen_semestral   = Column(String(50))   # rango del CSV
    volumen_mid         = Column(Integer)      # valor medio para cálculos

    # Temporalidad
    temporalidad        = Column(String(100))  # Anual | Ciclos escolares | Semestral | etc.

    # Madurez (clave para el módulo 5 del dashboard)
    madurez             = Column(String(50))   # Exploración | Implementación | Escalamiento

    # Casos de éxito / evidencia (campo de la encuesta)
    casos_exito         = Column(Text)

    # Ruta del beneficiario (campo de ambos CSVs)
    siguiente_paso      = Column(Text)

    activo              = Column(Boolean, default=True)
    fuente              = Column(String(100))  # rodadora_csv | encuesta_csv | manual
    fecha_registro      = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación inversa
    organizacion        = relationship("Organizacion", back_populates="programas")
