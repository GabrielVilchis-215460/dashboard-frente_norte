"""
Script de seed: importa los datos de los CSVs reales a la BD.

Fuentes:
  - RODADORA_-_Hoja_1.csv         → 6 programas de La Rodadora (los 7 restantes son NaN)
  - Encuesta_de_Indicadores...csv → 7 organizaciones (deduplicando Centro Industria 4.0)

Ejecutar desde /backend:
    python -m scripts.etl_seed
"""
import sys, os, re, logging
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models import Organizacion, Programa
from app.db.session import Base, SessionLocal, engine
from app.utils.constants import (
    PCT_MUJERES_RANGOS, PCT_MUJERES_DEFAULT_MID, VOLUMEN_SEMESTRAL_MIDS, CSV_NULL_PLACEHOLDERS, DATOS_GEOGRAFICOS_INSTITUCIONES
)

# Montaje del .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Montaje de los logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("seed")

# Rutas de los CSVs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENCUESTA_CSV = os.path.join(BASE_DIR, "..", "data", "raw", "encuesta.csv")
RODADORA_CSV = os.path.join(BASE_DIR, "..", "data", "raw", "rodadora.csv")

# Funciones auxiliares de normalizacion de datos
def clean_text(value) -> str | None:
    """
    Cleans a CSV cell value.
 
    Returns None if:
      - the value is pandas NaN
      - the value is "." (Google Forms placeholder)
      - the resulting string is empty after strip
 
    Args:
        value: Raw cell value (str, float NaN, etc.)
 
    Returns:
        Cleaned string, or None if the value is invalid/empty.
    """
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text in CSV_NULL_PLACEHOLDERS:
        return None
    return text or None
 
def parse_contact(value) -> tuple[str | None, str | None, str | None]:
    """
    Extracts name, email and phone from a free-text contact field.
 
    The Frente Norte survey did not separate these into distinct fields,
    so they come combined in a single string. Real examples:
      "Ivette de la Torre coordinacion.sems@pauta.org.mx 5554523888"
      "José Roberto Carlos. 6562151067"
      "rosella.sipinna@gmail.com"
 
    Args:
        value: Raw cell value from the CSV.
 
    Returns:
        Tuple (name, email, phone). Each element may be None if
        it could not be extracted.
    """
    text = clean_text(value)
    if not text:
        return None, None, None
 
    # Extract email
    email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', text)
    email = email_match.group(0) if email_match else None
 
    # Extract phone (at least 7 digits, may include +, spaces, dashes)
    phone_match = re.search(r'[\+\d][\d\s\-\.]{7,14}', text)
    phone = phone_match.group(0).strip() if phone_match else None
 
    # Name: whatever remains after removing email and phone
    name = text
    if email:
        name = name.replace(email, '')
    if phone:
        name = name.replace(phone, '')

    # Remove noise words that appear in free-text contact fields
    # e.g. "Cel", "Tel", "Tel.", "Cel." written before/after the phone number
    name = re.sub(r'\b[Cc]el\.?\b|\b[Tt]el\.?\b|\b[Tt]eléfono\.?\b', '', name)
    name = re.sub(r'\s+', ' ', name).strip(' ,.-')
    name = name if name else None
 
    return name, email, phone
 
def normalize_women_pct(value) -> tuple[str | None, int | None, int | None, float]:
    """
    Normalizes the women percentage range to canonical format
    and decomposes it into min, max and midpoint.
 
    CSVs use inconsistent formats:
      "51–75%" (em-dash + %) → range="51-75", min=51, max=75, mid=63.0
      "26–50%"               → range="26-50", min=26, max=50, mid=38.0
 
    Args:
        value: Raw cell value from the CSV.
 
    Returns:
        Tuple (normalized_range, min, max, mid).
        If the format is not recognized, returns (None, None, None, 37.5).
    """
    text = clean_text(value)
    if not text:
        return None, None, None, PCT_MUJERES_DEFAULT_MID
 
    entry = PCT_MUJERES_RANGOS.get(text)   
    if entry:
        range_str, mid = entry
        parts = range_str.split('-')
        try:
            pct_min = int(parts[0])
            pct_max = int(parts[1])
        except (IndexError, ValueError):
            pct_min, pct_max = None, None
        return range_str, pct_min, pct_max, mid
 
    logger.warning("Unknown pct_mujeres value: %r → using default 37.5", text)
    return None, None, None, PCT_MUJERES_DEFAULT_MID
 
