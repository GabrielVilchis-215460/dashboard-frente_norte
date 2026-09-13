import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.health_index.schemas import EcosistemaResponse, IndiceSaludResponse
from app.api.health_index.service import calcular_brechas, get_indice
from app.models.ecosistema import Ecosistema
from app.models.indicadores import Indicador
from app.models.benchmark_valores import BenchmarkValor
from sqlalchemy import text

router = APIRouter(prefix="/indice_salud", tags=["Indice de Salud del Ecosistema"])

logger = logging.getLogger("stem_api.indice_salud")

@router.get("", response_model=IndiceSaludResponse)
def get_indice_salud(db: Session = Depends(get_db)):
    """
    Endpoint principal que obtiene los KPIs, evolución y benchmark 
    para el ecosistema Ciudad Juárez de forma automática.
    """
    return get_indice(db=db)

@router.get("/{ecosistema_id}/brechas", response_model=EcosistemaResponse)
def obtener_brechas(db: Session = Depends(get_db)):
    """
    Endpoint para consultar las brechas y fortalezas del ecosistema STEM 
    comparado con sus referentes.
    """
    return calcular_brechas(db=db)

@router.post("/seed-test-data")
def poblar_datos_sinteticos(db: Session = Depends(get_db)):
    """
    Carga los ecosistemas faltantes (Guadalajara, Tijuana, Monterrey y Ciudad Juárez) 
    y sus valores de benchmark para 2026, reutilizando los indicadores existentes sin alterarlos[cite: 1].
    """
    # 1. Definir los ecosistemas requeridos (locales, referentes y pares)
    ecosistemas_data = [
        {"nombre": "Ciudad Juárez", "rol": "local"},
        {"nombre": "Monterrey", "rol": "referente"},
        {"nombre": "Guadalajara", "rol": "referente"},
        {"nombre": "Tijuana", "rol": "par"}
    ]
    
    ecosistemas_objs = {}
    for eco_info in ecosistemas_data:
        eco = db.query(Ecosistema).filter(Ecosistema.nombre == eco_info["nombre"]).first()
        if not eco:
            eco = Ecosistema(nombre=eco_info["nombre"], rol=eco_info["rol"])
            db.add(eco)
            db.commit()
            db.refresh(eco)
        ecosistemas_objs[eco_info["nombre"]] = eco

    # 2. Obtener los indicadores existentes (no se crean ni alteran)
    claves_indicadores = ["egresados_stem", "mujeres_stem", "empleo_stem", "salario_stem", "centros_investigacion"]
    indicadores_objs = {}
    for clave in claves_indicadores:
        ind = db.query(Indicador).filter(Indicador.clave == clave).first()
        if not ind:
            raise HTTPException(
                status_code=400, 
                detail=f"Falta el indicador con clave '{clave}' en la base de datos. Asegúrate de crearlos previamente[cite: 1]."
            )
        indicadores_objs[clave] = ind

    # 3. Asignar valores de benchmark para cada ecosistema en el año 2026
    valores_prueba = [
        # Ciudad Juárez
        {"ecosistema": "Ciudad Juárez", "indicador_clave": "egresados_stem", "valor": 34.0},
        {"ecosistema": "Ciudad Juárez", "indicador_clave": "mujeres_stem", "valor": 28.0},
        {"ecosistema": "Ciudad Juárez", "indicador_clave": "empleo_stem", "valor": 43.0},
        {"ecosistema": "Ciudad Juárez", "indicador_clave": "salario_stem", "valor": 24000.0},
        {"ecosistema": "Ciudad Juárez", "indicador_clave": "centros_investigacion", "valor": 1.6},
        
        # Monterrey
        {"ecosistema": "Monterrey", "indicador_clave": "egresados_stem", "valor": 45.0},
        {"ecosistema": "Monterrey", "indicador_clave": "mujeres_stem", "valor": 42.0},
        {"ecosistema": "Monterrey", "indicador_clave": "empleo_stem", "valor": 38.0},
        {"ecosistema": "Monterrey", "indicador_clave": "salario_stem", "valor": 32000.0},
        {"ecosistema": "Monterrey", "indicador_clave": "centros_investigacion", "valor": 3.5},

        # Guadalajara
        {"ecosistema": "Guadalajara", "indicador_clave": "egresados_stem", "valor": 42.0},
        {"ecosistema": "Guadalajara", "indicador_clave": "mujeres_stem", "valor": 40.0},
        {"ecosistema": "Guadalajara", "indicador_clave": "empleo_stem", "valor": 40.0},
        {"ecosistema": "Guadalajara", "indicador_clave": "salario_stem", "valor": 30000.0},
        {"ecosistema": "Guadalajara", "indicador_clave": "centros_investigacion", "valor": 3.0},

        # Tijuana
        {"ecosistema": "Tijuana", "indicador_clave": "egresados_stem", "valor": 30.0},
        {"ecosistema": "Tijuana", "indicador_clave": "mujeres_stem", "valor": 25.0},
        {"ecosistema": "Tijuana", "indicador_clave": "empleo_stem", "valor": 35.0},
        {"ecosistema": "Tijuana", "indicador_clave": "salario_stem", "valor": 21000.0},
        {"ecosistema": "Tijuana", "indicador_clave": "centros_investigacion", "valor": 1.2},
    ]

    for item in valores_prueba:
        eco_obj = ecosistemas_objs[item["ecosistema"]]
        ind_obj = indicadores_objs[item["indicador_clave"]]
        
        existe = db.query(BenchmarkValor).filter(
            BenchmarkValor.ecosistema_id == eco_obj.id,
            BenchmarkValor.indicador_id == ind_obj.id,
            BenchmarkValor.anio == 2026
        ).first()

        if not existe:
            val = BenchmarkValor(
                ecosistema_id=eco_obj.id,
                indicador_id=ind_obj.id,
                anio=2026,
                valor=item["valor"]
            )
            db.add(val)

    db.commit()

    return {
        "mensaje": "Ciudades y benchmarks agregados correctamente, respetando los indicadores existentes."
    }

@router.delete("/seed-test-data")
def limpiar_datos_sinteticos(db: Session = Depends(get_db)):
    """
    Elimina los ecosistemas y sus benchmarks, y reinicia los contadores 
    de ID de ambas tablas a 1, conservando intactos los indicadores[cite: 1, 2, 3].
    """
    try:
        # TRUNCATE con CASCADE limpia las tablas y RESTART IDENTITY reinicia los IDs a 1.
        # Respetamos la tabla 'indicadores' para que no sea tocada.
        db.execute(text("TRUNCATE TABLE benchmark_valores, ecosistemas RESTART IDENTITY CASCADE;"))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al limpiar y reiniciar IDs: {str(e)}")

    return {
        "mensaje": "¡Datos depurados con éxito y contadores de ID reiniciados a 1!"
    }