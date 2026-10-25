# Placement Preparation Platform - Phase 2 Native Setup Guide

This guide documents the native execution, dependency management, configuration, database connectivity, and testing procedures on Windows.

> **Important**: This project runs 100% natively on Windows. **Docker is strictly prohibited.**

---

## 1. System Requirements & Software Versions

| Component | Verified Version | Installation Command / Location | Purpose |
| :--- | :--- | :--- | :--- |
| **Operating System** | Windows 11 (64-bit) | Native Host | Development & Execution Environment |
| **Python** | 3.11.3 | Standard Windows Installer | Backend runtime, async ASGI server |
| **Node.js** | v24.13.0 | Standard Windows Installer | Frontend bundling & Vite dev server |
| **npm** | 11.6.2 | Bundled with Node.js | Frontend dependency management |
| **PostgreSQL** | 16.15-5 | `winget install PostgreSQL.PostgreSQL.16` | Native relational database service |
| **Git** | 2.54.0.windows.1 | Git for Windows | Local version control |

---

## 2. Directory Structure

```
d:\Placement Portal\
├── backend/                        # Python FastAPI Backend
│   ├── alembic/                    # Database migrations
│   │   ├── versions/               # Versioned migration scripts
│   │   └── env.py                  # Migration runner configuration
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/      # Health check and domain endpoints
│   │   │       └── router.py       # Master API v1 router
│   │   ├── core/                   # Configuration, Database engine, Structured Logging
│   │   ├── models/                 # 15 SQLAlchemy declarative ORM models
│   │   ├── schemas/                # Pydantic v2 validation models
│   │   └── main.py                 # FastAPI application entry point
│   ├── tests/                      # Pytest automated test suite
│   ├── .env.example                # Documented configuration template (placeholders only)
│   ├── .env                        # Local environment secrets (ignored by Git)
│   ├── alembic.ini                 # Alembic configuration
│   └── requirements.txt            # Pinned backend dependencies
├── frontend/                       # React 18 + TypeScript + Vite Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/             # Framer-inspired Button, Card, Badge, Input, EmptyState
│   │   │   └── layout/             # Navbar with live PostgreSQL status badge
│   │   ├── services/               # API clients with environment-configured base URLs
│   │   ├── App.tsx                 # Responsive workspace landing view
│   │   ├── index.css               # Framer design tokens, Plus Jakarta Sans, Inter
│   │   └── main.tsx                # React root mount
│   ├── .env.example                # Frontend environment template
│   ├── index.html                  # HTML entry point
│   ├── package.json                # Dependencies and npm scripts
│   ├── postcss.config.js           # PostCSS configuration
│   ├── tailwind.config.js          # Extended Tailwind theme (#FAF6ED, #292444, #FF5B3D, #E8E0D2)
│   ├── tsconfig.json               # TypeScript compiler configuration
│   └── vite.config.ts              # Vite build configuration
├── docs/                           # Architectural and setup documentation
├── .gitignore                      # Secrets protection & build artifact exclusion
└── README.md
```

---

## 3. Environment Setup & Configuration Templates

### Backend Configuration
1. From `d:\Placement Portal\backend`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Inspect `backend/.env`. It contains:
   ```ini
   PROJECT_NAME="Placement Preparation Behavior & Outcome Analytics"
   API_V1_STR=/api/v1
   ENVIRONMENT=development
   SECRET_KEY=replace_with_a_secure_random_hex_key_for_jwt_signing
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/placement_portal
   CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]
   ```

### Frontend Configuration
1. From `d:\Placement Portal\frontend`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Inspect `frontend/.env`. It points to the backend API:
   ```ini
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

---

## 4. Database Setup & Non-Destructive Connectivity Verification

The PostgreSQL 16 server runs natively as a Windows Service (`postgresql-x64-16`).

1. **Verify service readiness**:
   ```powershell
   & "C:\Program Files\PostgreSQL\16\bin\pg_isready.exe" -h localhost -p 5432
   # Expected output: localhost:5432 - accepting connections
   ```

2. **Verify database existence**:
   ```powershell
   $env:PGPASSWORD="postgres"
   & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -h localhost -p 5432 -d placement_portal -c "\dt"
   ```

3. **Run Alembic Migrations**:
   From `d:\Placement Portal\backend`:
   ```powershell
   .\.venv\Scripts\alembic.exe upgrade head
   ```

---

## 5. Starting the Applications Independently

### Backend Service (FastAPI)
Run from `d:\Placement Portal\backend`:
```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive API Documentation: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- Health Check Telemetry: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### Frontend Service (Vite Dev Server)
Run from `d:\Placement Portal\frontend`:
```powershell
npm run dev
```
- Web Application: [http://localhost:5173/](http://localhost:5173/)

---

## 6. Testing & Quality Verification

### Run Backend Unit & Integration Tests
From `d:\Placement Portal\backend`:
```powershell
.\.venv\Scripts\pytest.exe -v
```

### Run Frontend Type-Checking & Production Build
From `d:\Placement Portal\frontend`:
```powershell
npm run build
```

---

## 7. Shared Design Token System (Framer "Tempo Lessons")

| Design Token | Hex Code | Role & Usage |
| :--- | :--- | :--- |
| **Canvas** | `#FAF6ED` | Primary warm ivory page canvas background |
| **Contrast Frame** | `#292444` | Deep navy outer containers, dark headers, cards |
| **Primary Action** | `#FF5B3D` | Coral-orange CTA buttons (`rounded-full` pills) |
| **Surface** | `#FFFFFF` | Content card surfaces, modals, inputs |
| **Warm Border** | `#E8E0D2` | Subtle hairline borders on cards, tags, and inputs |
| **Subtle Tag** | `#F5EFE3` | Warm ivory pill badges with active status indicator dot |
| **Primary Text** | `#292444` | High-contrast editorial typography (WCAG AAA compliant: 12.4:1) |
| **Secondary Text** | `#5E5875` | Subtitles, labels, metadata |
| **Muted Text** | `#8E879E` | Timestamps, placeholders |
| **Success** | `#15803D` | Forest green status indicator |
| **Warning** | `#B45309` | Amber review tags |
| **Error** | `#B91C1C` | Crimson validation alerts |
