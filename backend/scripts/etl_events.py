"""
Script ETL (Extract, Transform, Load) para la automatización de eventos.

Descripción:
    Este script se conecta de manera dinámica a la base de datos de PostgreSQL (Supabase por el momento)
    para obtener las organizaciones que tienen un feed de RSS (proveniente de RSS.app) configurado.
    Descarga el contenido JSON de cada feed, procesa los posts utilizando el modelo de IA 
    'gemini-3.1-flash-lite' para determinar si anuncian un evento futuro y, de ser así, 
    extrae de forma estructurada sus datos (nombre, ubicación, fecha y URL original) 
    para finalmente insertarlos de forma segura (evitando duplicados) en la base de datos.

Instrucciones de uso:
    Para correr el script, primero se deberá estar en la carpeta de backend y al mismo nivel del directorio, correr sl siguiente comando: 
        python -m scripts.etl_events

Frecuencia recomendada:
    Se recomienda correr una vez por semana, preferiblemente cada lunes.
"""

import json, time, requests, os
from datetime import date, datetime
from google import genai
from google.genai import types
from app.db.session import SessionLocal
from app.models.eventos import Evento 
from app.models.organizacion import Organizacion
from app.core.config import settings
from sqlalchemy import or_
from difflib import SequenceMatcher

api_key = settings.GEMINI_API_KEY
# Inicializo el cliente de Google Gemini
client = genai.Client(api_key=api_key)

# consatnte temporal del bundle con orgs de rss
BUNDLE_URL = "https://rss.app/feeds/v1.1/_e96R3DNd6AgEXOm1.json"
FALLBACK_JSON_PATH = os.path.join("data", "raw", "stem_ecosystem.json") # Ruta del bundle de las orgs rss

