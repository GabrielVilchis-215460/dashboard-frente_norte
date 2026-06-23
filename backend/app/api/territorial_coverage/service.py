from sqlalchemy.orm import Session
import logging
from app.api.territorial_coverage.schemas import CoberturaTerritorial, CoberturaColonia
from app.models.programa import Programa
from app.utils.helpers import coverage_level

logger = logging.getLogger("stem_api.cobertura_territorial")

def get_cobertura(db: Session) -> CoberturaTerritorial:
    """
    Calcula la cobertura territorial del ecosistema STEM por colonia y zona.

    Cuenta cuántos programas impactan cada colonia y clasifica el nivel
    de oferta. Las colonias con un solo programa se consideran de baja oferta.

    Args:
        db: Sesión activa de SQLAlchemy.

    Returns:
        CoberturaTerritorial: Cobertura por colonia, zona y zonas de baja oferta.
    """
    logger.info("Calculando cobertura territorial")
    programas = db.query(Programa).filter(Programa.activo == True).all()

    # Conteo de programas por colonia
    colonia_count: dict[str, int] = {}
    for p in programas:
        for colonia in (p.colonias_impacto or []):
            colonia_nombre = colonia.strip()
            if colonia_nombre:
                colonia_count[colonia_nombre] = colonia_count.get(colonia_nombre, 0) + 1

    # Conteo de programas por zona
    zona_count: dict[str, int] = {}
    for p in programas:
        zona = (p.zona or "Sin datos").strip()
        zona_count[zona] = zona_count.get(zona, 0) + 1

    # Detalle de colonias con su nivel de oferta
    detalle = [
        CoberturaColonia(
            nombre=colonia,
            zona=None,     # Sin datos de zona por colonia en el CSV
            latitud=None,  # Sin coordenadas en los datos actuales
            longitud=None,
            num_programas=n,
            nivel_oferta=coverage_level(n)
        )
        for colonia, n in sorted(colonia_count.items(), key=lambda x: x[1], reverse=True)
    ]

    # Colonias de baja oferta = solo 1 programa activo
    baja_oferta = [c for c, n in colonia_count.items() if n < 2]

    logger.info(
        "Cobertura: %d colonias, %d de baja oferta",
        len(colonia_count), len(baja_oferta),
    )

    return CoberturaTerritorial(
        total_colonias_impactadas=len(colonia_count),
        por_zona=zona_count,
        colonias_detalle=detalle,
        zonas_baja_oferta=baja_oferta,
    )
