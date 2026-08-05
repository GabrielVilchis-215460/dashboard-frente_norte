"""
Script de respaldo

Script ETL (Extract, Transform, Load) para la automatización de eventos.

Descripción:
    Descarga el Bundle unificado de RSS.app y procesa los posts con Gemini
    para detectar eventos futuros, extrayendo: nombre, descripción,
    ubicación, coordenadas, fecha, horario, categoría e imagen.

Instrucciones de uso:
    Desde la carpeta backend:
        python -m scripts.etl_events

Frecuencia recomendada:
    Una vez por semana, preferiblemente cada lunes.
"""

import json, re, time, unicodedata, logging, os, requests
from requests.exceptions import HTTPError

from datetime import date, datetime
from difflib import SequenceMatcher

from google import genai
from google.genai import types
from sqlalchemy import or_

from app.db.session import SessionLocal
from app.models.eventos import Evento
from app.models.organizacion import Organizacion
from app.core.config import settings

logger = logging.getLogger("etl_events")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# Constantes
BUNDLE_URL: str = settings.ETL_BUNDLE_URL
FALLBACK_JSON_PATH: str = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "stem_ecosystem.json")

# Bounding box de Ciudad Juárez para validar coordenadas extraídas por IA
# Cualquier valor fuera de este rango se descarta (previene alucinaciones)
_JUAREZ_LAT_MIN, _JUAREZ_LAT_MAX = 31.55, 31.85
_JUAREZ_LNG_MIN, _JUAREZ_LNG_MAX = -106.65, -106.25

# Intervalo mínimo entre llamadas a Gemini (segundos).
# Límite real observado en AI Studio: 15 RPM -> 60/15 = 4s exactos.
# Usamos 6s para dejar margen de seguridad (~10 RPM efectivos).
_GEMINI_MIN_INTERVAL: float = 6.0
_RSS_PLAN_NO_PAGADO = False  # Se activa si el bundle devuelve 402

def _coords_validas(lat: float | None, lng: float | None) -> bool:
    """Devuelve True solo si las coords caen dentro del bounding box de Juárez."""
    if lat is None or lng is None:
        return False
    return (
        _JUAREZ_LAT_MIN <= lat <= _JUAREZ_LAT_MAX
        and _JUAREZ_LNG_MIN <= lng <= _JUAREZ_LNG_MAX
    )

# Rate limiter para Gemini 
class _GeminiRateLimiter:
    """
    Esta clase garantiza un intervalo mínimo real entre llamadas a Gemini usando
    time.monotonic() (no afectado por cambios de reloj del sistema).

    A diferencia de un time.sleep() fijo después de cada post, este
    limiter mide cuánto tiempo *realmente* pasó desde la última llamada
    (incluyendo el tiempo que tardó Gemini en responder) y solo espera
    la diferencia que falte. Así nunca esperamos de más si una llamada
    fue lenta, pero tampoco excedemos el RPM si todas son rápidas.
    """

    def __init__(self, min_interval: float):
        self.min_interval = min_interval
        self._last_call_at: float | None = None

    def wait(self) -> None:
        if self._last_call_at is not None:
            elapsed = time.monotonic() - self._last_call_at
            faltante = self.min_interval - elapsed
            if faltante > 0:
                time.sleep(faltante)
        self._last_call_at = time.monotonic()

_gemini_rate_limiter = _GeminiRateLimiter(_GEMINI_MIN_INTERVAL)


# Gemini 
class GeminiQuotaExceeded(Exception):
    """Se lanza cuando Gemini sigue con 429 tras el retry — señal para detener el lote."""

def _parse_retry_delay(error_str: str) -> float:
    """Extrae el número de segundos del retryDelay incluido en el mensaje de error 429."""
    # Formato SDK: 'retryDelay': '58s'  o  Please retry in 58.54s
    m = re.search(r"retryDelay['\"]?\s*:\s*['\"]?(\d+(?:\.\d+)?)s", error_str)
    if m:
        return float(m.group(1))
    m = re.search(r"retry in (\d+(?:\.\d+)?)s", error_str, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return 65.0  # fallback conservador si no se puede parsear

def _is_429(e: Exception) -> bool:
    return "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)

def _call_gemini(prompt: str, client: genai.Client) -> object:
    # El rate limiter espera lo necesario ANTES de cada llamada real a la API,
    # sin importar si es primer intento o retry.
    _gemini_rate_limiter.wait()
    return client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )

