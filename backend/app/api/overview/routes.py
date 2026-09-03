import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.overview.schemas import PanoramaGeneral
from app.api.overview.service import get_panorama

logger = logging.getLogger("stem_api.panorama_general")

router = APIRouter(prefix="/panorama_general", tags=["Panorama General"])

@router.get(
    "/",
    response_model=PanoramaGeneral,
    status_code=status.HTTP_200_OK,
    summary="Obtener indicadores generales del ecosistema STEM",
    description="""
Este endpoint de acceso público expone de manera consolidada los **indicadores clave de rendimiento (KPIs)**, métricas de impacto y resúmenes geoespaciales del ecosistema STEM de Ciudad Juárez.

### ¿Qué alimenta este endpoint?
Alimenta directamente el **Módulo 1 — Panorama General** del dashboard principal, permitiendo visualizar los siguientes datos: 
* **Volumen e impacto del ecosistema:** Total de organizaciones, programas activos y una estimación de beneficiarios semestrales.
* **Inclusión y enfoque del ecosistema:** Porcentaje global de participación femenina y proporción de programas con enfoque transversal/integral.
* **Distribución sectorial y temática del ecosistema:** Clasificación de organizaciones por tipo y conteo de disciplinas STEM representadas.
* **Liderazgo territorial del ecosistema:** Top de instituciones con mayor número de programas y un preview geolocalizado de hasta 15 pines prioritarios con sus logotipos institucionales.

    """,
    responses={
        200: {
            "description": "Indicadores del ecosistema calculados y devueltos exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "total_organizaciones": 45,
                        "total_programas_activos": 120,
                        "beneficiarios_semestre": 15400,
                        "colonias_impactadas": 32,
                        "pct_mujeres_beneficiarias": 48.5,
                        "pct_programas_enfoque_integral": 22.0,
                        "organizaciones_por_tipo": {
                            "Institución Educativa": 15,
                            "OSC / Sociedad Civil": 20
                        },
                        "areas_stem_representadas": {
                            "Tecnología": 35,
                            "Ciencia": 28
                        },
                        "top_organizaciones": [
                            {
                                "nombre": "Universidad Tecnológica Paso del Norte (UTPN)",
                                "total_programas": 12
                            }
                        ],
                        "preview_mapa": [
                            {
                                "id": 8,
                                "nombre": "CIITA Chihuahua IPN",
                                "latitud": 31.7150,
                                "longitud": -106.4245,
                                "logo_url": "https://example.com/logo.png",
                                "total_programas": 5
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor al procesar la consulta o calcular las métricas."
        },
    },
)
def panorama(db: Session = Depends(get_db)) -> PanoramaGeneral:
    """
    Calcula y retorna los KPIs globales del ecosistema STEM consultando
    organizaciones y programas vigentes en la base de datos.
    """
    try:
        return get_panorama(db)
    except Exception as exc:
        logger.error("Error en /metricas/panorama: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al calcular el panorama general."
        )