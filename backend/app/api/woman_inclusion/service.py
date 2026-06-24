import logging
from sqlalchemy.orm import Session
from app.api.woman_inclusion.schemas import (
    InclusionFemenina, 
    ProgramaDetalle, 
    RangoParticipacion
)
from app.models.programa import Programa
from app.utils.helpers import mid_pct

logger = logging.getLogger("stem_api.inclusion_femenina")

def get_inclusion_femenina(db: Session) -> InclusionFemenina:
    logger.info("Calculando inclusión femenina")
    programas = db.query(Programa).filter(Programa.activo == True).all()

    pcts = [mid_pct(p.pct_mujeres_rango) for p in programas if p.pct_mujeres_rango]
    promedio = round(sum(pcts) / len(pcts), 1) if pcts else 0.0

    total_ninas = 0
    total_mujeres = 0
    carrusel_destacados = []

    rangos_conteo = {
        "0% - 25%": 0,
        "26% - 50%": 0,
        "51% - 75%": 0,
        "76% - 100%": 0
    }

    poblaciones_femeninas = {
        "Niñez (6–12 años)", "Adolescentes (13–17 años)",
        "Niñez (6-12 años)", "Adolescentes (13-17 años)"
    }

    for p in programas:
        nombre_prog = p.nombre if p.nombre else "Programa sin nombre"
        org_nombre = p.organizacion.nombre if p.organizacion else "Organización Desconocida"
        desc_prog = p.descripcion if p.descripcion else "Sin descripción disponible"
        pct_valor = mid_pct(p.pct_mujeres_rango) if p.pct_mujeres_rango else 0.0

        if p.pct_mujeres_rango == "0-25":
            rangos_conteo["0% - 25%"] += 1
        elif p.pct_mujeres_rango == "26-50":
            rangos_conteo["26% - 50%"] += 1
        elif p.pct_mujeres_rango == "51-75":
            rangos_conteo["51% - 75%"] += 1
        elif p.pct_mujeres_rango == "76-100":
            rangos_conteo["76% - 100%"] += 1

        es_destacado = False

        # logica para tarjetas y carrusel del frontend
        if p.pct_mujeres_rango == "76-100":
            total_mujeres += 1
            es_destacado = True

        if p.poblacion_objetivo and p.poblacion_objetivo.strip() in poblaciones_femeninas:
            total_ninas += 1
            es_destacado = True

        if es_destacado:
            carrusel_destacados.append(
                ProgramaDetalle(
                    nombre=nombre_prog,
                    organizacion=org_nombre,
                    pct_mujeres=pct_valor, 
                    descripcion=desc_prog
                )
            )

    # Convertir el diccionario de rangos al formato de la gráfica
    lista_rangos = [
        RangoParticipacion(rango=k, cantidad=v) 
        for k, v in rangos_conteo.items()
    ]

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
        total_ninas_adolescentes=total_ninas,
        total_enfocados_mujeres=total_mujeres,
        distribucion_por_rango=lista_rangos,
        por_nivel_educativo=por_nivel_avg,
        carrusel_programas_destacados=carrusel_destacados
    )