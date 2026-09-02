"""
Script ETL (Extract, Transform, Load) para la automatización de eventos.

Descripción:
    Descarga el Bundle unificado de RSS.app y procesa los posts con un modelo
    de NVIDIA NIM (nvidia/nemotron-3.5-lightning-30b-a3b) para detectar eventos futuros,
    extrayendo: nombre, descripción, ubicación, coordenadas, fecha, horario,
    categoría e imagen.

Instrucciones de uso:
    Desde la carpeta backend:
        python -m scripts.etl_events

Frecuencia recomendada:
    Una vez por semana, preferiblemente cada lunes.
"""

import json, re, time, unicodedata, logging, os, requests, threading, concurrent.futures
from requests.exceptions import HTTPError

from datetime import date, datetime, timedelta
from difflib import SequenceMatcher

from openai import OpenAI, RateLimitError
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

# Modelo y endpoint de NVIDIA NIM (compatible con el SDK de OpenAI)
NIM_BASE_URL = settings.NIM_BASE_URL
#NIM_MODEL = "meta/llama-3.1-70b-instruct"
NIM_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"

# Bounding box de Ciudad Juárez para validar coordenadas extraídas por IA
# Cualquier valor fuera de este rango se descarta (previene alucinaciones)
_JUAREZ_LAT_MIN, _JUAREZ_LAT_MAX = 31.55, 31.85
_JUAREZ_LNG_MIN, _JUAREZ_LNG_MAX = -106.65, -106.25

# Intervalo mínimo global entre llamadas a NIM (segundos).
# Límite del free tier: 40 RPM → 60/40 = 1.5s exactos entre llamadas globales.
# El limiter es thread-safe para soportar procesamiento paralelo.
_NIM_MIN_INTERVAL: float = 1.5
_RSS_PLAN_NO_PAGADO = False  # Se activa si el bundle devuelve 402

# Límites de texto del post enviado a NIM
_TEXT_MIN_CHARS = 80       # posts muy cortos no tienen info suficiente
_TEXT_MAX_CHARS = 2500     # truncar para ahorrar tokens y mantener instrucciones al frente

# Ventana de fechas aceptables
_FECHA_MAX_PASADO_DIAS = 14   # eventos que empezaron hace más de 14 días se descartan
_FECHA_MAX_FUTURO_DIAS = 730  # eventos a más de 2 años se descartan (posible alucinación)

# Valores permitidos para validación post-extracción
_ENFOQUES_VALIDOS = {"Ciencia", "Tecnologia", "Ingenieria", "Matematicas", "Robotica",
                     "Inteligencia artificial", "Medio ambiente", "Finanzas", "Emprendimiento"}
_TIPOS_VALIDOS = {"Talleres", "Cursos", "Campamento", "Bootcamp", "Conferencia", "Eventos"}

# Cap de seguridad: máximo de eventos extraíbles de un solo post.
# Previene que el modelo "alucine" listas largas de eventos inventados.
_MAX_EVENTOS_POR_POST = 8
_MAX_ENFOQUES_POR_EVENTO = 3

# Claves que algunos modelos usan para envolver el array de resultados
_WRAPPER_KEYS = ("eventos", "events", "items", "data", "results", "lista")

# Palabras clave que indican que un post PODRÍA anunciar un evento.
# Un post sin ninguna de estas palabras se descarta antes de llamar a NIM,
# reduciendo el número de llamadas a la API en un 40-60%.
_PALABRAS_EVENTO = {
    # Tipos de actividad
    "taller", "talleres", "curso", "cursos", "clase", "clases",
    "conferencia", "conferencias", "webinar", "webinars", "seminario",
    "bootcamp", "hackathon", "campamento", "feria", "simposio",
    "workshop", "training", "capacitación", "charla", "ponencia",
    "open house", "demo day", "pitch", "concurso", "competencia",
    # Verbos de invitación
    "regístrate", "inscríbete", "inscribete", "registrate", "únete",
    "participa", "asiste", "acompáñanos", "acompañanos", "join",
    "register", "sign up", "signup", "enroll",
    # Sustantivos de convocatoria
    "convocatoria", "inscripción", "inscripcion", "registro", "cupo",
    "cupos", "evento", "eventos", "actividad", "actividades", "sesión",
    "sesion", "reunion", "reunión",
    # Palabras de tiempo que indican fecha concreta
    "lunes", "martes", "miércoles", "miercoles", "jueves", "viernes",
    "sábado", "sabado", "domingo",
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    # Palabras de horario
    "am", "pm", "hrs", "horas", "hora", "horario",
}

