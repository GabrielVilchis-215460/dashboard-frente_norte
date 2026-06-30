# Dashboard del Ecosistema STEM — Ciudad Juárez
Developed for **Frente Norte / FICOSEC** · STEM Ecosystem Observatory

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite |
| Styling | CSS Modules · Glassmorphism design system (3 themes) |
| State | Zustand · custom `useApi` hook |
| Maps | Leaflet.js + leaflet.heat |
| Charts | Recharts |
| Backend | FastAPI + SQLAlchemy 2.0 |
| Database | PostgreSQL (Supabase) |
| Auth | JWT (HTTPBearer) + bcrypt · slowapi rate limiting |

---

## Repository Structure

```
dashboard-frente_norte/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── admin_panel/        # CRUD orgs & programs (protected)
│   │   │   ├── auth/               # JWT login
│   │   │   ├── overview/           # Panorama General
│   │   │   ├── beneficiary_profile/
│   │   │   ├── woman_inclusion/
│   │   │   ├── STEM_offerings/
│   │   │   ├── ecosystem_maturity/
│   │   │   ├── territorial_coverage/
│   │   │   ├── ecosystem_map/
│   │   │   ├── health_index/       # ISE
│   │   │   └── export/             # Excel / PDF export
│   │   ├── core/                   # config, security, rate limiter
│   │   ├── db/                     # session, Base
│   │   ├── models/                 # Organizacion | Programa
│   │   └── utils/                  # constants, helpers
│   ├── scripts/
│   │   └── etl_seed.py             # ETL — seeds DB from CSV data
│   └── requirements.txt
└── frontend/
    └── src/
        ├── components/
        │   ├── layout/             # AppLayout, Sidebar, PageHeader
        │   ├── dashboard/          # KPICard
        │   ├── charts/             # DonutChart, HorizontalBarChart, CenterDonut
        │   └── ui/                 # Card, Badge, Skeleton
        ├── pages/
        │   ├── Overview/           # Panorama General + mini map
        │   ├── Beneficiaries/      # Perfil de Beneficiarios
        │   ├── Inclusion/          # Inclusión y Participación Femenina
        │   ├── STEMOffer/          # Oferta STEM
        │   ├── Maturity/           # Madurez del Ecosistema
        │   ├── Health/             # Índice de Salud del Ecosistema (ISE)
        │   ├── Map/                # Mapa Interactivo (pines + heatmap)
        │   └── Admin/              # Panel de administración (protegido)
        ├── services/
        │   ├── api.ts              # Public API client (Axios)
        │   └── adminApi.ts         # Admin API client (Axios + JWT interceptors)
        ├── store/                  # Zustand global store
        ├── hooks/                  # useApi
        ├── types/                  # TypeScript types
        └── utils/                  # format helpers
```

---

## Dashboard Modules

| # | Module | API Endpoint | Status |
|---|--------|-------------|--------|
| 1 | Panorama General | `GET /api/v1/overview/` | ✅ Done |
| 2 | Perfil de Beneficiarios | `GET /api/v1/beneficiary-profile/` | ✅ Done |
| 3 | Inclusión y Participación Femenina | `GET /api/v1/woman-inclusion/` | ✅ Done |
| 4 | Oferta STEM | `GET /api/v1/stem-offerings/` | ✅ Done |
| 5 | Madurez del Ecosistema | `GET /api/v1/ecosystem-maturity/` | ✅ Done |
| 6 | Índice de Salud (ISE) | `GET /api/v1/health-index/` | ✅ Done |
| 🗺 | Mapa Interactivo | `GET /api/v1/ecosystem-map/` | ✅ Done |
| ⚙️ | Panel de Administración | `POST /api/v1/auth/login` + `/admin-panel/` | ✅ Done |
| 📤 | Exportación | `GET /api/v1/export/` | ✅ Done |

---

## Local Setup

### Backend

```bash
cd backend
cp .env.example .env        # fill in DATABASE_URL (Supabase) and ADMIN_PASSWORD_HASH
pip install -r requirements.txt
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

> **Note:** `ADMIN_PASSWORD_HASH` must be wrapped in quotes inside `.env` to prevent shell interpolation of `$` characters.
> Generate a new hash with: `python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('your_password'))"`
> Requires `bcrypt==4.0.1` for passlib compatibility.

### Seed the database

```bash
cd backend
python -m scripts.etl_seed
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## Admin Panel

Access at `/admin` (redirects to `/admin/login` if not authenticated).

- Session token stored in `sessionStorage`
- Auto-redirect to login on 401
- Organizations and programs support soft-delete (toggle active/inactive) instead of hard delete to preserve data integrity
- Location picker uses an interactive Leaflet satellite map

---

## Design System

Three color themes applied per route section:

| Theme | Routes | Accent |
|-------|--------|--------|
| `theme-navy` | Overview, STEMOffer, Health | Blue `#60a5fa` |
| `theme-teal` | Beneficiaries, Maturity | Teal `#2dd4bf` |
| `theme-cyan` | Inclusion, Map, Admin | Cyan `#38bdf8` |

Charts use a unified `CHART_PALETTE` combining accent colors from all three themes for consistent cross-theme readability.
