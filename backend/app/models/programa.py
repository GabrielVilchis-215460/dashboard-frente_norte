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

    id = Column(Integer, primary_key=True, index=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    nombre  = Column(String(255), nullable=True, index=True)
    descripcion = Column(Text)

    # Áreas STEM que cubre el programa
    areas_stem = Column(ARRAY(String), default=[])

    # Tipo de actividades que ofrece (puede ser múltiple)
    tipos_actividad = Column(ARRAY(String), default=[])
    # Talleres/Cursos/Bootcamps | Eventos/Conferencias |
    # Mentorías/Programas de largo plazo | Incubación/Aceleración |
    # Investigación/Proyectos | Visualización/Divulgación

    modalidad = Column(String(50))   # Presencial | Virtual | Híbrido

    # Perfil de beneficiarios
    poblacion_objetivo  = Column(String(100))
    # Niñez (6-12) | Adolescentes (13-17) | Jóvenes | Profesionistas/Docentes/Emprendedores | Público general

    nivel_educativo = Column(String(100))
    # Preescolar | Primaria | Secundaria | Preparatoria | Superior | Público general

     # Participación femenina — rango para display, numéricos para queries
    pct_mujeres_rango = Column(String(20)) # "51-75"
    pct_mujeres_min = Column(Integer) # 51
    pct_mujeres_max = Column(Integer) # 75
    pct_mujeres_mid = Column(Float) # 63.0

    # Alcance
    zona = Column(String(50))   # Urbana | Rural | Ambas
    colonias_impacto = Column(ARRAY(String), default=[])
    volumen_semestral = Column(String(50))   # rango del CSV
    volumen_min = Column(Integer) # 51
    volumen_max = Column(Integer) # 200
    volumen_mid = Column(Integer) # 126

    # Temporalidad
    temporalidad = Column(String(100))  # Anual | Ciclos escolares | Semestral | etc.

    # Madurez (clave para el módulo 5 del dashboard)
    madurez = Column(String(50))   # Exploración | Implementación | Escalamiento

    # Casos de éxito / evidencia (campo de la encuesta)
    casos_exito = Column(Text)

    # Ruta del beneficiario (campo de ambos CSVs)
    siguiente_paso = Column(Text)

    activo = Column(Boolean, default=True)
    fuente = Column(String(100))  # rodadora_csv | encuesta_csv | manual
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relación 
    organizacion = relationship("Organizacion", back_populates="programas")
