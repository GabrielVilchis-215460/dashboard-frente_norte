"""
Script de seed: importa los datos de los CSVs reales a la BD.

Fuentes:
  - RODADORA_-_Hoja_1.csv         → 6 programas de La Rodadora (los 7 restantes son NaN)
  - Encuesta_de_Indicadores...csv → 7 organizaciones (deduplicando Centro Industria 4.0)

Ejecutar desde /backend:
    python -m scripts.seed_from_csv
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from app.db.session import SessionLocal, engine
from app.models import Organizacion, Programa
from app.db.session import Base

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# ── Helpers ───────────────────────────────────────────────────

def pct_mid(rango: str) -> float:
    mapa = {"0–25%": 12.5, "0-25%": 12.5, "26–50%": 37.5, "51–75%": 62.5, "76–100%": 88.0}
    return mapa.get(str(rango).strip(), 37.5)

def volumen_mid(rango: str) -> int:
    mapa = {"1 - 50": 25, "1–50": 25, "51 - 200": 125, "51–200": 125,
            "501 - 1000": 750, "Más de 1000": 1500, "Más de 1,000 personas.": 1500}
    return mapa.get(str(rango).strip(), 0)

def parse_list(val) -> list:
    if pd.isna(val): return []
    return [x.strip() for x in str(val).split(",") if x.strip()]


# ── 1. Seed organizaciones desde encuesta ────────────────────

def seed_encuesta(db, csv_path: str) -> dict:
    """Retorna {nombre_org: id} para usarlo al insertar programas."""
    df = pd.read_csv(csv_path)

    # Deduplicar Centro de Estudios Industria 4.0 (aparece 2 veces)
    df = df.drop_duplicates(subset=["Nombre de la organización"], keep="first")

    org_ids = {}
    for _, row in df.iterrows():
        nombre = str(row["Nombre de la organización"]).strip()
        if pd.isna(row["Nombre de la organización"]):
            continue

        org = Organizacion(
            nombre=nombre,
            tipo=str(row.get("Tipo de organización", "")).strip(),
            areas_stem=parse_list(row.get("Enfoque y áreas STEM", "")),
            enfoque_principal=str(row.get("¿Cuál es su enfoque principal de trabajo?", "")).strip(),
            descripcion=str(row.get("Descripción de la capacitación/programa:", "")).strip(),
            logo_url=str(row.get("Logo de la organización ", "")).strip() or None,
            contacto=str(row.get("Favor de agregar un contacto principal", "")).strip(),
            zona=str(row.get("Zonas de operación:", "")).strip(),
            colonias=parse_list(row.get("Colonias principales donde impactan:", "")),
            fuente="encuesta_csv",
            # latitud/longitud se llenan en la siguiente fase (investigación documental)
        )
        db.add(org)
        db.flush()  # para obtener el id sin hacer commit
        org_ids[nombre] = org.id

        # Cada organización de la encuesta tiene UN programa implícito
        prog = Programa(
            organizacion_id=org.id,
            nombre=f"Programa de {nombre}",
            descripcion=str(row.get("Descripción de la capacitación/programa:", "")).strip(),
            areas_stem=parse_list(row.get("Enfoque y áreas STEM", "")),
            tipos_actividad=parse_list(row.get("¿Qué tipo de actividades ofrecen?", "")),
            modalidad=str(row.get("Modalidad de los programas:", "")).strip(),
            poblacion_objetivo=str(row.get("Tipo de población que atiende:", "")).strip(),
            nivel_educativo=str(row.get("Nivel educativo predominante:", "")).strip(),
            pct_mujeres_rango=str(row.get("¿Qué porcentaje de sus beneficiarios son mujeres? ", "")).strip(),
            pct_mujeres_mid=pct_mid(str(row.get("¿Qué porcentaje de sus beneficiarios son mujeres? ", ""))),
            zona=str(row.get("Zonas de operación:", "")).strip(),
            colonias_impacto=parse_list(row.get("Colonias principales donde impactan:", "")),
            volumen_semestral=str(row.get("Volumen de atención semestral:", "")).strip(),
            volumen_mid=volumen_mid(str(row.get("Volumen de atención semestral:", ""))),
            temporalidad=str(row.get("Temporalidad de los programas:", "")).strip(),
            madurez=str(row.get("Madurez del programa:", "")).strip(),
            casos_exito=str(row.get("Grupo muestra (Evidencia): Favor de mencionar de 3 a 5 perfiles de beneficiarios destacados o casos de éxito. ", "")).strip(),
            siguiente_paso=str(row.get("Al concluir su programa, ¿cuál es el siguiente paso para el beneficiario?", "")).strip(),
            fuente="encuesta_csv",
        )
        db.add(prog)

    db.commit()
    print(f"✅ {len(org_ids)} organizaciones importadas desde encuesta")
    return org_ids


# ── 2. Seed programas de La Rodadora desde su CSV ────────────

def seed_rodadora(db, csv_path: str, rodadora_id: int):
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["Nombre del programa"])  # elimina filas vacías

    count = 0
    for _, row in df.iterrows():
        prog = Programa(
            organizacion_id=rodadora_id,
            nombre=str(row["Nombre del programa"]).strip(),
            descripcion=str(row.get("Descripción de la capacitación/programa:", "")).strip(),
            areas_stem=[],  # el CSV de Rodadora no tiene columna de áreas; se llena manualmente
            tipos_actividad=["Talleres / Cursos / Bootcamps"],  # default Rodadora
            poblacion_objetivo=str(row.get("Tipo de población que atiende:", "")).strip(),
            nivel_educativo=str(row.get("Nivel educativo predominante:", "")).strip(),
            pct_mujeres_rango=str(row.get("¿Qué porcentaje de sus beneficiarios son mujeres? ", "")).strip(),
            pct_mujeres_mid=pct_mid(str(row.get("¿Qué porcentaje de sus beneficiarios son mujeres? ", ""))),
            zona=str(row.get("Zonas de operación:", "")).strip(),
            colonias_impacto=parse_list(row.get("Colonias principales donde impactan:", "")),
            volumen_semestral=str(row.get("Volumen de atención semestral:", "")).strip(),
            volumen_mid=volumen_mid(str(row.get("Volumen de atención semestral:", ""))),
            temporalidad=str(row.get("Temporalidad de los programas:", "")).strip(),
            madurez=str(row.get("Madurez del programa:", "")).strip(),
            siguiente_paso=str(row.get("Al concluir su programa, ¿cuál es el siguiente paso para el beneficiario?", "")).strip(),
            fuente="rodadora_csv",
        )
        db.add(prog)
        count += 1

    db.commit()
    print(f"✅ {count} programas de La Rodadora importados")


# ── Main ──────────────────────────────────────────────────────

if __name__ == "__main__":
    ENCUESTA_CSV = "../../data/raw/encuesta.csv"
    RODADORA_CSV = "../../data/raw/rodadora.csv"

    db = SessionLocal()
    try:
        org_ids = seed_encuesta(db, ENCUESTA_CSV)
        rodadora_id = org_ids.get("LA RODADORA ESPACIO INTERACTIVO")
        if rodadora_id:
            seed_rodadora(db, RODADORA_CSV, rodadora_id)
        else:
            print("⚠️  La Rodadora no encontrada en encuesta, programas del CSV omitidos")
    finally:
        db.close()
