from fastapi import APIRouter
from app.api.overview.routes import router as panorama_router
from app.api.beneficiary_profile.routes import router as beneficiarios_router
from app.api.woman_inclusion.routes import router as inclusion_router
from app.api.STEM_offerings.routes import router as ofertas_router
from app.api.ecosystem_maturity.routes import router as madurez_router
from app.api.territorial_coverage.routes import router as cobertura_router
# from app.api.ecosystem_map.routes import router as mapa_router
from app.api.health_index.routes import router as indice_router
from app.api.admin_panel.routes import router as admin_router
from app.api.auth.routes import router as auth_router

api_router = APIRouter(prefix="/api")

# ── Autenticación (público) ────────────────────────────────────────────────────
api_router.include_router(auth_router)

# ── Módulos de métricas (públicos, solo lectura) ───────────────────────────────
api_router.include_router(panorama_router)
api_router.include_router(beneficiarios_router)
api_router.include_router(inclusion_router)
api_router.include_router(ofertas_router)
api_router.include_router(madurez_router)
api_router.include_router(cobertura_router)
# api_router.include_router(mapa_router)
api_router.include_router(indice_router)

# ── Panel de administración (requiere JWT) ─────────────────────────────────────
api_router.include_router(admin_router)