def normalize_volume(value) -> tuple[str | None, int | None, int | None, int]:
    """
    Normalizes the semestral volume range and decomposes it into min, max and midpoint.
 
    CSVs use different formats:
      Encuesta: "1–50" (em-dash, no spaces)
      Rodadora: "1 - 50" (hyphen with spaces)
      Special:  "Más de 1000" / "Más de 1,000 personas."
 
    Args:
        value: Raw cell value from the CSV.
 
    Returns:
        Tuple (clean_original_range, min, max, mid).
        If the format is not in the catalog, returns (text, None, None, 0).
    """
    text = clean_text(value)
    if not text:
        return None, None, None, 0
 
    mid = VOLUMEN_SEMESTRAL_MIDS.get(text, 0)
    if mid == 0:
        logger.warning("Unknown volumen_semestral value: %r → mid = 0", text)
        return text, None, None, 0
 
    # Extract min and max from the range text
    text_norm = text.replace(',', '').replace('–', '-').replace('—', '-')
    mas_match = re.search(r'[Mm]ás\s+de\s+(\d+)', text_norm)
    if mas_match:
        vol_min = int(mas_match.group(1)) + 1
        vol_max = vol_min + 999   # estimated upper bound
        return text, vol_min, vol_max, mid
 
    range_match = re.search(r'(\d+)\s*-\s*(\d+)', text_norm)
    if range_match:
        return text, int(range_match.group(1)), int(range_match.group(2)), mid
 
    return text, None, None, mid
 
def normalize_logo_url(url: "str | None") -> "str | None":
    """
    Converts a Google Drive share URL to a direct-render URL

    Google Drive share links (open?id=...) do not render as <img src> in
    browsers. This converts them to the uc?export=view format which does.
 
    Example:
      Input:  "https://drive.google.com/open?id=1tFHZy..."
      Output: "https://drive.google.com/uc?export=view&id=1tFHZy..."
 
    Args:
        url: Raw URL string, or None.
 
    Returns:
        Converted URL, original URL if format is not recognized, or None.
    """
    if not url: 
        return 
    match = re.search(r'[?&]id=([\w-]+)', url)
    if match:
        return f"https://drive.google.com/uc?export=view&id={match.group(1)}"
    return url

def parse_list(value) -> list[str]:
    """
    Converts a comma-separated string into a list of clean strings.
 
    Args:
        value: Cell value, e.g. "Ciencia, Tecnología, Robótica"
 
    Returns:
        List of strings, e.g. ["Ciencia", "Tecnología", "Robótica"].
        Empty list if the value is NaN or empty.
    """
    # Patron de separacion para listas de localizacion
    location_split = re. compile(r',\s*(?![A-Z]{2}\b)')
    if pd.isna(value):
        return []
    return [x.strip() for x in location_split.split(str(value)) if x.strip()]
 