def _get_gemini_client() -> genai.Client:
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY no está configurada.")
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def extract_events_data(text_post: str, org_name: str, client: genai.Client, phase_callback=None) -> tuple[dict, int]:
    """
    Envía el texto del post a Gemini y devuelve el JSON extraído junto con
    el total de tokens consumidos. Devuelve {"es_evento": False} en caso de error.
    """
    date_today = date.today().isoformat()
    prompt = f"""
Eres un analizador de datos experto. Analiza el siguiente texto extraído de las redes sociales de la organización '{org_name}'.
La fecha actual del sistema es {date_today}.

Tu tarea es determinar si el texto anuncia un evento, taller o actividad futura.

REGLA 1: FILTRO DE AUTORÍA ORIGINAL (ANTI-REPOST)
Si el post es un repost o colaboración de un evento organizado por OTRA entidad, marca "es_evento": false.

REGLA 2: UBICACIÓN GEOGRÁFICA
Solo considera válido (es_evento: true) si el evento es en Ciudad Juárez, Chihuahua, o es 100% ONLINE/VIRTUAL.
Extrae el nombre del lugar en "ubicacion" (ej. "T-Hub, Ciudad Juárez").
Además, si el texto menciona una dirección o lugar específico y conocido de Ciudad Juárez del que puedas
inferir coordenadas con alta confianza, extrae "latitud" y "longitud" como números decimales.
Si no puedes determinarlas con certeza, devuelve null en ambos campos.
IMPORTANTE: Las coordenadas deben estar dentro del rango de Ciudad Juárez
(lat entre 31.55 y 31.85, lng entre -106.65 y -106.25). Nunca inventes coordenadas.

REGLA 3: CATEGORIZACIÓN
- ENFOQUE permitido: "Ciencia", "Tecnologia", "Ingenieria", "Matematicas", "Robotica", "Inteligencia artificial", "Medio ambiente", "Finanzas", "Emprendimiento".
- TIPO permitido: "Talleres", "Cursos", "Campamento", "Bootcamp", "Conferencia", "Eventos".

REGLA 4: FECHAS Y HORARIOS
- Evento de un día: "fecha" = ese día, "fecha_fin" = null.
- Rango de fechas: "fecha" = inicio, "fecha_fin" = final. Formato "YYYY-MM-DD".
- "hora_inicio" y "hora_fin" en formato "HH:MM" (24 h). null si no se mencionan.

REGLA 5: DESCRIPCIÓN
Extrae un resumen breve (máximo 3 oraciones) del evento basado exclusivamente en lo que dice el texto.
No inventes información. Si no hay suficiente contexto, devuelve null.

REGLA 6: IMAGEN
Extrae la URL de la imagen promocional si existe explícitamente en el texto. Si no, null.

IMPORTANTE SOBRE EL FORMATO DE RESPUESTA:
Responde ÚNICAMENTE con UN SOLO objeto JSON (nunca una lista/array), incluso si detectas
más de un evento posible en el texto. En ese caso, elige el evento principal o más
prominente del post y describe solo ese.

Responde ÚNICAMENTE con un objeto JSON válido, sin markdown:
{{
    "es_evento": true/false,
    "nombre": "Nombre del evento",
    "descripcion": "Resumen breve o null",
    "ubicacion": "Lugar mencionado o null",
    "latitud": 31.xxxx o null,
    "longitud": -106.xxxx o null,
    "fecha": "YYYY-MM-DD",
    "fecha_fin": "YYYY-MM-DD o null",
    "hora_inicio": "HH:MM o null",
    "hora_fin": "HH:MM o null",
    "enfoque": "Opción permitida o null",
    "tipo": "Opción permitida o null",
    "imagen_url": "URL o null"
}}

Texto del post:
"{text_post}"
"""

    for attempt in range(2):  # intento 0 = primera llamada, intento 1 = retry tras 429
        try:
            response = _call_gemini(prompt, client)

            tokens_used = 0
            if response.usage_metadata:
                m = response.usage_metadata
                logger.info(
                    "  [Tokens] Entrada: %s | Salida: %s | Total: %s",
                    m.prompt_token_count, m.candidates_token_count, m.total_token_count,
                )
                tokens_used = m.total_token_count

            parsed = json.loads(response.text)

            if isinstance(parsed, list):
                logger.warning(
                    "  -> Gemini devolvió una lista de %d elemento(s) en vez de un objeto. "
                    "Se usa el primero.", len(parsed)
                )
                parsed = parsed[0] if parsed else {"es_evento": False}

            if not isinstance(parsed, dict):
                logger.warning("  -> Respuesta de Gemini no es un objeto JSON válido: %r", parsed)
                return {"es_evento": False}, tokens_used

            return parsed, tokens_used

        except Exception as e:
            if _is_429(e):
                delay = _parse_retry_delay(str(e))
                if attempt == 0:
                    logger.warning(
                        "  -> 429 cuota Gemini. Esperando %.0fs antes de reintentar...", delay
                    )
                    if phase_callback:
                        phase_callback("waiting_quota", delay + 2)
                    time.sleep(delay + 2)
                    if phase_callback:
                        phase_callback("", None)
                    continue  # retry
                else:
                    # Segundo 429 consecutivo — detenemos el lote completo
                    logger.error(
                        "  -> 429 cuota Gemini tras reintento. Deteniendo procesamiento del lote."
                    )
                    raise GeminiQuotaExceeded() from e
            logger.error("Error al procesar post con Gemini: %s", e)
            return {"es_evento": False}, 0

    return {"es_evento": False}, 0  # no debería llegar aquí


