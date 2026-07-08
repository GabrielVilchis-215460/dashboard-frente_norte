# STEM Ecosystem Dashboard — Ciudad Juárez
Developed for **Frente Norte / FICOSEC** · STEM Ecosystem Observatory

<a href="https://dashboard-frente-norte.vercel.app" target="_blank">
  <img src="https://img.shields.io/badge/Website-Deployed-success?style=for-the-badge&logo=vercel" alt="Website" />
</a>
<a href="https://dashboard-frente-norte.onrender.com/docs" target="_blank">
  <img src="https://img.shields.io/badge/API-Swagger_Docs-blue?style=for-the-badge&logo=fastapi" alt="API Docs" />
</a>

## Project's description

This repository contains the source code for the **STEM Ecosystem Dashboard of Ciudad Juárez**, developed for the **STEM Ecosystem Observatory** of Frente Norte and FICOSEC. The platform allows visualizing, analyzing, and managing key indicators about organizations, programs, ecosystem maturity, female inclusion, and territorial impact in the border region. All of this through an interactive control panel, with thermal satellite maps and dynamic charts that facilitate decision-making.

---

## Tech Stack

<div align="center">
  <img src="https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB" alt="React" />
  <img src="https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/Zustand-764ABC?style=for-the-badge&logo=redux&logoColor=white" alt="Zustand" />
  <img src="https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=Leaflet&logoColor=white" alt="Leaflet" />
  <img src="https://img.shields.io/badge/Recharts-22B5BF?style=for-the-badge&logo=react&logoColor=white" alt="Recharts" />
  <br/>
  <img src="https://img.shields.io/badge/FastAPI-009485.svg?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=python&logoColor=white" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase" />
  <img src="https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens" alt="JWT" />
  <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</div>

---

## Repository Structure

```
dashboard-frente_norte/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── admin_panel/        # CRUD orgs & programs (protected)
│   │   │   ├── auth/               # JWT login
│   │   │   ├── overview/           # General Overview
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
        │   ├── Overview/           # General Overview + mini map
        │   ├── Beneficiaries/      # Beneficiary Profile
        │   ├── Inclusion/          # Female Inclusion and Participation
        │   ├── STEMOffer/          # STEM Offerings
        │   ├── Maturity/           # Ecosystem Maturity
        │   ├── Health/             # Ecosystem Health Index (ISE)
        │   ├── Map/                # Interactive Map (pins + heatmap)
        │   └── Admin/              # Admin panel (protected)
        ├── services/
        │   ├── api.ts              # Public API client (Axios)
        │   └── adminApi.ts         # Admin API client (Axios + JWT interceptors)
        ├── store/                  # Zustand global store
        ├── hooks/                  # useApi
        ├── types/                  # TypeScript types
        └── utils/                  # format helpers
```

## Local Setup

### Using Docker (Recommended)

You can spin up the entire infrastructure (Frontend and Backend) easily using Docker and Docker Compose.

**1. Set up your backend environment variables:**

```bash
cp backend/.env.example backend/.env
```

(Fill in the values such as `DATABASE_URL` and `ADMIN_PASSWORD_HASH` in your new `.env` file)

**2. From the project root, build and start the containers:**

```bash
docker-compose up -d --build
```

**3. Access the services:**

- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs

**4. To stop execution:**

```bash
docker-compose down
```

### Manual Setup (Without Docker)

#### Backend

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

#### Seed the database

```bash
cd backend
python -m scripts.etl_seed
```

#### Frontend

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
