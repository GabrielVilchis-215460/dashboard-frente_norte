from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import organizaciones, programas, metricas

app = FastAPI(
    title="Dashboard STEM Ciudad Juárez — API",
    description="Backend del Observatorio del Ecosistema STEM de Ciudad Juárez. Desarrollado para Frente Norte.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(organizaciones.router, prefix="/api/v1")
app.include_router(programas.router,      prefix="/api/v1")
app.include_router(metricas.router,       prefix="/api/v1")


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "proyecto": "Dashboard STEM CJ", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
