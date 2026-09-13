import logging
from sqlalchemy.orm import Session
from app.utils import ttl_cache
from app.models.indicadores import Indicador
from app.models.ecosistema import Ecosistema
from app.models.benchmark_valores import BenchmarkValor
from fastapi import HTTPException
from sqlalchemy import func

logger = logging.getLogger("stem_api.indice_salud")

_CACHE_KEY = "indice_salud"
_CACHE_TTL = 300

PLANTILLAS_BRECHAS = {
    "egresados_stem": (
        "El porcentaje de egresados STEM ({valor_juarez}{unidad}) se encuentra por debajo "
        "del referente {ecosistema_referente} ({valor_referente}{unidad}). Se recomienda intensificar convenios "
        "entre la industria local y las universidades para ofrecer becas focalizadas."
    ),
    "mujeres_stem": (
        "La participación de mujeres en el egreso STEM es del {valor_juarez}{unidad}, distanciándose del líder "
        "{ecosistema_referente} ({valor_referente}{unidad}). Se sugiere implementar programas de mentoría temprana y "
        "campañas vocacionales en preparatorias."
    ),
    "empleo_stem": (
        "El empleo formal en áreas STEM representa el {valor_juarez}{unidad}, en contraste con el "
        "{valor_referente}{unidad} de {ecosistema_referente}. Es necesario detonar hubs de innovación y "
        "políticas de atracción de inversiones de alta tecnología."
    ),
    "salario_stem": (
        "El salario promedio en ocupaciones STEM es de ${valor_juarez:,.1f} {unidad}, mientras que en {ecosistema_referente} "
        "alcanza los ${valor_referente:,.1f} {unidad}. Se recomienda impulsar la certificación de competencias avanzadas "
        "y la transición hacia la Industria 4.0."
    ),
    "centros_investigacion": (
        "Se cuenta con {valor_juarez} {unidad}, un valor bajo frente a los {valor_referente} {unidad} de {ecosistema_referente}. "
        "Se aconseja fomentar la triple hélice (Gobierno-Academia-Industria) para establecer laboratorios de investigación aplicada."
    )
}

PLANTILLAS_FORTALEZAS = {
    "egresados_stem": (
        "El ecosistema destaca con un {valor_juarez}{unidad} en egresados STEM, superando al referente {ecosistema_referente} "
        "({valor_referente}{unidad}). Se sugiere capitalizar este volumen de talento con programas de retención local."
    ),
    "mujeres_stem": (
        "En participación de mujeres STEM, se registra un sólido {valor_juarez}{unidad} frente al {valor_referente}{unidad} "
        "de {ecosistema_referente}. Es una oportunidad clave para posicionar a la ciudad como referente en equidad tecnológica."
    ),
    "empleo_stem": (
        "Se muestra un liderazgo sobresaliente en empleo formal STEM ({valor_juarez}{unidad} vs {valor_referente}{unidad} de {ecosistema_referente}). "
        "El siguiente paso estratégico es consolidar clústeres de diseño e ingeniería avanzada."
    ),
    "salario_stem": (
        "El salario promedio STEM (${valor_juarez:,.1f} {unidad}) supera al de {ecosistema_referente} (${valor_referente:,.1f} {unidad}). "
        "Esto refleja una alta competitividad salarial que debe mantenerse impulsando proyectos de I+D."
    ),
    "centros_investigacion": (
        "Se lidera con {valor_juarez} {unidad} superando a {ecosistema_referente} ({valor_referente} {unidad}). "
        "Se recomienda potenciar la vinculación de estos centros con la industria local para acelerar la transferencia tecnológica."
    )
}

