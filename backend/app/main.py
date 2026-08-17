import threading
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.config import settings
from app.core.limiter import limiter
from app.api.routes import api_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dashboard STEM Ciudad Juárez — API",
    description="Backend del Observatorio del Ecosistema STEM de Ciudad Juárez. Desarrollado para Frente Norte.",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# Registra el limiter y su manejador de error en la app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


def _etl_scheduled_job():
    """Función que dispara el ETL automático desde el scheduler."""
    from app.api.events import etl_runner
    if etl_runner.try_start():
        logger.info("ETL automático de lunes iniciado por el scheduler.")
        threading.Thread(target=etl_runner.run_etl_background, daemon=True).start()
    else:
        logger.info("ETL automático de lunes: ya había uno en ejecución, se omite.")


@app.on_event("startup")
def _startup():
    """Pre-carga el módulo ETL y activa el scheduler de lunes."""
    def _load():
        try:
            import scripts.etl_events  # noqa: F401
        except Exception as e:
            logger.warning("ETL preload failed: %s", e)
    threading.Thread(target=_load, daemon=True).start()

    # Ejecutar ETL automáticamente todos los lunes a las 08:00 hora de Ciudad Juárez (UTC-7)
    scheduler = BackgroundScheduler(timezone="America/Mazatlan")
    scheduler.add_job(
        _etl_scheduled_job,
        trigger=CronTrigger(day_of_week="mon", hour=8, minute=0),
        id="etl_semanal",
        replace_existing=True,
    )
    scheduler.start()
    
    msg = "Scheduler ETL activado: lunes 08:00 hora Juárez"
    print(f"INFO:     {msg}")
    logger.info(msg)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "proyecto": "Dashboard STEM Frente Norte", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