def _tiene_palabras_evento(texto: str) -> bool:
    """
    Filtro rápido O(n) en Python: descarta posts que no contienen ninguna
    palabra clave de evento. Evita llamadas a NIM innecesarias.
    Se aplica sobre el texto normalizado (minúsculas, sin tildes).
    """
    texto_n = _normalizar(texto)
    return any(kw in texto_n for kw in _PALABRAS_EVENTO)


def _coords_validas(lat: float | None, lng: float | None) -> bool:
    """Devuelve True solo si las coords caen dentro del bounding box de Juárez."""
    if lat is None or lng is None:
        return False
    return (
        _JUAREZ_LAT_MIN <= lat <= _JUAREZ_LAT_MAX
        and _JUAREZ_LNG_MIN <= lng <= _JUAREZ_LNG_MAX
    )

# Rate limiter para NIM — thread-safe para procesamiento paralelo
class _NimRateLimiter:
    """
    Garantiza un intervalo mínimo global entre llamadas a NIM usando
    time.monotonic() y un lock para soportar múltiples workers simultáneos.

    El patrón check-and-reserve evita que dos threads obtengan el slot
    al mismo tiempo: solo se actualiza _last_call_at cuando el thread
    ya "ganó" su turno, antes de liberar el lock.
    """

    def __init__(self, min_interval: float):
        self.min_interval = min_interval
        self._lock = threading.Lock()
        self._last_call_at: float = 0.0

    def wait(self) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                elapsed = now - self._last_call_at
                if elapsed >= self.min_interval:
                    self._last_call_at = now
                    return
                wait_time = self.min_interval - elapsed
            time.sleep(wait_time)

_nim_rate_limiter = _NimRateLimiter(_NIM_MIN_INTERVAL)


# NVIDIA NIM
class NimQuotaExceeded(Exception):
    """Se lanza cuando NIM sigue con 429 tras el retry — señal para detener el lote."""

def _parse_retry_delay(error: Exception) -> float:
    """
    Extrae el número de segundos de espera de un error 429.
    El SDK de OpenAI expone el header Retry-After cuando el servidor lo manda;
    NIM no siempre lo incluye, así que caemos a un valor conservador si falta.
    """
    response = getattr(error, "response", None)
    if response is not None:
        retry_after = response.headers.get("retry-after")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
    m = re.search(r"retry in (\d+(?:\.\d+)?)s", str(error), re.IGNORECASE)
    if m:
        return float(m.group(1))
    return 65.0  # fallback conservador si no se puede determinar

def _is_429(e: Exception) -> bool:
    return isinstance(e, RateLimitError) or "429" in str(e)

def _strip_json_fences(raw: str) -> str:
    """Quita ```json ... ``` o bloques <think>...</think> que algunos modelos
    abiertos agregan pese a la instrucción de responder solo JSON."""
    raw = raw.strip()
    if "<think>" in raw and "</think>" in raw:
        raw = raw.split("</think>", 1)[1].strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0]
    return raw.strip()

def _call_nim(prompt: str, client: OpenAI) -> object:
    _nim_rate_limiter.wait()
    return client.chat.completions.create(
        model=NIM_MODEL,
        messages=[
            {"role": "system", "content": "Responde únicamente con un array JSON válido, sin markdown ni texto adicional."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=1000,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}}, # este modelo cuenta con modo thinking
    )

def _get_nim_client() -> OpenAI:
    if not settings.NVIDIA_API_KEY:
        raise RuntimeError("NVIDIA_API_KEY no está configurada.")
    return OpenAI(base_url=NIM_BASE_URL, api_key=settings.NVIDIA_API_KEY, timeout=90)

