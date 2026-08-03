import threading
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.limiter import limiter
from app.api.routes import api_router

app = FastAPI(
    title="Dashboard STEM Ciudad Juárez — API",
    description="Backend del Observatorio del Ecosistema STEM de Ciudad Juárez. Desarrollado para Frente Norte.",
    version="1.0.0",
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


@app.on_event("startup")
def _preload_etl():
    """Pre-carga el módulo ETL en background para que la primera ejecución sea inmediata."""
    def _load():
        try:
            import scripts.etl_events  # noqa: F401
        except Exception:
            pass
    threading.Thread(target=_load, daemon=True).start()


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "proyecto": "Dashboard STEM Frente Norte", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