def extract_events_data(text_post: str, org_name: str) -> tuple[dict, int]:
    date_today = date.today().isoformat()
    prompt = f"""
    Eres un analizador de datos experto. Analiza el siguiente texto extraído de las redes sociales de la organización '{org_name}'.
    La fecha actual del sistema es {date_today}.
    
    Tu tarea es determinar si el texto anuncia un evento, taller o actividad futura.
    
    REGLA 1: FILTRO DE AUTORÍA ORIGINAL (ANTI-REPOST)
    Analiza si este post es un "repost", "compartido" o una colaboración de un evento ajeno. 
    Si el texto indica claramente que el evento es organizado por OTRA entidad, marca "es_evento": false.
    
    REGLA 2: UBICACIÓN
    Solo considera como válido (es_evento: true) si es en Ciudad Juárez, Chihuahua, o 100% ONLINE/VIRTUAL.
    
    REGLA 3: CATEGORIZACIÓN
    - ENFOQUE permitidas: "Ciencia", "Tecnologia", "Ingenieria", "Matematicas", "Robotica", "Inteligencia artificial", "Medio ambiente", "Finanzas", "Emprendimiento".
    - TIPO permitidas: "Talleres", "Cursos", "Campamento", "Bootcamp", "Conferencia", "Eventos".
    
    REGLA 4: FECHAS Y HORARIOS (MUY IMPORTANTE)
    - Si el evento dura un solo día, "fecha" es ese día y "fecha_fin" es null.
    - Si el texto menciona un RANGO de fechas (ej. 'del 11 de julio al 15 de agosto'), pon el inicio en "fecha" y el final en "fecha_fin". Ambas en formato "YYYY-MM-DD".
    - Extrae la "hora_inicio" y "hora_fin" si se mencionan. Deben estar estrictamente en formato militar "HH:MM" (ej. "14:30"). Si no se mencionan, pon null.
    
    REGLA 5: IMAGEN
    Extrae la URL de la imagen promocional si existe explícitamente en el texto, si no, null.
    
    Responde ÚNICAMENTE con un objeto JSON válido:
    {{
        "es_evento": true/false,
        "nombre": "Nombre inferido",
        "ubicacion": "Lugar mencionado",
        "fecha": "YYYY-MM-DD",
        "fecha_fin": "YYYY-MM-DD o null",
        "hora_inicio": "HH:MM o null",
        "hora_fin": "HH:MM o null",
        "enfoque": "Opcion permitida",
        "tipo": "Opcion permitida",
        "imagen_url": "URL o null"
    }}
    
    Texto del post:
    "{text_post}"
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        tokens_used = 0
        usage = response.usage_metadata

        if usage:
            print(f"  [Tokens] Entrada: {usage.prompt_token_count} | Salida: {usage.candidates_token_count} | Total: {usage.total_token_count}")
            tokens_used = usage.total_token_count

        return json.loads(response.text), tokens_used
    
    except Exception as e:
        print(f"Error procesando post con Gemini: {e}")
        return {"es_evento": False}, 0

# Funcion auxiliar
def get_org_from_post(post: dict, db, org: Organizacion = None):
    if org:
        return org.nombre, org.id
    
    # Todo este bloque funciona SOLO para el procesamiento de los bundles
    authors = post.get('authors', [])
    if authors and isinstance(authors, list):
        author_name = authors[0].get('name')
        if author_name:
            org_db = db.query(Organizacion).filter(
                or_(Organizacion.nombre == author_name, Organizacion.rss_alias == author_name),
                Organizacion.activo == True
            ).first()
            
            if org_db:
                return org_db.nombre, org_db.id
            else:
                return author_name, None
                
    return "Organizacion Desconocida", None

# Esta funcion contiene toda la logica para extrear los eventos
def process_posts(posts: list, db, org: Organizacion = None):
    events_added = 0
    total_tokens = 0

    for i, post in enumerate(posts, 1):
        text_post = post.get('content_text') or post.get('summary') or post.get('title', '')
        url_post = post.get('url', 'Sin URL disponible')
        media_attachments = post.get('attachments', [])

        org_name, org_id = get_org_from_post(post, db, org)

        if not org_id:
            print(f"[{i}/{len(posts)}] Saltando post: Organizacion '{org_name}' no se encuentra activa en la BD.")
            continue

        image_url = None
        if media_attachments and isinstance(media_attachments, list):
            image_url = media_attachments[0].get('url')

        if not image_url:
            image_url = post.get('image') or post.get('thumbnail')
        
        if not text_post.strip():
            continue

        print(f"[{i}/{len(posts)}] Analizando post para '{org_name}'...")

        datos, tokens_post = extract_events_data(text_post, org_name)
        total_tokens += tokens_post
        datos["url_original"] = url_post

        print("  -> Respuesta JSON cruda de Gemini:")
        print(json.dumps(datos, indent=4, ensure_ascii=False))

        if datos.get("es_evento"):
            print(f"  -> EVENTO DETECTADO: {datos.get('nombre')}")
            datos.pop("es_evento", None)
            
            try:
                # Convertir el string YYYY-MM-DD a un objeto Date de Python
                fecha_evento = datetime.strptime(datos["fecha"], "%Y-%m-%d").date()
                
                # Procesar variables nuevas en inglés (con soporte para nulos)
                end_date = None
                if datos.get("fecha_fin"):
                    end_date = datetime.strptime(datos["fecha_fin"], "%Y-%m-%d").date()
                
                start_time = None
                if datos.get("hora_inicio"):
                    start_time = datetime.strptime(datos["hora_inicio"], "%H:%M").time()
                    
                end_time = None
                if datos.get("hora_fin"):
                    end_time = datetime.strptime(datos["hora_fin"], "%H:%M").time()

            except (ValueError, TypeError) as e:
                print(f"  -> Formato de fecha u hora inválido devuelto por la IA: {e}")
                time.sleep(4)
                continue

            final_image = datos.get("imagen_url") or image_url

            #evento_existente = db.query(Evento).filter(
            #    Evento.nombre == datos["nombre"],
            #    Evento.organizacion_id == org_id,
            #    Evento.fecha == fecha_evento
            #).first()
            eventos_mismo_dia = db.query(Evento).filter(
                Evento.organizacion_id == org_id,
                Evento.fecha == fecha_evento
            ).all()

            es_duplicado = False
            for ev in eventos_mismo_dia:
                nombre_bd = ev.nombre.lower()
                nombre_nuevo = datos["nombre"].lower()
                
                # Compara qué tanto se parecen los textos
                similitud = SequenceMatcher(None, nombre_bd, nombre_nuevo).ratio()
                
                if similitud > 0.65 or nombre_bd in nombre_nuevo or nombre_nuevo in nombre_bd:
                    es_duplicado = True
                    break

            if not es_duplicado:
                nuevo_evento = Evento(
                    nombre=datos["nombre"],
                    ubicacion=datos["ubicacion"],
                    fecha=fecha_evento,
                    fecha_fin=end_date,          
                    hora_inicio=start_time,      
                    hora_fin=end_time,          
                    enfoque=datos.get("enfoque"),
                    tipo=datos.get("tipo"),
                    url_original=datos["url_original"],
                    imagen_url=final_image,
                    organizacion_id=org_id,
                    activo=True
                )
                db.add(nuevo_evento)
                events_added += 1
                print("  -> Evento preparado para guardar en BD.")
            else:
                print("  -> El evento ya estaba registrado previamente.")
        else:
            print("  -> No es un evento.")
        
        time.sleep(4)

    return events_added, total_tokens
    
# Esta funcion solo funciona con las columnas de rss_url de la tabla de las organizaciones
def process_feed_rss(org: Organizacion, db) -> int:
    print(f"\nProcesando organizacion: {org.nombre}")
    print(f"Descargando feed desde: {org.rss_url}")
    
    try:
        # descargo directamente el JSON diramente de internet
        response = requests.get(org.rss_url)
        response.raise_for_status()
        feed_data = response.json()

    except Exception as e:
        print(f"Error al descargar feed de la organizacion: {e}")
        return 0
    
    posts = feed_data.get('items', []) or feed_data.get('entries', [])
    print(f"Se encontraron {len(posts)} posts. Iniciando análisis...\n")

    events_added, total_tokens = process_posts(posts, db, org)
    db.commit()

    print(f"\nProceso terminado para {org.nombre}! Se insertaron {events_added} eventos nuevos.")
    return total_tokens

# Esta funcion solo funciona con los bundles con orgs de RSS
def process_bundle(db):
    print(f"\nIniciando procesamiento de Bundle mediante URL...")
    feed_data = None

    # primero trata de acceder mediante un request al url
    try:
        print(f"Intentando descargar Bundle en linea desde: {BUNDLE_URL}")
        response = requests.get(BUNDLE_URL, timeout=10)
        response.raise_for_status()
        feed_data = response.json()
        print("Bundle descargado correctamente desde internet.")
    # si no puede acceder, entonces tomara en cuenta el json que esta en el directorio del proyecto
    # NOTA: dicho bundle se deberá actualizar cada lunes tambien
    except Exception as e:
        print(f"No se pudo acceder al Bundle en linea ({e}). Iniciando Fallback local...")
        if os.path.exists(FALLBACK_JSON_PATH):
            print(f"Cargando archivo local de respaldo: {FALLBACK_JSON_PATH}")
            with open(FALLBACK_JSON_PATH, "r", encoding="utf-8") as file:
                feed_data = json.load(file)
        else:
            print(f"Error critico: Tampoco se encontro el archivo local en {FALLBACK_JSON_PATH}")
            return 0
        
    if feed_data:
        posts = feed_data.get('items', []) or feed_data.get('entries', [])
        print(f"Se encontraron {len(posts)} posts en el Bundle. Iniciando analisis...\n")
        
        events_added, total_tokens = process_posts(posts, db, org=None)
        db.commit()

        print(f"\nProceso del Bundle terminado! Se insertaron {events_added} eventos nuevos.")
        return total_tokens
    
    return 0

if __name__ == "__main__":
    print("\n Iniciando extracción de eventos...")

    total_tokens_consumed = 0

    db_main = SessionLocal()

    try:
        # primero procesa orgs en la BD
        orgs_with_feed = db_main.query(Organizacion).filter(Organizacion.rss_url.isnot(None)).all()

        if not orgs_with_feed:
            print("No hay organizaciones con 'rss_url' configurado en la base de datos.")
        else:
            print(f"\n--- FASE 1: Procesando {len(orgs_with_feed)} feeds individuales ---")
            for org in orgs_with_feed:
                tokens_org = process_feed_rss(org, db_main)
                total_tokens_consumed += tokens_org 
                time.sleep(10)
        # luego procesa los bundles
        print("\n--- FASE 2: Procesando Bundle Unificado ---")
        tokens_bundle = process_bundle(db_main)
        total_tokens_consumed += tokens_bundle
        
        print("\n Extracción finalizada con exito!")
        print(f" Total de tokens consumidos (Fase 1 + Fase 2): {total_tokens_consumed}")
    except Exception as e:
        db_main.rollback()
        print(f"Ocurrio un error critico en la ejecucion general: {e}")
    finally:
        db_main.close()