def _construir_prompt(text_post: str, org_name: str) -> str:
    date_today = date.today().isoformat()
    texto_truncado = text_post[:_TEXT_MAX_CHARS]
    texto_escapado = texto_truncado.replace("\\", "\\\\").replace('"""', "'''")

    return f"""Eres un extractor de datos experto para un directorio de eventos STEM en Ciudad Juárez, México.
Analiza el siguiente post de redes sociales publicado por la organización "{org_name}".
Fecha actual: {date_today}.

TAREA
Extraer TODOS los eventos válidos que mencione el post. Un post puede contener cero, uno o varios eventos
(por ejemplo, un resumen semanal de actividades). Devuelve un array JSON con un objeto por evento.
Si no hay eventos válidos, devuelve un array vacío: []

REGLA 1 — AUTORÍA ORIGINAL
Incluye solo eventos organizados DIRECTAMENTE por "{org_name}".
Si un evento lo organiza OTRA entidad (repost, mención, colaboración externa), omítelo.
Excepción: si "{org_name}" es co-organizador explícito ("by the Hub in collaboration with…"), inclúyelo.

REGLA 2 — FECHA OBLIGATORIA
Incluye solo eventos con fecha explícita en el texto. No inventes ni inferras fechas.
Formato: "YYYY-MM-DD". Si el texto dice solo mes y día, usa el año {date_today[:4]}.
Si el año inferido produce una fecha pasada de más de 30 días, usa {int(date_today[:4]) + 1}.

REGLA 3 — UBICACIÓN GEOGRÁFICA
Incluye solo eventos en Ciudad Juárez, Chihuahua, México, o 100% ONLINE/VIRTUAL.
Si el evento es claramente en otra ciudad (ej. El Paso, TX), omítelo.
Coordenadas: solo si las puedes inferir con certeza del texto. Rango Juárez: lat 31.55–31.85, lng -106.65 a -106.25.
Si no las conoces con certeza, pon null en ambos campos.

REGLA 4 — HORARIOS
Convierte siempre a formato 24h (HH:MM).
Ejemplos: "12:15 PM" → "12:15", "8:30 AM" → "08:30", "4 PM" → "16:00", "10am" → "10:00".
Si no se menciona hora, pon null.

REGLA 5 — CATEGORIZACIÓN (usa exactamente estos valores, sin variaciones)
ENFOQUE: un array con UNO O MÁS valores de la siguiente lista (máximo 3), según los temas que
realmente aborde el evento. Si el evento combina disciplinas, inclúyelas todas. Si no aplica
ninguna, usa un array vacío [].
Valores permitidos: "Ciencia" | "Tecnologia" | "Ingenieria" | "Matematicas" | "Robotica" | "Inteligencia artificial" | "Medio ambiente" | "Finanzas" | "Emprendimiento"
TIPO: "Talleres" | "Cursos" | "Campamento" | "Bootcamp" | "Conferencia" | "Eventos" (un solo valor, no array)
Ejemplo: un hackathon de robótica enfocado en negocios → ["Robotica", "Emprendimiento"]
No repitas valores ni inventes combinaciones fuera de la lista.

REGLA 6 — DESCRIPCIÓN
Máximo 2 oraciones por evento, basadas únicamente en el texto del post. No inventes detalles.
Si no hay información suficiente, pon null.

REGLA 7 — IMAGEN
Extrae la URL de imagen solo si aparece explícitamente en el texto. Si no, null.

FORMATO DE RESPUESTA
Devuelve ÚNICAMENTE el array JSON, sin markdown, sin texto antes ni después.
Estructura de cada objeto (todos los campos son obligatorios, usa null cuando no aplique):
[
  {{
    "nombre": "string",
    "descripcion": "string o null",
    "ubicacion": "string o null",
    "latitud": número o null,
    "longitud": número o null,
    "fecha": "YYYY-MM-DD",
    "fecha_fin": "YYYY-MM-DD o null",
    "hora_inicio": "HH:MM o null",
    "hora_fin": "HH:MM o null",
    "enfoque": ["valor_exacto", "..."],
    "tipo": "valor_exacto o null",
    "imagen_url": "URL o null"
  }}
]

POST A ANALIZAR:
\"\"\"
{texto_escapado}
\"\"\""""