def seed_survey(db: Session, csv_path: str) -> dict[str, int]:
    """
    Imports organizations and their programs from the survey CSV.

    Deduplication strategy:
      - CSV-level: drops duplicate organization names before processing.
      - DB-level: checks each organization by name (case-insensitive) before
        inserting. If it already exists, the row is skipped and the existing
        ID is reused to link programs. Programs are also skipped if the
        organization already has a program from encuesta_csv source.

    Args:
        db: Active SQLAlchemy session.
        csv_path: Absolute path to encuesta.csv.

    Returns:
        Dictionary {organization_name: db_id} used to link La Rodadora's
        programs to the organization already created in this step.

    Raises:
        FileNotFoundError: If the CSV file does not exist at the given path.
        Exception: Any DB error — automatic rollback handled in main().
    """
    logger.info("Reading survey CSV: %s", csv_path)
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    logger.info("Rows read: %d", len(df))

    # CSV-level deduplication
    col_name = "Nombre de la organización"
    before = len(df)
    df = df.drop_duplicates(subset=[col_name], keep="first")
    after = len(df)
    if before != after:
        logger.info("CSV duplicates removed: %d row(s)", before - after)

    org_ids: dict[str, int] = {}
    stats = {"orgs_inserted": 0, "orgs_skipped": 0, "progs_inserted": 0, "progs_skipped": 0}

    for idx, row in df.iterrows():
        name = clean_text(row.get(col_name))
        if not name:
            logger.warning("Row %s: empty organization name, skipped", idx)
            continue

        # ── DB-level deduplication: organization ──────────────────────────────
        existing_org = db.query(Organizacion).filter(
            Organizacion.nombre.ilike(name)
        ).first()

        if existing_org:
            logger.info("  ↩ SKIP org (already exists): %s (id=%d)", name, existing_org.id)
            org_ids[name] = existing_org.id
            stats["orgs_skipped"] += 1
        else:
            org_type    = clean_text(row.get("Tipo de organización")) or "Sin clasificar"
            description = clean_text(row.get("Descripción de la capacitación/programa:"))
            contact_name, contact_email, contact_phone = parse_contact(
                row.get("Favor de agregar un contacto principal")
            )
            geo_data = DATOS_GEOGRAFICOS_INSTITUCIONES.get(name, {
                "direccion": None, "latitud": None, "longitud": None, "sitio_web": None
            })

            org = Organizacion(
                nombre=name,
                tipo=org_type,
                areas_stem=parse_list(row.get("Enfoque y áreas STEM")),
                enfoque_principal=clean_text(row.get("¿Cuál es su enfoque principal de trabajo?")),
                descripcion=description,
                logo_url=clean_text(row.get("Logo de la organización ")),
                contacto_nombre=contact_name,
                contacto_email=contact_email,
                contacto_telefono=contact_phone,
                direccion=geo_data.get("direccion"),
                latitud=geo_data.get("latitud"),
                longitud=geo_data.get("longitud"),
                sitio_web=geo_data.get("sitio_web"),
                zona=clean_text(row.get("Zonas de operación:")),
                colonias=parse_list(row.get("Colonias principales donde impactan:")),
                fuente="encuesta_csv",
                activo=True,
            )
            db.add(org)
            db.flush()
            org_ids[name] = org.id
            stats["orgs_inserted"] += 1
            logger.info("  ✓ INSERT org: %s (%s)", name, org_type)
            existing_org = org

        # ── DB-level deduplication: program ───────────────────────────────────
        # Each org from the survey generates one implicit program (nombre=None).
        # Skip if that org already has a program from this source.
        existing_prog = db.query(Programa).filter(
            Programa.organizacion_id == existing_org.id,
            Programa.fuente == "encuesta_csv",
        ).first()

        if existing_prog:
            logger.info("    ↩ SKIP program (already exists for this org)")
            stats["progs_skipped"] += 1
        else:
            description = clean_text(row.get("Descripción de la capacitación/programa:"))
            pct_range, pct_min, pct_max, pct_mid = normalize_women_pct(
                row.get("¿Qué porcentaje de sus beneficiarios son mujeres? ")
            )
            vol_str, vol_min, vol_max, vol_mid = normalize_volume(
                row.get("Volumen de atención semestral:")
            )

            program = Programa(
                organizacion_id=existing_org.id,
                nombre=None,
                descripcion=description,
                areas_stem=parse_list(row.get("Enfoque y áreas STEM")),
                tipos_actividad=parse_list(row.get("¿Qué tipo de actividades ofrecen?")),
                modalidad=clean_text(row.get("Modalidad de los programas:")),
                poblacion_objetivo=clean_text(row.get("Tipo de población que atiende:")),
                nivel_educativo=clean_text(row.get("Nivel educativo predominante:")),
                pct_mujeres_rango=pct_range,
                pct_mujeres_min=pct_min,
                pct_mujeres_max=pct_max,
                pct_mujeres_mid=pct_mid,
                zona=clean_text(row.get("Zonas de operación:")),
                colonias_impacto=parse_list(row.get("Colonias principales donde impactan:")),
                volumen_semestral=vol_str,
                volumen_min=vol_min,
                volumen_max=vol_max,
                volumen_mid=vol_mid,
                temporalidad=clean_text(row.get("Temporalidad de los programas:")),
                madurez=clean_text(row.get("Madurez del programa:")),
                casos_exito=clean_text(
                    row.get("Grupo muestra (Evidencia): Favor de mencionar de 3 a 5 "
                            "perfiles de beneficiarios destacados o casos de éxito. ")
                ),
                siguiente_paso=clean_text(
                    row.get("Al concluir su programa, ¿cuál es el siguiente paso para el beneficiario?")
                ),
                fuente="encuesta_csv",
                activo=True,
            )
            db.add(program)
            stats["progs_inserted"] += 1
            logger.info("    ✓ INSERT program for: %s", name)

    db.commit()
    logger.info(
        "Survey complete — orgs: %d inserted, %d skipped | programs: %d inserted, %d skipped",
        stats["orgs_inserted"], stats["orgs_skipped"],
        stats["progs_inserted"], stats["progs_skipped"],
    )
    return org_ids

