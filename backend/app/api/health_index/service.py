import logging
from app.api.health_index.schemas import IndiceSaludEcosistema, DimensionISE
from sqlalchemy.orm import Session
from app.utils.constants import (
    TOTAL_COLONIAS_JUAREZ,
    TOTAL_AREAS_STEM,
    META_BENEFICIARIOS_SEMESTRE,
    ISE_PESOS
)
from app.utils.helpers import ise_level
from app.api.woman_inclusion.service import get_inclusion_femenina
from app.api.overview.service import get_panorama
from app.api.ecosystem_maturity.service import get_madurez

logger = logging.getLogger("stem_api.indice_salud")

def get_indice_salud(db: Session) -> IndiceSaludEcosistema:
    """
    Calcula el Índice de Salud del Ecosistema STEM (ISE).

    Fórmula:
        ISE = Cobertura×0.25 + Diversidad×0.20 + Inclusión×0.20
              + Alcance×0.20 + Madurez×0.15

    Cada dimensión se normaliza a escala 0-100 antes de aplicar los pesos.

    Args:
        db: Sesión activa de SQLAlchemy.

    Returns:
        IndiceSaludEcosistema: Score global, nivel cualitativo y 5 dimensiones.
    """
    logger.info("Calculando Índice de Salud del Ecosistema STEM")

    # Reutilizar cálculos de otros módulos
    panorama = get_panorama(db)
    inclusion = get_inclusion_femenina(db)
    madurez_d = get_madurez(db)

    # Dimensión 1: Cobertura territorial 
    # Colonias impactadas como porcentaje del total de colonias de Cd. Juárez
    d_cobertura = min(100.0, (panorama.colonias_impactadas / TOTAL_COLONIAS_JUAREZ) * 100)

    # Dimensión 2: Diversidad de oferta STEM 
    # Áreas STEM cubiertas como porcentaje de las 8 áreas posibles
    d_diversidad = min(100.0, (len(panorama.areas_stem_representadas) / TOTAL_AREAS_STEM) * 100)

    # Dimensión 3: Inclusión femenina 
    # Porcentaje promedio de mujeres en los programas (ya está en escala 0-100)
    d_inclusion = min(100.0, inclusion.pct_promedio_mujeres)

    # Dimensión 4: Alcance de beneficiarios 
    # Beneficiarios semestral como porcentaje de la meta
    d_alcance = min(100.0, (panorama.beneficiarios_semestre / META_BENEFICIARIOS_SEMESTRE) * 100)

    # Dimensión 5: Madurez de programas
    # Ponderación: Escalamiento=1.0, Implementación=0.5, Exploración=0.0
    total_prog = sum(madurez_d.por_etapa.values()) or 1
    escala = madurez_d.por_etapa.get("Escalamiento", 0)
    impleme = madurez_d.por_etapa.get("Implementación", 0)
    d_madurez = min(100.0, ((escala * 1.0 + impleme * 0.5) / total_prog) * 100)

    # Score global ponderado
    score = (
        d_cobertura  * ISE_PESOS["cobertura"]  +
        d_diversidad * ISE_PESOS["diversidad"] +
        d_inclusion  * ISE_PESOS["inclusion"]  +
        d_alcance    * ISE_PESOS["alcance"]    +
        d_madurez    * ISE_PESOS["madurez"]
    )

    nivel = ise_level(score)
    logger.info("ISE score: %.1f — nivel: %s", score, nivel)

    return IndiceSaludEcosistema(
        score_global=round(score, 1),
        nivel=nivel,
        dimensiones=[
            DimensionISE(
                nombre="Cobertura territorial",
                score=round(d_cobertura, 1),
                peso=ISE_PESOS["cobertura"],
                descripcion=f"Colonias impactadas vs. {TOTAL_COLONIAS_JUAREZ} en Cd. Juárez",
            ),
            DimensionISE(
                nombre="Diversidad de oferta STEM",
                score=round(d_diversidad, 1),
                peso=ISE_PESOS["diversidad"],
                descripcion=f"Áreas STEM cubiertas de {TOTAL_AREAS_STEM} posibles",
            ),
            DimensionISE(
                nombre="Inclusión femenina",
                score=round(d_inclusion, 1),
                peso=ISE_PESOS["inclusion"],
                descripcion="Promedio de participación de mujeres en los programas",
            ),
            DimensionISE(
                nombre="Alcance de beneficiarios",
                score=round(d_alcance, 1),
                peso=ISE_PESOS["alcance"],
                descripcion=f"Beneficiarios semestre vs. meta de {META_BENEFICIARIOS_SEMESTRE:,}",
            ),
            DimensionISE(
                nombre="Madurez de programas",
                score=round(d_madurez, 1),
                peso=ISE_PESOS["madurez"],
                descripcion="% de programas en Implementación o Escalamiento",
            ),
        ],
    )