def _parsear_hora(raw: str | None) -> "datetime.time | None":
    """Parsea hora en formato 24h o 12h (AM/PM). Retorna None si falla."""
    if not raw:
        return None
    raw = raw.strip()
    for fmt in ("%H:%M", "%I:%M %p", "%I:%M%p", "%I %p", "%I%p"):
        try:
            return datetime.strptime(raw.upper(), fmt.upper()).time()
        except ValueError:
            continue
    return None


def _limpiar_texto(valor: str | None, max_len: int = 500) -> str | None:
    """Strip de whitespace y truncado. Retorna None si queda vacío."""
    if not valor or not isinstance(valor, str):
        return None
    limpio = " ".join(valor.split())
    return limpio[:max_len] if limpio else None


def _validar_fecha(fecha_str: str | None) -> "date | None":
    """Parsea fecha YYYY-MM-DD con tolerancia a formatos sin cero inicial."""
    if not fecha_str or not isinstance(fecha_str, str):
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(fecha_str.strip(), fmt).date()
        except ValueError:
            continue
    return None

def _validar_enfoques(raw: object, prefijo: str, nombre: str) -> list[str]:
    """
    Normaliza el campo 'enfoque' devuelto por NIM a una lista de valores válidos.
    Acepta tanto un string único (compatibilidad hacia atrás, por si el modelo
    ignora la instrucción de array) como una lista. Descarta valores no
    reconocidos, elimina duplicados conservando el orden, y aplica el cap
    de seguridad para prevenir listas infladas por alucinación del modelo.
    """
    if not raw:
        return []

    if isinstance(raw, str):
        raw = [raw]

    if not isinstance(raw, list):
        logger.warning("%s Enfoque con formato inesperado (%s); se descarta.", prefijo, type(raw).__name__)
        return []

    vistos: set[str] = set()
    validos: list[str] = []
    for val in raw:
        if not isinstance(val, str):
            continue
        val = val.strip()
        if val not in _ENFOQUES_VALIDOS:
            logger.warning("%s Enfoque '%s' no reconocido; se descarta.", prefijo, val)
            continue
        if val not in vistos:
            vistos.add(val)
            validos.append(val)

    if len(validos) > _MAX_ENFOQUES_POR_EVENTO:
        logger.warning(
            "%s '%s' con %d enfoques (máx %d); truncando.",
            prefijo, nombre, len(validos), _MAX_ENFOQUES_POR_EVENTO,
        )
        validos = validos[:_MAX_ENFOQUES_POR_EVENTO]

    return validos

def _normalizar_respuesta_nim(parsed: object) -> list[dict]:
    """
    Normaliza la respuesta de NIM a list[dict] independientemente del formato
    que haya devuelto el modelo. Aplica el cap de seguridad y filtra basura.
    """
    # Caso 1: array directo (formato esperado)
    if isinstance(parsed, list):
        eventos = parsed

    # Caso 2: dict envuelto en una clave conocida  {"eventos": [...]}
    elif isinstance(parsed, dict):
        for key in _WRAPPER_KEYS:
            if key in parsed and isinstance(parsed[key], list):
                logger.warning("  -> NIM envolvió el array en la clave '%s'. Extrayendo.", key)
                eventos = parsed[key]
                break
        else:
            # Caso 3: dict único con campos de evento — modelo ignoró la instrucción de array
            if "nombre" in parsed or "fecha" in parsed:
                logger.warning("  -> NIM devolvió un objeto único en vez de array. Convirtiendo.")
                eventos = [parsed]
            else:
                logger.warning("  -> Respuesta de NIM no reconocida: %r", type(parsed))
                return []
    else:
        logger.warning("  -> Respuesta de NIM inesperada (tipo %s). Descartando.", type(parsed).__name__)
        return []

    # Filtrar elementos que no sean dicts
    validos = [e for e in eventos if isinstance(e, dict)]
    descartados = len(eventos) - len(validos)
    if descartados:
        logger.warning("  -> %d elemento(s) del array no son objetos válidos; descartados.", descartados)

    # Aplicar cap de seguridad
    if len(validos) > _MAX_EVENTOS_POR_POST:
        logger.warning(
            "  -> NIM devolvió %d eventos (máximo permitido: %d). Truncando.",
            len(validos), _MAX_EVENTOS_POR_POST,
        )
        validos = validos[:_MAX_EVENTOS_POR_POST]

    return validos