def get_indice(db: Session):
    # detección automática del año mas reciente con datos registrados
    anio_actual = db.query(func.max(BenchmarkValor.anio)).scalar()
    if not anio_actual:
        raise HTTPException(status_code=404, detail="No hay datos de benchmark registrados en el sistema.")

    ecosistema_actual = db.query(Ecosistema).filter(Ecosistema.rol == "local").first()
    if not ecosistema_actual:
        raise HTTPException(status_code=404, detail="Ecosistema no encontrado")

    indicadores = db.query(Indicador).all()
    ecosistema_id = ecosistema_actual.id

    kpis = []
    evolucion = []
    benchmark = []

    for ind in indicadores:
        # valor actual del indicador para el año consultado del ecosistema
        val_actual = db.query(BenchmarkValor).filter(
            BenchmarkValor.ecosistema_id == ecosistema_id,
            BenchmarkValor.indicador_id == ind.id,
            BenchmarkValor.anio == anio_actual
        ).first()

        v_actual = float(val_actual.valor) if val_actual else 0.0

        # cambio porcentual vs año anterior para los KPIs
        val_anterior = db.query(BenchmarkValor).filter(
            BenchmarkValor.ecosistema_id == ecosistema_id,
            BenchmarkValor.indicador_id == ind.id,
            BenchmarkValor.anio == anio_actual - 1
        ).first()

        cambio = None
        if val_anterior:
            v_ant = float(val_anterior.valor)
            cambio = round(v_actual - v_ant, 1) # el cambio es puntual no porcentual

        kpis.append({
            "clave": ind.clave,
            "nombre": ind.nombre,
            "valor_actual": v_actual,
            "unidad": ind.unidad,
            "cambio_porcentual": cambio
        })

        # primer carrusel de graficas
        registros_historicos = db.query(BenchmarkValor).filter(
            BenchmarkValor.ecosistema_id == ecosistema_id,
            BenchmarkValor.indicador_id == ind.id
        ).order_by(BenchmarkValor.anio.asc()).all()

        serie_historica = [
            {"anio": reg.anio, "valor": float(reg.valor)} 
            for reg in registros_historicos
        ]

        evolucion.append({
            "indicador_clave": ind.clave,
            "indicador_nombre": ind.nombre,
            "unidad": ind.unidad,
            "serie_historica": serie_historica
        })

        # segundo carrusel de graficas
        valores_ecosistemas = db.query(BenchmarkValor, Ecosistema).join(Ecosistema).filter(
            BenchmarkValor.indicador_id == ind.id,
            BenchmarkValor.anio == anio_actual
        ).order_by(BenchmarkValor.valor.desc()).all()

        comparativa_ecosistemas = [
            {
                "ecosistema": eco.nombre,
                "rol": eco.rol,
                "valor": float(val.valor)
            }
            for val, eco in valores_ecosistemas
        ]

        benchmark.append({
            "indicador_clave": ind.clave,
            "indicador_nombre": ind.nombre,
            "unidad": ind.unidad,
            "comparativa_ecosistemas": comparativa_ecosistemas
        })

    return {
        "ecosistema_actual": ecosistema_actual.nombre,
        "kpis": kpis,
        "carrusel_evolucion" : evolucion,
        "carrusel_benchmark": benchmark
    }


def calcular_brechas(db: Session) -> dict:
    anio = db.query(func.max(BenchmarkValor.anio)).scalar()
    if not anio:
        raise HTTPException(status_code=404, detail="No hay datos de benchmark registrados en el sistema.")

    ecosistema_actual = db.query(Ecosistema).filter(Ecosistema.rol == "local").first()
    if not ecosistema_actual:
        raise HTTPException(status_code=404, detail="No se encontró un ecosistema local configurado.")

    ecosistema_id = ecosistema_actual.id

    cache_key = f"brechas_ecosistema_{ecosistema_id}_{anio}"
    
    cached = ttl_cache.get(cache_key, _CACHE_TTL)
    if cached:
        return cached

    indicadores = db.query(Indicador).all()
    resultados_analisis = []

    for ind in indicadores:
        valor_actual_obj = db.query(BenchmarkValor).filter(
            BenchmarkValor.ecosistema_id == ecosistema_id,
            BenchmarkValor.indicador_id == ind.id,
            BenchmarkValor.anio == anio
        ).first()

        if not valor_actual_obj:
            continue

        v_actual = float(valor_actual_obj.valor)

        mejor_referente = db.query(BenchmarkValor, Ecosistema).join(Ecosistema).filter(
            BenchmarkValor.indicador_id == ind.id,
            BenchmarkValor.anio == anio,
            BenchmarkValor.ecosistema_id != ecosistema_id
        ).order_by(BenchmarkValor.valor.desc()).first()

        if not mejor_referente:
            continue

        val_ref_obj, ecosistema_ref_obj = mejor_referente
        v_ref = float(val_ref_obj.valor)
        nombre_ref = ecosistema_ref_obj.nombre

        diferencia = v_actual - v_ref

        if diferencia >= 0:
            tipo = "fortaleza"
            plantilla = PLANTILLAS_FORTALEZAS.get(ind.clave, "Se muestra un rendimiento competitivo en {nombre}.")
        else:
            tipo = "brecha"
            plantilla = PLANTILLAS_BRECHAS.get(ind.clave, "Se detectó un área de mejora en este indicador.")

        texto_generado = plantilla.format(
            valor_juarez=v_actual,
            valor_referente=v_ref,
            ecosistema_referente=nombre_ref,
            unidad=ind.unidad or ""
        )

        resultados_analisis.append({
            "indicador_clave": ind.clave,
            "indicador_nombre": ind.nombre,
            "tipo": tipo,
            "valor_actual": v_actual,
            "valor_referente": v_ref,
            "referente": nombre_ref,
            "diferencia": round(abs(diferencia), 2),
            "mensaje": texto_generado
        })

    result = {
        "ecosistema": ecosistema_actual.nombre,
        "rol": ecosistema_actual.rol,
        "anio": anio,
        "analisis": resultados_analisis
    }

    ttl_cache.put(cache_key, result)
    return result