def seed_rodadora(db: Session, csv_path: str, rodadora_id: int) -> None:
    """
    Imports La Rodadora's 6 programs from their specific CSV.

    Deduplication strategy:
      - Each program is identified by (organizacion_id + nombre).
      - If a program with the same name already exists for La Rodadora, it is skipped.

    Args:
        db: Active SQLAlchemy session.
        csv_path: Absolute path to rodadora.csv.
        rodadora_id: ID of the "La Rodadora" organization in the DB.

    Raises:
        FileNotFoundError: If the CSV file does not exist at the given path.
    """
    logger.info("Reading rodadora CSV: %s", csv_path)
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    logger.info("Rows read: %d (including empty ones)", len(df))

    df_valid = df.dropna(subset=["Nombre del programa"])
    logger.info("Valid programs: %d", len(df_valid))

    # Preload existing program names for La Rodadora to avoid N+1 queries
    existing_names = {
        p.nombre
        for p in db.query(Programa.nombre)
        .filter(Programa.organizacion_id == rodadora_id, Programa.nombre.isnot(None))
        .all()
    }

    inserted = 0
    skipped  = 0

    for _, row in df_valid.iterrows():
        name = clean_text(row.get("Nombre del programa"))
        if not name:
            continue

        # DB-level deduplication: program by name within this organization
        if name in existing_names:
            logger.info("  ↩ SKIP program (already exists): %s", name)
            skipped += 1
            continue

        pct_range, pct_min, pct_max, pct_mid = normalize_women_pct(
            row.get("¿Qué porcentaje de sus beneficiarios son mujeres? ")
        )
        vol_str, vol_min, vol_max, vol_mid = normalize_volume(
            row.get("Volumen de atención semestral:")
        )

        program = Programa(
            organizacion_id=rodadora_id,
            nombre=name,
            descripcion=clean_text(row.get("Descripción de la capacitación/programa:")),
            areas_stem=[],        # Rodadora CSV has no STEM areas column
            tipos_actividad=[],   # Rodadora CSV has no activity types column
            poblacion_objetivo=clean_text(row.get("Tipo de población que atiende:")),
            nivel_educativo=clean_text(row.get("Nivel educativo predominante:")),
            pct_mujeres_rango=pct_range,
            pct_mujeres_min=pct_min,
            pct_mujeres_max=pct_max,
            pct_mujeres_mid=pct_mid,
            zona=clean_text(row.get("Zonas de operación:")),
            colonias_impacto=parse_list(row.get("Colonias principales donde impactan:")),
            volumen_semestral=vol_str,
            volumen_min=vol_min,
            volumen_max=vol_max,
            volumen_mid=vol_mid,
            temporalidad=clean_text(row.get("Temporalidad de los programas:")),
            madurez=clean_text(row.get("Madurez del programa:")),
            siguiente_paso=clean_text(
                row.get("Al concluir su programa, ¿cuál es el siguiente paso para el beneficiario?")
            ),
            fuente="rodadora_csv",
            activo=True,
        )
        db.add(program)
        existing_names.add(name)   # prevent duplicates within the same CSV run
        inserted += 1
        logger.info("  ✓ INSERT program: %s", name)

    db.commit()
    logger.info("Rodadora complete — %d inserted, %d skipped", inserted, skipped)
 
def main():
    """
    Runs the full seed in order:
      1. Creates tables if they do not exist (no-op if Alembic already ran)
      2. Checks that the DB is empty to prevent duplicates
      3. Imports organizations and programs from the survey
      4. Imports La Rodadora programs linked to the org created in step 3
    """
    logger.info("=" * 60)
    logger.info("SEED — STEM Ecosystem Ciudad Juárez")
    logger.info("=" * 60)
 
    # Create tables if they do not exist 
    Base.metadata.create_all(bind=engine)
 
    db = SessionLocal()
    try:
        existing_orgs = db.query(Organizacion).count()
        if existing_orgs > 0:
            logger.info(
                "DB already has %d organization(s). "
                "Running in idempotent mode — existing records will be skipped.",
                existing_orgs,
            )
 
        # Step 1: Survey
        org_ids = seed_survey(db, ENCUESTA_CSV)
 
        # Step 2: Rodadora
        # La Rodadora was already inserted in step 1 (it appears in encuesta.csv).
        # We look up its ID to link the additional programs from rodadora.csv.
        rodadora_id = org_ids.get("LA RODADORA ESPACIO INTERACTIVO")
        if rodadora_id:
            seed_rodadora(db, RODADORA_CSV, rodadora_id)
        else:
            logger.warning(
                "La Rodadora not found in encuesta.csv under the exact name "
                "'LA RODADORA ESPACIO INTERACTIVO'. "
                "Programs from rodadora.csv were skipped."
            )
            logger.warning("Names found: %s", list(org_ids.keys()))
 
        # Summary
        total_orgs  = db.query(Organizacion).count()
        total_progs = db.query(Programa).count()
        logger.info("=" * 60)
        logger.info("SEED COMPLETE")
        logger.info("  Organizations in DB: %d", total_orgs)
        logger.info("  Programs in DB:      %d", total_progs)
        logger.info("=" * 60)
 
    except Exception as exc:
        logger.error("Error during seed: %s", exc, exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
 
if __name__ == "__main__":
    main()