import logging
from collections import Counter
from typing import Any

from app.utils.constants import (
    PCT_MUJERES_RANGOS,
    PCT_MUJERES_DEFAULT_MID,
    VOLUMEN_SEMESTRAL_MIDS,
    ISE_UMBRALES,
    COBERTURA_NIVEL_ALTO,
    COBERTURA_NIVEL_MEDIO
)

logger = logging.getLogger("stem_api.metricas_service")

def mid_pct(range: str | None) -> float:
    """
    Convierte el rango normalizado de porcentaje de mujeres a su valor medio.

    Args:
        rango: Rango normalizado almacenado en BD, ej: "51-75", "26-50".

    Returns:
        Valor medio del rango. Default 37.5 si el rango no es reconocido.
    """
    if not range:
        return PCT_MUJERES_DEFAULT_MID
    
    entry = PCT_MUJERES_RANGOS.get(range)
    if entry:
        return entry[1] # el mid es el segundo elemento de la tupla
    return PCT_MUJERES_DEFAULT_MID

def mid_volume(range: str | None) -> int:
    """
    Retorna el valor medio de un rango de volumen semestral.

    Args:
        rango: Rango almacenado en BD, ej: "1–50", "501 - 1000".

    Returns:
        Valor medio del rango. 0 si el rango no es reconocido.
    """
    if not range:
        return 0
    return VOLUMEN_SEMESTRAL_MIDS.get(range, 0)

def ise_level(score: float) -> str: 
    """
    Determina el nivel cualitativo del ISE a partir del score numérico.

    Args:
        score: Score del ISE entre 0 y 100.

    Returns:
        Nivel: "EXCELENTE", "BUENO", "EN_DESARROLLO" o "CRITICO".
    """
    for umbral, nivel in ISE_UMBRALES:
        if score >= umbral:
            return nivel
    return "CRITICO"

def coverage_level(programs_num: int) -> str:
    """
    Clasifica el nivel de oferta de una colonia según el número de programas.

    Args:
        num_programas: Número de programas activos que impactan la colonia.

    Returns:
        "Alto" (≥3), "Medio" (==2) o "Bajo" (<2).
    """
    if programs_num >= COBERTURA_NIVEL_ALTO:
        return "Alto"
    if programs_num >= COBERTURA_NIVEL_MEDIO:
        return "Medio"
    return "Bajo"

def count_by_field(items: list[Any], field: str) -> dict[str, int]:
    """
    Genera un conteo de ocurrencias de un campo de texto en una lista de objetos.
    Omite valores None y strings vacíos.

    Args:
        items: Lista de instancias de modelos SQLAlchemy.
        campo: Nombre del atributo a contar.

    Returns:
        Diccionario {valor: conteo} ordenado por conteo descendente.
    """
    contador = Counter(
        getattr(item, field)
        for item in items
        if getattr(item, field, None)
    )
    return dict(contador.most_common())