# Funciones auxilares
def _normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, sin espacios extras — para comparaciones tolerantes."""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return " ".join(texto.split())

def _similitud(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalizar(a), _normalizar(b)).ratio()

def _get_org_from_post(post: dict, db) -> tuple[str, int | None]:
    """
    Devuelve (nombre_org, org_id) a partir del autor del post en el Bundle.
    Primero intenta match exacto (nombre / rss_alias), luego fuzzy normalizado.
    org_id es None si no encuentra nada en BD.
    """
    authors = post.get("authors", [])
    if not (authors and isinstance(authors, list)):
        return "Organización Desconocida", None

    author_name = authors[0].get("name", "").strip()
    if not author_name:
        return "Organización Desconocida", None

    # Match exacto contra nombre o rss_alias
    org_db = (
        db.query(Organizacion)
        .filter(
            or_(Organizacion.nombre == author_name, Organizacion.rss_alias == author_name),
            Organizacion.activo == True,
        )
        .first()
    )
    if org_db:
        return org_db.nombre, org_db.id

    # Match fuzzy normalizado contra todas las orgs activas
    todas = db.query(Organizacion).filter(Organizacion.activo == True).all()
    mejor_sim, mejor_org = 0.0, None
    for o in todas:
        candidatos = [o.nombre]
        if o.rss_alias:
            candidatos.append(o.rss_alias)
        for c in candidatos:
            sim = _similitud(author_name, c)
            if sim > mejor_sim:
                mejor_sim, mejor_org = sim, o

    if mejor_org and mejor_sim >= 0.70:
        logger.info(
            "  [Org] '%s' → '%s' vía fuzzy (%.0f%%)", author_name, mejor_org.nombre, mejor_sim * 100
        )
        return mejor_org.nombre, mejor_org.id

    logger.warning("  [Org] '%s' no encontrada en BD (mejor match %.0f%%). Saltando.", author_name, mejor_sim * 100)
    return author_name, None

def _es_duplicado(eventos_bd: list, fecha_evento: date, nombre_nuevo: str) -> bool:
    """
    Detecta duplicados por nombre similar en la misma fecha en toda la BD.
    Opera sobre la lista cargada en memoria al inicio del lote.
    """
    nombre_nuevo_n = _normalizar(nombre_nuevo)
    for ev in eventos_bd:
        if ev.fecha != fecha_evento:
            continue
        nombre_bd_n = _normalizar(ev.nombre)
        sim = SequenceMatcher(None, nombre_bd_n, nombre_nuevo_n).ratio()
        if sim > 0.72 or nombre_bd_n in nombre_nuevo_n or nombre_nuevo_n in nombre_bd_n:
            logger.info(
                "  [Dedup] '%s' similar a '%s' existente (%.0f%%). Omitiendo.",
                nombre_nuevo, ev.nombre, sim * 100,
            )
            return True
    return False

# Procesamiento de posts
def process_posts(posts: list, db, client: genai.Client, phase_callback=None) -> tuple[int, int]:
    """
    Procesa una lista de posts del Bundle, extrae eventos y los inserta en BD.
    Devuelve (eventos_añadidos, tokens_consumidos).
    No llama a db.commit() — el caller es responsable del commit.
    """
    events_added = 0
    total_tokens = 0

    # Cargar eventos existentes una sola vez para dedup en memoria
    eventos_bd = db.query(Evento).all()

    for i, post in enumerate(posts, 1):
        text_post = post.get("content_text") or post.get("summary") or post.get("title", "")
        url_post = post.get("url", "")
        attachments = post.get("attachments", [])

        org_name, org_id = _get_org_from_post(post, db)

        if not org_id:
            logger.info("[%d/%d] Saltando: org '%s' no encontrada en BD.", i, len(posts), org_name)
            continue

        if not text_post.strip():
            continue

        # Dedup por URL exacta
        if url_post and any(ev.url_original == url_post for ev in eventos_bd):
            logger.info("[%d/%d] Saltando: URL ya existe en BD.", i, len(posts))
            continue

        # Dedup por título del post normalizado (protege contra cambios de URL en RSS)
        titulo_post = _normalizar(post.get("title", ""))
        if titulo_post:
            titulo_duplicado = False
            for ev in eventos_bd:
                if _similitud(titulo_post, ev.nombre) > 0.80:
                    logger.info("[%d/%d] Saltando: título similar a '%s' en BD.", i, len(posts), ev.nombre)
                    titulo_duplicado = True
                    break
            if titulo_duplicado:
                continue

        # Imagen adjunta tiene prioridad sobre la extraída por IA
        attachment_image = None
        if attachments and isinstance(attachments, list):
            attachment_image = attachments[0].get("url")
        if not attachment_image:
            attachment_image = post.get("image") or post.get("thumbnail")

        logger.info("[%d/%d] Analizando post para '%s'...", i, len(posts), org_name)

        try:
            datos, tokens = extract_events_data(text_post, org_name, client, phase_callback=phase_callback)
        except GeminiQuotaExceeded:
            logger.warning("  -> Cuota agotada. Se detiene el análisis de los posts restantes.")
            if phase_callback:
                phase_callback("", None)  # limpiar fase al salir
            break
        total_tokens += tokens

        if not isinstance(datos, dict):
            logger.warning(
                "[%d/%d] -> Respuesta inesperada del modelo (tipo %s). Saltando post.",
                i, len(posts), type(datos).__name__,
            )
            continue

        datos["url_original"] = url_post

        logger.debug("  -> JSON Gemini: %s", json.dumps(datos, ensure_ascii=False))

        if not datos.get("es_evento"):
            logger.info("  -> No es un evento.")
            continue

        logger.info("  -> EVENTO DETECTADO: %s", datos.get("nombre"))
        datos.pop("es_evento", None)

        # Parsear fechas y horas
        if not datos.get("fecha"):
            logger.warning(
                "  -> El modelo marcó el post como evento pero no dio 'fecha'. Se descarta "
                "(revisar manualmente si el evento es real: '%s').", datos.get("nombre")
            )
            continue

        try:
            fecha_evento = datetime.strptime(datos["fecha"], "%Y-%m-%d").date()

            end_date = None
            if datos.get("fecha_fin"):
                end_date = datetime.strptime(datos["fecha_fin"], "%Y-%m-%d").date()
                if end_date < fecha_evento:
                    logger.warning("  -> fecha_fin anterior a fecha; se descarta.")
                    end_date = None

            start_time = None
            if datos.get("hora_inicio"):
                start_time = datetime.strptime(datos["hora_inicio"], "%H:%M").time()

            end_time = None
            if datos.get("hora_fin"):
                end_time = datetime.strptime(datos["hora_fin"], "%H:%M").time()

        except (ValueError, TypeError) as exc:
            logger.warning("  -> Fecha/hora inválida de IA: %s", exc)
            continue

        # Validar coordenadas 
        lat = datos.get("latitud")
        lng = datos.get("longitud")
        if not _coords_validas(lat, lng):
            lat, lng = None, None

        # Imagen final 
        final_image = datos.get("imagen_url") or attachment_image

        # Deduplicación 
        if _es_duplicado(eventos_bd, fecha_evento, datos["nombre"]):
            continue

        nuevo_evento = Evento(
            nombre=datos["nombre"],
            descripcion=datos.get("descripcion"),
            ubicacion=datos.get("ubicacion"),
            latitud=lat,
            longitud=lng,
            fecha=fecha_evento,
            fecha_fin=end_date,
            hora_inicio=start_time,
            hora_fin=end_time,
            enfoque=datos.get("enfoque"),
            tipo=datos.get("tipo"),
            url_original=datos["url_original"],
            imagen_url=final_image,
            organizacion_id=org_id,
            activo=True,
        )
        db.add(nuevo_evento)
        eventos_bd.append(nuevo_evento)  # dedup en memoria para el mismo lote
        events_added += 1
        logger.info("  -> Evento preparado para guardar.")

    return events_added, total_tokens

# Procesamiento del bundle unificado
def process_bundle(db, client: genai.Client, phase_callback=None) -> tuple[int, bool]:
    """Devuelve (tokens_consumidos, rss_no_disponible)."""
    global _RSS_PLAN_NO_PAGADO
    logger.info("\nIniciando procesamiento del Bundle...")

    feed_data = None
    rss_no_disponible = False

    if BUNDLE_URL:
        try:
            logger.info("Descargando Bundle desde: %s", BUNDLE_URL)
            response = requests.get(BUNDLE_URL, timeout=15)
            response.raise_for_status()
            feed_data = response.json()
            logger.info("Bundle descargado correctamente.")
        except HTTPError as e:
            if e.response is not None and e.response.status_code == 402:
                rss_no_disponible = True
                _RSS_PLAN_NO_PAGADO = True
                logger.warning("RSS.app no disponible (plan no pagado). Sin datos nuevos que procesar.")
                return 0, rss_no_disponible
            else:
                logger.warning("No se pudo descargar el Bundle (%s). Usando respaldo local...", e)
        except Exception as e:
            logger.warning("No se pudo descargar el Bundle (%s). Usando respaldo local...", e)

    if feed_data is None:
        if os.path.exists(FALLBACK_JSON_PATH):
            logger.info("Cargando respaldo local: %s", FALLBACK_JSON_PATH)
            with open(FALLBACK_JSON_PATH, "r", encoding="utf-8") as f:
                feed_data = json.load(f)
        else:
            logger.error("Error crítico: no hay Bundle URL ni archivo local en %s", FALLBACK_JSON_PATH)
            return 0, rss_no_disponible

    posts = feed_data.get("items", []) or feed_data.get("entries", [])
    logger.info("Se encontraron %d posts en el Bundle.", len(posts))

    events_added, total_tokens = process_posts(posts, db, client, phase_callback=phase_callback)
    db.commit()

    logger.info("Bundle procesado. Eventos nuevos: %d", events_added)
    return total_tokens, rss_no_disponible


# Punto de entrada
def run_etl(phase_callback=None) -> dict:
    """
    Ejecuta el ETL completo procesando el Bundle unificado.
    Devuelve un resumen con el resultado.
    Puede ser llamado desde CLI o desde el endpoint de administración.
    """
    global _RSS_PLAN_NO_PAGADO
    _RSS_PLAN_NO_PAGADO = False  # Resetear estado al inicio de cada ejecución

    logger.info("\n=== Iniciando ETL de eventos ===")
    total_tokens = 0
    errores: list[str] = []

    try:
        client = _get_gemini_client()
    except RuntimeError as e:
        logger.error(str(e))
        return {"ok": False, "error": str(e), "tokens": 0, "rss_no_disponible": False}

    db = SessionLocal()
    try:
        logger.info("\n--- Procesando Bundle unificado ---")
        try:
            tokens, _ = process_bundle(db, client, phase_callback=phase_callback)
            total_tokens += tokens
        except Exception as e:
            msg = f"Error procesando bundle: {e}"
            logger.error(msg)
            errores.append(msg)
            db.rollback()

    finally:
        db.close()

    if _RSS_PLAN_NO_PAGADO:
        logger.warning("RSS.app no disponible — plan no pagado. Se usaron datos locales de respaldo.")

    logger.info("\n=== ETL finalizado. Tokens totales: %d ===", total_tokens)
    return {
        "ok": True,
        "tokens": total_tokens,
        "errores": errores,
        "rss_no_disponible": _RSS_PLAN_NO_PAGADO,
    }

if __name__ == "__main__":
    resultado = run_etl()
    if not resultado["ok"]:
        raise SystemExit(f"ETL falló: {resultado.get('error')}")