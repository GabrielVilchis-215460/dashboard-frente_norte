# Dashboard del Ecosistema STEM — Ciudad Juárez
Desarrollado para **Frente Norte** · Observatorio del Ecosistema STEM

## Estructura del repositorio

```
stem-dashboard/
├── backend/                   # FastAPI + PostgreSQL
│   ├── app/
│   │   ├── api/routers/       # organizaciones | programas | metricas
│   │   ├── core/              # config, settings
│   │   ├── db/                # session, Base
│   │   ├── models/            # Organizacion | Programa | Colonia
│   │   ├── schemas/           # Pydantic I/O + métricas
│   │   └── services/          # metricas_service (lógica del dashboard + ISE)
│   ├── scripts/
│   │   └── seed_from_csv.py   # Importa los CSVs reales a la BD
│   └── tests/
├── frontend/                  # React + Vite + TypeScript
│   └── src/
│       ├── components/
│       │   ├── layout/        # Sidebar (8 módulos)
│       │   ├── dashboard/     # KPI cards
│       │   ├── charts/        # Recharts wrappers
│       │   ├── map/           # Leaflet.js + pines
│       │   └── ui/            # Componentes reutilizables
│       ├── pages/             # Una página por módulo del PDF
│       ├── services/          # api.ts — toda comunicación con backend
│       └── types/             # index.ts — todos los tipos TS
├── data/
│   ├── raw/                   # CSVs originales de Frente Norte
│   ├── processed/             # CSVs limpios post-deduplicación
│   └── seeds/                 # JSON listos para importar
└── docs/                      # Diccionario de indicadores, metodología
```

## Módulos del Dashboard (según ficha técnica PDF)

| # | Módulo | Endpoint | Status |
|---|--------|----------|--------|
| 1 | Panorama General | `GET /api/v1/metricas/panorama` | 🟡 esqueleto |
| 2 | Perfil de Beneficiarios | `GET /api/v1/metricas/beneficiarios` | 🟡 esqueleto |
| 3 | Inclusión y Participación Femenina | `GET /api/v1/metricas/inclusion` | 🟡 esqueleto |
| 4 | Oferta STEM | `GET /api/v1/metricas/oferta` | 🟡 esqueleto |
| 5 | Madurez del Ecosistema | `GET /api/v1/metricas/madurez` | 🟡 esqueleto |
| 6 | Cobertura Territorial | `GET /api/v1/metricas/cobertura` | 🟡 esqueleto |
| 🗺 | Mapa Interactivo | `GET /api/v1/organizaciones/mapa` | 🟡 esqueleto |
| 💡 | Índice de Salud (ISE) | `GET /api/v1/metricas/indice-salud` | 🟡 esqueleto |

## Arranque local

```bash
# Backend
cd backend
cp .env.example .env        # llenar DATABASE_URL con Supabase
pip install -r requirements.txt
uvicorn app.main:app --reload
# → http://localhost:8000/docs

# Seed de datos
python -m scripts.seed_from_csv

# Frontend
cd frontend
cp .env.example .env
npm install
npm run dev
# → http://localhost:5173
```

## Datos disponibles

- `data/raw/encuesta.csv` — 7 organizaciones (encuesta Frente Norte, deduplicado)
- `data/raw/rodadora.csv` — 6 programas de La Rodadora Espacio Interactivo

**Pendiente de investigación documental:**
- Coordenadas (lat/lon) de cada organización
- Organizaciones no encuestadas: UACJ, CITA, CENALTEC, FABLab, TechHub, etc.