def extract_events_data(text_post: str, org_name: str, client: OpenAI, phase_callback=None) -> tuple[list[dict], int]:
    """
    Envía el texto del post a NIM y devuelve la lista de eventos extraídos
    junto con el total de tokens consumidos.
    Retorna ([], 0) ante cualquier error no recuperable.
    """
    prompt = _construir_prompt(text_post, org_name)

    for attempt in range(2):  # intento 0 = primera llamada, intento 1 = retry tras 429
        try:
            response = _call_nim(prompt, client)

            tokens_used = 0
            usage = getattr(response, "usage", None)
            if usage:
                logger.info(
                    "  [Tokens] Entrada: %s | Salida: %s | Total: %s",
                    usage.prompt_tokens, usage.completion_tokens, usage.total_tokens,
                )
                tokens_used = usage.total_tokens

            raw = _strip_json_fences(response.choices[0].message.content)
            parsed = json.loads(raw)
            eventos = _normalizar_respuesta_nim(parsed)

            logger.info("  -> %d evento(s) extraído(s) del post.", len(eventos))
            return eventos, tokens_used

        except json.JSONDecodeError as e:
            logger.error("  -> Respuesta de NIM no es JSON válido: %s", e)
            return [], 0

        except Exception as e:
            if _is_429(e):
                delay = _parse_retry_delay(e)
                if attempt == 0:
                    logger.warning(
                        "  -> 429 rate limit NIM. Esperando %.0fs antes de reintentar...", delay
                    )
                    if phase_callback:
                        phase_callback("waiting_quota", delay + 2)
                    time.sleep(delay + 2)
                    if phase_callback:
                        phase_callback("", None)
                    continue
                else:
                    logger.error("  -> 429 tras reintento. Deteniendo procesamiento del lote.")
                    raise NimQuotaExceeded() from e
            logger.error("Error al procesar post con NIM: %s", e)
            return [], 0

    return [], 0  # no debería llegar aquí


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

def _es_duplicado(eventos_bd: list[dict], fecha_evento: date, nombre_nuevo: str) -> bool:
    """
    Detecta duplicados por nombre similar en la misma fecha en toda la BD.
    Opera sobre la lista de dicts {"fecha", "nombre", "url_original"} cargada en memoria.
    """
    nombre_nuevo_n = _normalizar(nombre_nuevo)
    for ev in eventos_bd:
        if ev["fecha"] != fecha_evento:
            continue
        nombre_bd_n = _normalizar(ev["nombre"])
        sim = SequenceMatcher(None, nombre_bd_n, nombre_nuevo_n).ratio()
        if sim > 0.72 or nombre_bd_n in nombre_nuevo_n or nombre_nuevo_n in nombre_bd_n:
            logger.info(
                "  [Dedup] '%s' similar a '%s' existente (%.0f%%). Omitiendo.",
                nombre_nuevo, ev["nombre"], sim * 100,
            )
            return True
    return False

# Procesamiento de posts
_NIM_WORKERS = 8  # workers paralelos — el rate limiter global gestiona el RPM

