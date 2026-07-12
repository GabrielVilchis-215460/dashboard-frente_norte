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

def extract_events_data(text_post: str, org_name: str) -> dict:
    date_today = date.today().isoformat()
    prompt = f"""
    Eres un analizador de datos experto. Analiza el siguiente texto extraído de las redes sociales de la organización '{org_name}'.
    La fecha actual del sistema es {date_today}.
    
    Tu tarea es determinar si el texto anuncia un evento, taller o actividad futura.
    Si es un evento, extrae los datos. Si usa fechas relativas ("este viernes"), calcúlala basándote en la fecha actual.
    
    Responde ÚNICAMENTE con un objeto JSON válido con la siguiente estructura:
    {{
        "es_evento": true/false,
        "nombre": "Nombre inferido del evento",
        "ubicacion": "Lugar mencionado (o null si no se menciona)",
        "fecha": "YYYY-MM-DD"
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
        return json.loads(response.text)
    except Exception as e:
        print(f"Error procesando post con Gemini: {e}")
        return {"is_event": False}
    
def process_feed_rss(org: Organizacion):
    print(f"Procesando organizacion: {org.nombre}")
    print(f"Descargando feed desde: {org.rss_url}")
    
    try:
        # descargo directamente el JSON diramente de internet
        response = requests.get(org.rss_url)
        response.raise_for_status()
        feed_data = response.json()
    except Exception as e:
        print(f"Error al descargar feed de la organizacion: {e}")
        return
    
    posts = feed_data.get('items', []) or feed_data.get('entries', [])
    print(f"Se encontraron {len(posts)} posts. Iniciando análisis...\n")

    db = SessionLocal()
    events_added = 0

    try:
        for i, post in enumerate(posts, 1):
            texto_post = post.get('content_text') or post.get('summary') or post.get('title', '')
            url_post = post.get('url', 'Sin URL disponible')

            if not texto_post.strip():
                continue

            print(f"[{i}/{len(posts)}] Analizando post...")

            datos = extract_events_data(texto_post, org.nombre)
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
                        url_original=datos["url_original"],
                        organizacion_id=org.id,
                        activo=True
                    )
                    db.add(nuevo_evento)
                    eventos_agregados += 1
                    print("  -> Evento preparado para guardar en BD.")
                else:
                    print("  -> El evento ya estaba registrado previamente.")
            else:
                print("  -> No es un evento.")
            
            # Pausa obligatoria para cuidar la cuota de la API
            time.sleep(4)

        # Confirmar todos los guardados en PostgreSQL
        db.commit()
        print(f"\nProceso terminado! Se insertaron {eventos_agregados} eventos nuevos en la base de datos.")

    except Exception as e:
        db.rollback()
        print(f"Ocurrió un error en la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("\n Iniciando extracción de eventos...")

    db_main = SessionLocal()

    try:
        orgs_with_feed = db_main.query(Organizacion).filter(Organizacion.rss_url.isnot(None)).all()

        if not orgs_with_feed:
            print("No hay organizaciones con 'rss_url' configurado en la base de datos.")
        else:
            print(f"Se encontraron {len(orgs_with_feed)} organizaviones con feeds activos \n")

        for org in orgs_with_feed:
            process_feed_rss(org)
            print("\n Pausa de seguridad (10s) para cuidar la cuota de la API...")
            time.sleep(10)
        
        print("\n Extracción finalizada con exito!")
    finally:
        db_main.close()