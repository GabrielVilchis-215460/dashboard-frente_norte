import logging
from app.api.woman_inclusion.schemas import InclusionFemenina
from sqlalchemy.orm import Session
from app.models.programa import Programa
from app.utils.helpers import mid_pct

logger = logging.getLogger("stem_api.inclusion_femenina")

def get_inclusion_femenina(db: Session) -> InclusionFemenina:
    """
    Calcula los indicadores de inclusión femenina del ecosistema STEM.

    Usa los valores medios de los rangos de porcentaje de mujeres para
    calcular promedios y distribuciones por nivel educativo.

    Args:
        db: Sesión activa de SQLAlchemy.

    Returns:
        InclusionFemenina: KPIs y distribución de participación femenina.
    """
    logger.info("Calculando inclusión femenina")
    programas = db.query(Programa).filter(Programa.activo == True).all()

    pcts = [mid_pct(p.pct_mujeres_rango) for p in programas if p.pct_mujeres_rango]
    promedio = round(sum(pcts) / len(pcts), 1) if pcts else 0.0

    # Programas con predominio femenino (rango 76-100%)
    enfocados = sum(1 for p in programas if p.pct_mujeres_rango == "76-100")

    # Programas dirigidos a niñas y adolescentes (grupos con brecha de género mayor)
    poblaciones_femeninas = {
        "Niñez (6–12 años)", "Adolescentes (13–17 años)",
        "Niñez (6-12 años)", "Adolescentes (13-17 años)",
        "Niñez (6–12 años)", "Adolescentes (13–17 años)",
    }
    ninas = sum(
        1 for p in programas
        if p.poblacion_objetivo and p.poblacion_objetivo.strip() in poblaciones_femeninas
    )

    # Promedio de participación femenina por nivel educativo
    por_nivel: dict[str, list[float]] = {}
    for p in programas:
        if p.nivel_educativo and p.pct_mujeres_rango:
            por_nivel.setdefault(p.nivel_educativo, []).append(
                mid_pct(p.pct_mujeres_rango)
            )
    por_nivel_avg = {
        k: round(sum(v) / len(v), 1)
        for k, v in por_nivel.items()
    }

    return InclusionFemenina(
        pct_promedio_mujeres=promedio,
        programas_enfocados_mujeres=enfocados,
        programas_ninas_adolescentes=ninas,
        por_nivel_educativo=por_nivel_avg,
    )
