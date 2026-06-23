# queda pendiente docstrings

# Constantes para la geolocalizacion para Nominatim y OpenStreetMap
NOMINATIM_USER_AGENT = "stem-dashboard-cj/1.0 (contacto: frentenorte.org)"
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"
GEOCODING_DELAY_SECONDS = 1.1  # Margen sobre el límite de 1 req/s de Nominatim

# Normalizacion de los rangos de porcentaje de participacion femenina
PCT_MUJERES_RANGOS: dict[str, tuple[str, float]] = {
    # Formato canónico (rango_normalizado, valor_medio)
    "0-25":    ("0-25",  12.5),
    "26-50":   ("26-50", 37.5),
    "51-75":   ("51-75", 62.5),
    "76-100":  ("76-100", 88.0),
    # Variantes con em-dash y porcentaje (formato original de Google Forms)
    "0–25%":   ("0-25",  12.5),
    "26–50%":  ("26-50", 37.5),
    "51–75%":  ("51-75", 62.5),
    "76–100%": ("76-100", 88.0),
    # Variantes sin porcentaje
    "0–25":   ("0-25",  12.5),
    "26–50":  ("26-50", 37.5),
    "51–75":  ("51-75", 62.5),
    "76–100": ("76-100", 88.0),
    # Variantes con guión normal
    "0-25%":   ("0-25",  12.5),
    "26-50%":  ("26-50", 37.5),
    "51-75%":  ("51-75", 62.5),
    "76-100%": ("76-100", 88.0),
}

# Valor medio cuando el rango no está en el catálogo (default 26-50%)
PCT_MUJERES_DEFAULT_MID = 37.5

# Normalizacion del volumen semestral de la encuesta

VOLUMEN_SEMESTRAL_MIDS: dict[str, int] = {
    # Rodadora.csv (guión con espacios)
    "1 - 50":    25,
    "51 - 200":  125,
    "201 - 500": 350,
    "501 - 1000": 750,
    "Más de 1000": 1500,
    # Datos de la encuesta (em-dash, sin espacios)
    "1–50":    25,
    "51–200":  125,
    "201–500": 350,
    "501–1000": 750,
    # Variantes con texto adicional
    "Más de 1,000 personas.": 1500,
    "Más de 1000 personas":   1500,
}

# Indicador de salud del ecosistema STEM (ISE)
# Pesos que requieren los campos o paramatros requeridos. En conjunto, deben sumar exactamente 1.0

# Fórmula: ISE = Cobertura territorial×0.25 + Diversidad de oferta STEM×0.20 + Inclusion femenina ×0.20 + Alcance de beneficiarios×0.20 + Madurez de programas×0.15
ISE_PESOS: dict[str, float] = {
    "cobertura":  0.25,
    "diversidad": 0.20,
    "inclusion":  0.20,
    "alcance":    0.20,
    "madurez":    0.15,
}

# Referencias para normalizar cada dimensión a escala 0-100
TOTAL_COLONIAS_JUAREZ = 600  
TOTAL_AREAS_STEM = 8           # Áreas STEM posibles en el ecosistema
META_BENEFICIARIOS_SEMESTRE = 5_000  

# Umbrales para determinar el nivel del ISE
ISE_UMBRALES: list[tuple[float, str]] = [
    (75.0, "EXCELENTE"),
    (50.0, "BUENO"),
    (25.0, "EN_DESARROLLO"),
    (0.0,  "CRITICO"),
]

# Cobertura territorial
# Umbrales para clasificar el nivel de oferta de una colonia
COBERTURA_NIVEL_ALTO  = 3 # >= 3 programas -> Alto
COBERTURA_NIVEL_MEDIO = 2  # == 2 programas -> Medio
# < 2 programas -> Bajo (default)

# Placeholders de valores nulos del CSV que deben ser None
# Algunas celdas tienen "." como valor de relleno en Google Forms.
CSV_NULL_PLACEHOLDERS = {".", "N/A", "n/a", "NA", "Sin datos", ""}

# Madurez de programas 
# Orden numérico para calcular la madurez "máxima" de una organización
MADUREZ_ORDEN: dict[str, int] = {
    "Escalamiento":   3,
    "Implementación": 2,
    "Exploración":    1,
}

# Direcciones de las instituciones para el archivo seed/ETL
DATOS_GEOGRAFICOS_INSTITUCIONES = {
    "SE SIPINNA Estatal": {
        "direccion": "Bustamante #2504, Altavista, 31200 Chihuahua, Chih., Mexico",
        "latitud": 28.6529623,
        "longitud": -106.081874,
        "sitio_web": "https://sipinna.chihuahua.gob.mx/"
    },
    "PAUTA": {
        "direccion": None,
        "latitud": None,
        "longitud": None,
        "sitio_web": "https://pauta.org.mx"
    },
    "CENTRO DE ESTUDIOS INDUSTRIA 4.0": {
        "direccion": "Plaza Oscared, Av. Tecnológico 5476-Int. 2, La Cuesta, 32650 Juárez, Chih., Mexico",
        "latitud": 31.6742947,
        "longitud": -106.4241559,
        "sitio_web": "http://www.roboed.mx/"
    },
    "Mech Robotix AC": {
        "direccion": "Avenida Antonio J. Bermúdez 770 Ote, Plaza Bermúdez, Local 13, Parque Ind Bermúdez, 32470 Juárez, Chih., Mexico",
        "latitud": 31.7247618,
        "longitud": -106.3932477,
        "sitio_web": "https://mechrobotix.wixsite.com/misitio"
    },
    "UNITED WAY CHIHUAHUA": {
        "direccion": "Boulevard Manuel Gómez Morín #9360 Edificio A local 2E Col, Partido Senecú, 32545 Juárez, Chih., Mexico",
        "latitud": 31.695404,
        "longitud": -106.3908233,
        "sitio_web": "http://www.uwchihuahua.org/"
    },
    "LA RODADORA ESPACIO INTERACTIVO": {
        "direccion": "Calle Jesús Soltero Lozoya y Blvd. Teófilo Borunda, Supermanzana Del Norte, Comunitario Jarudo, 32652 Juárez, Chih., Mexico",
        "latitud": 31.6901179,
        "longitud": -106.42815,
        "sitio_web": "http://www.larodadora.org/"
    },
    "Tecnológico de Monterrey": {
        "direccion": "Bulevar Tomás Fernández 8945, Parques Industriales, 32470 Juárez, Chih., Mexico",
        "latitud": 31.7160341,
        "longitud": -106.3951052,
        "sitio_web": "https://tec.mx/es/ciudad-juarez"
    }
}

# ETL
# Nombre del bucket de Supabase Storage donde se guardan los CSVs
SUPABASE_BUCKET_STEM_DATA = "stem-data"