def process_posts(posts: list, client: OpenAI, phase_callback=None) -> tuple[int, int, int, int]:
    """
    Procesa una lista de posts del Bundle, extrae eventos y los inserta en BD.

    Usa dos sesiones de BD de corta duración para evitar que la conexión quede
    abierta e inactiva durante los minutos que tardan las llamadas a NIM:
      - Sesión 1 (Fase 1): pre-filtrado y carga de catálogos → cierra antes de NIM.
      - Sesión 2 (Fase 3): inserción de eventos → abre DESPUÉS de NIM → commit → cierra.

    Devuelve (eventos_añadidos, tokens_consumidos, posts_candidatos, total_posts).
    """
    events_added = 0
    total_tokens = 0

    # ── Fase 1: pre-filtrado con sesión corta ─────────────────────────────────
    # Cargamos los datos que necesitamos en memoria (dicts plain) y cerramos la
    # sesión ANTES de la fase NIM para no dejar una conexión idle varios minutos.
    db_pre = SessionLocal()
    try:
        eventos_bd: list[dict] = [
            {"fecha": ev.fecha, "nombre": ev.nombre, "url_original": ev.url_original}
            for ev in db_pre.query(Evento).all()
        ]
        # Set de URLs existentes para dedup O(1) — evita O(n) por cada post
        urls_existentes: set[str] = {
            ev["url_original"] for ev in eventos_bd if ev["url_original"]
        }

        candidates = []
        for i, post in enumerate(posts, 1):
            text_post = post.get("content_text") or post.get("summary") or post.get("title", "")
            url_post = post.get("url", "")
            attachments = post.get("attachments", [])

            org_name, org_id = _get_org_from_post(post, db_pre)
            if not org_id:
                logger.info("[%d/%d] Saltando: org '%s' no encontrada en BD.", i, len(posts), org_name)
                continue
            if len(text_post.strip()) < _TEXT_MIN_CHARS:
                logger.info("[%d/%d] Saltando: texto demasiado corto (%d chars).", i, len(posts), len(text_post.strip()))
                continue
            if url_post and url_post in urls_existentes:
                logger.info("[%d/%d] Saltando: URL ya existe en BD.", i, len(posts))
                continue
            titulo_post = _normalizar(post.get("title", ""))
            if titulo_post and any(_similitud(titulo_post, ev["nombre"]) > 0.80 for ev in eventos_bd):
                logger.info("[%d/%d] Saltando: título similar ya existe en BD.", i, len(posts))
                continue
            if not _tiene_palabras_evento(text_post):
                logger.info("[%d/%d] Saltando: sin palabras clave de evento.", i, len(posts))
                continue

            attachment_image = None
            if attachments and isinstance(attachments, list):
                attachment_image = attachments[0].get("url")
            if not attachment_image:
                attachment_image = post.get("image") or post.get("thumbnail")

            candidates.append({
                "idx": i,
                "total": len(posts),
                "text": text_post,
                "url": url_post,
                "org_name": org_name,
                "org_id": org_id,
                "attachment_image": attachment_image,
            })
    finally:
        db_pre.close()  # libera la conexión antes de la fase NIM (puede tardar minutos)

    logger.info("Posts candidatos para NIM: %d / %d", len(candidates), len(posts))

    # ── Fase 2: llamadas NIM en paralelo (sin BD) ─────────────────────────────
    quota_exceeded = threading.Event()
    # (candidate, lista_eventos, tokens_consumidos)
    nim_results: list[tuple[dict, list[dict], int]] = []
    results_lock = threading.Lock()

    def extract_one(cand: dict) -> None:
        if quota_exceeded.is_set():
            return
        logger.info("[%d/%d] Analizando post para '%s'...", cand["idx"], cand["total"], cand["org_name"])
        try:
            lista_eventos, tokens = extract_events_data(cand["text"], cand["org_name"], client, phase_callback)
            with results_lock:
                nim_results.append((cand, lista_eventos, tokens))
        except NimQuotaExceeded:
            quota_exceeded.set()
            logger.warning("  -> Cuota agotada. Cancelando posts restantes.")
            if phase_callback:
                phase_callback("", None)

    with concurrent.futures.ThreadPoolExecutor(max_workers=_NIM_WORKERS) as executor:
        executor.map(extract_one, candidates)

    # ── Fase 3: validación e inserción con sesión fresca ─────────────────────
    # La sesión se abre AQUÍ, después de NIM, garantizando una conexión activa.
    # pool_pre_ping=True en el engine la verificará antes de usarla.
    hoy = date.today()
    fecha_min = hoy - timedelta(days=_FECHA_MAX_PASADO_DIAS)
    fecha_max = hoy + timedelta(days=_FECHA_MAX_FUTURO_DIAS)

    nuevos_eventos: list[Evento] = []    # para capturar IDs tras el commit
    urls_nuevas: set[str] = set()        # dedup de URLs de este run (complementa urls_existentes)

    db_insert = SessionLocal()
    try:
        for cand, lista_eventos, tokens in nim_results:
            total_tokens += tokens

            if not lista_eventos:
                logger.info("  -> Post de '%s': sin eventos válidos.", cand["org_name"])
                continue

            for ev_idx, datos in enumerate(lista_eventos, 1):
                prefijo = f"  [Evento {ev_idx}/{len(lista_eventos)}]"
                logger.debug("%s JSON: %s", prefijo, json.dumps(datos, ensure_ascii=False))

                # ── Validar nombre ────────────────────────────────────────────
                nombre = _limpiar_texto(datos.get("nombre"), max_len=200)
                if not nombre:
                    logger.warning("%s Sin nombre válido. Descartando.", prefijo)
                    continue

                logger.info("%s EVENTO DETECTADO: %s", prefijo, nombre)

                # ── Validar fecha ─────────────────────────────────────────────
                fecha_evento = _validar_fecha(datos.get("fecha"))
                if not fecha_evento:
                    logger.warning("%s '%s' sin fecha válida. Descartando.", prefijo, nombre)
                    continue
                if fecha_evento < fecha_min:
                    logger.info("%s '%s' con fecha %s muy en el pasado. Descartando.", prefijo, nombre, fecha_evento)
                    continue
                if fecha_evento > fecha_max:
                    logger.warning("%s '%s' con fecha %s muy en el futuro (posible alucinación). Descartando.", prefijo, nombre, fecha_evento)
                    continue

                # ── Validar fecha_fin ─────────────────────────────────────────
                end_date = _validar_fecha(datos.get("fecha_fin"))
                if end_date and end_date < fecha_evento:
                    logger.warning("%s fecha_fin anterior a fecha_inicio; se descarta.", prefijo)
                    end_date = None

                # ── Parsear horarios (tolerante a 12h y 24h) ──────────────────
                start_time = _parsear_hora(datos.get("hora_inicio"))
                end_time = _parsear_hora(datos.get("hora_fin"))
                if datos.get("hora_inicio") and not start_time:
                    logger.warning("%s Hora inicio '%s' no reconocida; se omite.", prefijo, datos.get("hora_inicio"))
                if datos.get("hora_fin") and not end_time:
                    logger.warning("%s Hora fin '%s' no reconocida; se omite.", prefijo, datos.get("hora_fin"))

                # ── Validar coordenadas ───────────────────────────────────────
                lat = datos.get("latitud")
                lng = datos.get("longitud")
                if not _coords_validas(lat, lng):
                    lat, lng = None, None

                # ── Validar enfoque y tipo contra listas permitidas ───────────
               # enfoque = datos.get("enfoque")
                #if enfoque and enfoque not in _ENFOQUES_VALIDOS:
                 #   logger.warning("%s Enfoque '%s' no reconocido; se descarta.", prefijo, enfoque)
                  #  enfoque = None
                # ── Validar enfoques (lista) y tipo contra listas permitidas ──
                enfoque = _validar_enfoques(datos.get("enfoque"), prefijo, nombre)

                tipo = datos.get("tipo")
                if tipo and tipo not in _TIPOS_VALIDOS:
                    logger.warning("%s Tipo '%s' no reconocido; se descarta.", prefijo, tipo)
                    tipo = None

                # ── Limpiar campos de texto ───────────────────────────────────
                descripcion = _limpiar_texto(datos.get("descripcion"), max_len=1000)
                ubicacion = _limpiar_texto(datos.get("ubicacion"), max_len=200)
                imagen_url_nim = _limpiar_texto(datos.get("imagen_url"), max_len=500)
                final_image = imagen_url_nim or cand["attachment_image"]

                if _es_duplicado(eventos_bd, fecha_evento, nombre):
                    continue

                nuevo_evento = Evento(
                    nombre=nombre,
                    descripcion=descripcion,
                    ubicacion=ubicacion,
                    latitud=lat,
                    longitud=lng,
                    fecha=fecha_evento,
                    fecha_fin=end_date,
                    hora_inicio=start_time,
                    hora_fin=end_time,
                    enfoque=enfoque,
                    tipo=tipo,
                    url_original=cand["url"],
                    imagen_url=final_image,
                    organizacion_id=cand["org_id"],
                    activo=True,
                )
                db_insert.add(nuevo_evento)
                nuevos_eventos.append(nuevo_evento)
                eventos_bd.append({"fecha": fecha_evento, "nombre": nombre, "url_original": cand["url"]})
                events_added += 1
                logger.info("%s '%s' preparado para guardar.", prefijo, nombre)

        db_insert.commit()
        # Después del commit el ORM refresca los IDs autogenerados
        nuevos_ids = [ev.id for ev in nuevos_eventos if ev.id is not None]
    except Exception:
        db_insert.rollback()
        nuevos_ids = []
        raise
    finally:
        db_insert.close()

    return events_added, total_tokens, len(candidates), len(posts), nuevos_ids

