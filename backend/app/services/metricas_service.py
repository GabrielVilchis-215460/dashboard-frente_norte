"""
Servicio de métricas — toda la lógica de cálculo del dashboard.
Los routers solo llaman a estas funciones; no hay lógica de negocio en los routers.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.organizacion import Organizacion
from app.models.programa import Programa
from app.schemas.metricas import (
    PanoramaGeneral, PerfilBeneficiarios, InclusionFemenina,
    OfertaSTEM, MadurezEcosistema, CoberturaTerritorial,
    IndiceSaludEcosistema, DimensionISE, CoberturaColonia,
)
from typing import Dict
from collections import Counter


# ── helpers ──────────────────────────────────────────────────

def _pct_mid(rango: str) -> float:
    """Convierte el rango de porcentaje de mujeres al valor medio."""
    mapa = {"0–25%": 12.5, "0-25": 12.5,
            "26–50%": 37.5, "26-50": 37.5,
            "51–75%": 62.5, "51-75": 62.5,
            "76–100%": 88.0, "76-100": 88.0}
    return mapa.get(rango, 37.5)


def _volumen_mid(rango: str) -> int:
    """Convierte el rango de volumen al valor medio para cálculos."""
    mapa = {
        "1 - 50": 25, "1–50": 25,
        "51 - 200": 125, "51–200": 125,
        "201 - 500": 350, "201–500": 350,
        "501 - 1000": 750, "501–1000": 750,
        "Más de 1000": 1500, "Más de 1,000 personas.": 1500,
    }
    return mapa.get(rango, 0)


# ── Módulo 1: Panorama General ────────────────────────────────

def get_panorama(db: Session) -> PanoramaGeneral:
    orgs = db.query(Organizacion).filter(Organizacion.activo == True).all()
    programas = db.query(Programa).filter(Programa.activo == True).all()

    tipos_count: Dict[str, int] = {}
    for o in orgs:
        tipos_count[o.tipo] = tipos_count.get(o.tipo, 0) + 1

    areas = set()
    for p in programas:
        areas.update(p.areas_stem or [])

    colonias = set()
    for p in programas:
        colonias.update(p.colonias_impacto or [])

    beneficiarios = sum(_volumen_mid(p.volumen_semestral or "") for p in programas)

    return PanoramaGeneral(
        total_organizaciones=len(orgs),
        total_programas_activos=len(programas),
        beneficiarios_semestre=beneficiarios,
        colonias_impactadas=len(colonias),
        organizaciones_por_tipo=tipos_count,
        areas_stem_representadas=list(areas),
    )


# ── Módulo 2: Perfil de Beneficiarios ────────────────────────

def get_perfil_beneficiarios(db: Session) -> PerfilBeneficiarios:
    programas = db.query(Programa).filter(Programa.activo == True).all()

    etario = Counter(p.poblacion_objetivo for p in programas if p.poblacion_objetivo)
    nivel  = Counter(p.nivel_educativo for p in programas if p.nivel_educativo)
    zona   = Counter(p.zona for p in programas if p.zona)

    return PerfilBeneficiarios(
        por_grupo_etario=dict(etario),
        por_nivel_educativo=dict(nivel),
        por_zona=dict(zona),
    )


# ── Módulo 3: Inclusión y Participación Femenina ─────────────

def get_inclusion_femenina(db: Session) -> InclusionFemenina:
    programas = db.query(Programa).filter(Programa.activo == True).all()

    pcts = [_pct_mid(p.pct_mujeres_rango) for p in programas if p.pct_mujeres_rango]
    promedio = sum(pcts) / len(pcts) if pcts else 0.0

    enfocados = sum(1 for p in programas if p.pct_mujeres_rango in ["76–100%", "76-100"])
    ninas = sum(1 for p in programas
                if p.poblacion_objetivo in ["Niñez (6–12 años)", "Adolescentes (13–17 años)"])

    por_nivel: Dict[str, list] = {}
    for p in programas:
        if p.nivel_educativo and p.pct_mujeres_rango:
            por_nivel.setdefault(p.nivel_educativo, []).append(_pct_mid(p.pct_mujeres_rango))
    por_nivel_avg = {k: round(sum(v)/len(v), 1) for k, v in por_nivel.items()}

    return InclusionFemenina(
        pct_promedio_mujeres=round(promedio, 1),
        programas_enfocados_mujeres=enfocados,
        programas_ninas_adolescentes=ninas,
        por_nivel_educativo=por_nivel_avg,
    )


# ── Módulo 4: Oferta STEM ─────────────────────────────────────

def get_oferta_stem(db: Session) -> OfertaSTEM:
    programas = db.query(Programa).filter(Programa.activo == True).all()
    orgs = db.query(Organizacion).filter(Organizacion.activo == True).all()

    areas: Dict[str, int] = {}
    for p in programas:
        for a in (p.areas_stem or []):
            areas[a] = areas.get(a, 0) + 1

    actividades: Dict[str, int] = {}
    for p in programas:
        for t in (p.tipos_actividad or []):
            actividades[t] = actividades.get(t, 0) + 1

    especialidad: Dict[str, int] = {}
    for o in orgs:
        for a in (o.areas_stem or []):
            especialidad[a] = especialidad.get(a, 0) + 1

    return OfertaSTEM(
        programas_por_area=areas,
        tipos_actividad_ofrecidos=actividades,
        organizaciones_por_especialidad=especialidad,
    )


# ── Módulo 5: Madurez del Ecosistema ─────────────────────────

def get_madurez(db: Session) -> MadurezEcosistema:
    programas = db.query(Programa).filter(Programa.activo == True).all()
    orgs = db.query(Organizacion).filter(Organizacion.activo == True).all()

    por_etapa: Dict[str, int] = {}
    beneficiarios_etapa: Dict[str, int] = {}
    for p in programas:
        etapa = p.madurez or "Sin clasificar"
        por_etapa[etapa] = por_etapa.get(etapa, 0) + 1
        vol = _volumen_mid(p.volumen_semestral or "")
        beneficiarios_etapa[etapa] = beneficiarios_etapa.get(etapa, 0) + vol

    # Madurez de organización = madurez del programa más avanzado
    org_madurez: Dict[str, int] = {}
    orden = {"Escalamiento": 3, "Implementación": 2, "Exploración": 1}
    for o in orgs:
        niveles = [p.madurez for p in o.programas if p.madurez]
        if niveles:
            top = max(niveles, key=lambda x: orden.get(x, 0))
        else:
            top = "Sin clasificar"
        org_madurez[top] = org_madurez.get(top, 0) + 1

    return MadurezEcosistema(
        por_etapa=por_etapa,
        beneficiarios_por_etapa=beneficiarios_etapa,
        organizaciones_por_madurez=org_madurez,
    )


# ── Módulo 6: Cobertura Territorial ──────────────────────────

def get_cobertura(db: Session) -> CoberturaTerritorial:
    programas = db.query(Programa).filter(Programa.activo == True).all()

    colonia_count: Dict[str, int] = {}
    for p in programas:
        for c in (p.colonias_impacto or []):
            colonia_count[c] = colonia_count.get(c, 0) + 1

    zona_count: Dict[str, int] = {}
    for p in programas:
        z = p.zona or "Sin datos"
        zona_count[z] = zona_count.get(z, 0) + 1

    def _nivel(n: int) -> str:
        if n >= 3: return "Alto"
        if n == 2: return "Medio"
        return "Bajo"

    detalle = [
        CoberturaColonia(nombre=c, zona=None, latitud=None, longitud=None,
                         num_programas=n, nivel_oferta=_nivel(n))
        for c, n in colonia_count.items()
    ]

    baja_oferta = [c for c, n in colonia_count.items() if n == 1]

    return CoberturaTerritorial(
        total_colonias_impactadas=len(colonia_count),
        por_zona=zona_count,
        colonias_detalle=detalle,
        zonas_baja_oferta=baja_oferta,
    )


# ── Índice de Salud del Ecosistema STEM ──────────────────────

def get_indice_salud(db: Session) -> IndiceSaludEcosistema:
    """
    ISE = Cobertura*0.25 + Diversidad*0.20 + Inclusión*0.20
          + Alcance*0.20 + Madurez*0.15

    Cada dimensión normalizada 0-100.
    """
    panorama   = get_panorama(db)
    inclusion  = get_inclusion_femenina(db)
    madurez_d  = get_madurez(db)

    TOTAL_COLONIAS_JUAREZ = 600  # referencia para normalizar cobertura
    AREAS_STEM_POSIBLES   = 8    # Ciencia, Tecnología, Ingeniería, Matemáticas,
                                 # Robótica, IA, Medio ambiente, Historia Natural

    cobertura  = min(100, (panorama.colonias_impactadas / TOTAL_COLONIAS_JUAREZ) * 100)
    diversidad = min(100, (len(panorama.areas_stem_representadas) / AREAS_STEM_POSIBLES) * 100)
    inclusion_s = min(100, inclusion.pct_promedio_mujeres)
    alcance    = min(100, (panorama.beneficiarios_semestre / 5000) * 100)

    total_prog = sum(madurez_d.por_etapa.values()) or 1
    escala     = madurez_d.por_etapa.get("Escalamiento", 0)
    impleme    = madurez_d.por_etapa.get("Implementación", 0)
    madurez_s  = min(100, ((escala * 1.0 + impleme * 0.5) / total_prog) * 100)

    score = (cobertura * 0.25 + diversidad * 0.20 + inclusion_s * 0.20
             + alcance * 0.20 + madurez_s * 0.15)

    def _nivel(s: float) -> str:
        if s >= 75: return "Excelente"
        if s >= 50: return "Bueno"
        if s >= 25: return "En desarrollo"
        return "Crítico"

    return IndiceSaludEcosistema(
        score_global=round(score, 1),
        nivel=_nivel(score),
        dimensiones=[
            DimensionISE(nombre="Cobertura territorial", score=round(cobertura, 1),
                         peso=0.25, descripcion="Colonias impactadas vs. total de Juárez"),
            DimensionISE(nombre="Diversidad de oferta STEM", score=round(diversidad, 1),
                         peso=0.20, descripcion="Áreas STEM cubiertas de 8 posibles"),
            DimensionISE(nombre="Inclusión femenina", score=round(inclusion_s, 1),
                         peso=0.20, descripcion="Promedio de participación de mujeres"),
            DimensionISE(nombre="Alcance de beneficiarios", score=round(alcance, 1),
                         peso=0.20, descripcion="Beneficiarios semestre vs. meta 5,000"),
            DimensionISE(nombre="Madurez de programas", score=round(madurez_s, 1),
                         peso=0.15, descripcion="% de programas en Implementación o Escalamiento"),
        ],
    )
