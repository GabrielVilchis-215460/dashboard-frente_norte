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
    Para correr el script: 
        python -m scripts.etl_eventos

Frecuencia recomendada:
    Se recomienda correr una vez por semana, preferiblemente cada lunes.
"""

import json, time, requests
from datetime import date, datetime
from google import genai
from google.genai import types
from app.db.session import SessionLocal
from app.models.eventos import Evento 
from app.models.organizacion import Organizacion
from app.core.config import settings

api_key = settings.GEMINI_API_KEY
# Inicializo el cliente de Google Gemini
client = genai.Client(api_key=api_key)

def extract_events_data(text_post: str, org_name: str) -> tuple[dict, int]:
    date_today = date.today().isoformat()
    prompt = f"""
    Eres un analizador de datos experto. Analiza el siguiente texto extraído de las redes sociales de la organización '{org_name}'.
    La fecha actual del sistema es {date_today}.
    
    Tu tarea es determinar si el texto anuncia un evento, taller o actividad futura.
    
    REGLA 1: FILTRO DE AUTORÍA ORIGINAL (ANTI-REPOST)
    Analiza si este post es un "repost", "compartido" o una colaboración de un evento ajeno. 
    Si el texto indica claramente que el evento es organizado por OTRA entidad y '{org_name}' solo lo está promocionando/compartiendo, 
    debes marcar "es_evento": false. Solo acepta el evento si le pertenece legítimamente a '{org_name}' o si co-organizan activamente.
    
    REGLA 2: UBICACIÓN
    Solo debes considerar como evento válido (es_evento: true) si la actividad se llevará a cabo en Ciudad Juárez, Chihuahua, o si es un evento 100% ONLINE/VIRTUAL. 
    Si es presencial en otra ciudad, marca "es_evento": false.

    REGLA 3: CATEGORIZACIÓN ESTRICTA (ENFOQUE Y TIPO DE EVENTOS)
    Asigna el 'enfoque' y el 'tipo' eligiendo ÚNICAMENTE UNA opción de las siguientes listas (la que mejor se asemeje al post):
    - Opciones de ENFOQUE permitidas: "Ciencia", "Tecnologia", "Ingenieria", "Matematicas", "Robotica", "Inteligencia artificial", "Medio ambiente", "Finanzas", "Emprendimiento".
    - Opciones de TIPO permitidas: "Talleres", "Cursos", "Campamento", "Bootcamp", "Conferencia", "Eventos".
    Si no logras deducirlo, puedes dejar el valor como null.
    
    Si es un evento válido, extrae los datos. Si usa fechas relativas ("este viernes"), calcúlala basándote en la fecha actual.
    
    REGLA 4: EXTRACCIÓN DE LA URL DE LA IMAGEN
    Analiza minuciosamente el texto del post adjunto en busca de cualquier enlace, etiqueta HTML (como <img src="...">) o URL directa que apunte a la imagen, flyer, banner o foto 
    promocional de este evento específico. Si encuentras dicha URL, extraela. Si no hay ninguna URL de imagen explícita en el texto, pon null.
    
    Responde ÚNICAMENTE con un objeto JSON válido con la siguiente estructura:
    {{
        "es_evento": true/false,
        "nombre": "Nombre inferido del evento",
        "ubicacion": "Lugar mencionado (o null si no se menciona)",
        "fecha": "YYYY-MM-DD",
        "enfoque": "Una de las opciones permitidas o null",
        "tipo": "Una de las opciones permitidas o null",
        "imagen_url": "URL completa de la imagen encontrada en el texto o null"
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
    
def process_feed_rss(org: Organizacion) -> int:
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

    db = SessionLocal()
    events_added = 0
    total_tokens = 0

    try:
        for i, post in enumerate(posts, 1):
            texto_post = post.get('content_text') or post.get('summary') or post.get('title', '')
            url_post = post.get('url', 'Sin URL disponible')
            media_attachments = post.get('attachments', [])
            imagen_url = None
            
            if media_attachments and isinstance(media_attachments, list):
                imagen_url = media_attachments[0].get('url')

            if not imagen_url:
                imagen_url = post.get('image') or post.get('thumbnail')
            
            if not texto_post.strip():
                continue

            print(f"[{i}/{len(posts)}] Analizando post...")

            datos, tokens_post = extract_events_data(texto_post, org.nombre)
            total_tokens += tokens_post
            datos["url_original"] = url_post

            print("  -> Respuesta JSON cruda de Gemini:")
            print(json.dumps(datos, indent=4, ensure_ascii=False))
            
            if datos.get("es_evento"):
                print(f"  -> ¡EVENTO DETECTADO!: {datos.get('nombre')}")

                datos.pop("es_evento", None)
                
                try:
                    # Convertir el string YYYY-MM-DD a un objeto Date de Python
                    fecha_evento = datetime.strptime(datos["fecha"], "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    print(f"  -> Fecha inválida devuelta por la IA: {datos.get('fecha')}")
                    time.sleep(4)
                    continue

                imagen_final = datos.get("imagen_url")
                if not imagen_final:
                    media_attachments = post.get('attachments', [])

                    if media_attachments and isinstance(media_attachments, list):
                        imagen_final = media_attachments[0].get('url')

                    if not imagen_final:
                        imagen_final = post.get('image') or post.get('thumbnail')

                # Evitar duplicados consultando si ya existe en la BD
                evento_existente = db.query(Evento).filter(
                    Evento.nombre == datos["nombre"],
                    Evento.organizacion_id == org.id,
                    Evento.fecha == fecha_evento
                ).first()

                if not evento_existente:
                    # Crear la instancia del modelo SQLAlchemy
                    nuevo_evento = Evento(
                        nombre=datos["nombre"],
                        ubicacion=datos["ubicacion"],
                        fecha=fecha_evento,
                        enfoque=datos.get("enfoque"),
                        tipo=datos.get("tipo"),
                        url_original=datos["url_original"],
                        imagen_url=imagen_final,
                        organizacion_id=org.id,
                        activo=True
                    )
                    db.add(nuevo_evento)
                    events_added += 1
                    print("  -> Evento preparado para guardar en BD.")
                else:
                    print("  -> El evento ya estaba registrado previamente.")
            else:
                print("  -> No es un evento.")
            
            # Pausa obligatoria para cuidar la cuota de la API
            time.sleep(4)

        db.commit()
        print(f"\nProceso terminado! Se insertaron {events_added} eventos nuevos en la base de datos.")
        return total_tokens

    except Exception as e:
        db.rollback()
        print(f"Ocurrió un error en la base de datos: {e}")
        return total_tokens
    finally:
        db.close()

if __name__ == "__main__":
    print("\n Iniciando extracción de eventos...")

    total_tokens_consumed = 0

    db_main = SessionLocal()

    try:
        orgs_with_feed = db_main.query(Organizacion).filter(Organizacion.rss_url.isnot(None)).all()

        if not orgs_with_feed:
            print("No hay organizaciones con 'rss_url' configurado en la base de datos.")
        else:
            print(f"Se encontraron {len(orgs_with_feed)} organizaciones con feeds activos \n")

        for org in orgs_with_feed:
            tokens_org = process_feed_rss(org)
            total_tokens_consumed += tokens_org 
            time.sleep(10)
        
        print("\n Extracción finalizada con exito!")
        print(f"Total de tokens consumidos: {total_tokens_consumed}")
    finally:
        db_main.close()