# Procesamiento del bundle unificado
def process_bundle(client: OpenAI, phase_callback=None) -> tuple[int, bool, int, int, int, list[int]]:
    """
    Descarga y procesa el Bundle RSS.
    Devuelve (tokens_consumidos, rss_no_disponible, eventos_añadidos, posts_analizados, posts_encontrados, nuevos_ids).
    No requiere una sesión de BD — process_posts gestiona sus propias sesiones.
    """
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
                return 0, rss_no_disponible, 0, 0, 0, []
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
            return 0, rss_no_disponible, 0, 0, 0, []

    posts = feed_data.get("items", []) or feed_data.get("entries", [])
    logger.info("Se encontraron %d posts en el Bundle.", len(posts))

    events_added, total_tokens, posts_analizados, posts_encontrados, nuevos_ids = process_posts(
        posts, client, phase_callback=phase_callback
    )

    logger.info("Bundle procesado. Eventos nuevos: %d", events_added)
    return total_tokens, rss_no_disponible, events_added, posts_analizados, posts_encontrados, nuevos_ids


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
    total_eventos_añadidos = 0
    total_posts_analizados = 0
    total_posts_encontrados = 0
    total_nuevos_ids: list[int] = []
    errores: list[str] = []

    try:
        client = _get_nim_client()
    except RuntimeError as e:
        logger.error(str(e))
        return {"ok": False, "error": str(e), "tokens": 0, "rss_no_disponible": False}

    logger.info("\n--- Procesando Bundle unificado ---")
    try:
        tokens, _, ev_añadidos, posts_anal, posts_enc, nuevos_ids = process_bundle(
            client, phase_callback=phase_callback
        )
        total_tokens += tokens
        total_eventos_añadidos += ev_añadidos
        total_posts_analizados += posts_anal
        total_posts_encontrados += posts_enc
        total_nuevos_ids.extend(nuevos_ids)
    except Exception as e:
        msg = f"Error procesando bundle: {e}"
        logger.error(msg)
        errores.append(msg)

    if _RSS_PLAN_NO_PAGADO:
        logger.warning("RSS.app no disponible — plan no pagado. Se usaron datos locales de respaldo.")

    logger.info("\n=== ETL finalizado. Tokens totales: %d | Eventos añadidos: %d ===", total_tokens, total_eventos_añadidos)
    return {
        "ok": True,
        "tokens": total_tokens,
        "errores": errores,
        "rss_no_disponible": _RSS_PLAN_NO_PAGADO,
        "posts_encontrados": total_posts_encontrados,
        "posts_analizados": total_posts_analizados,
        "eventos_añadidos": total_eventos_añadidos,
        "nuevos_ids": total_nuevos_ids,
    }

if __name__ == "__main__":
    resultado = run_etl()
    if not resultado["ok"]:
        raise SystemExit(f"ETL falló: {resultado.get('error')}")