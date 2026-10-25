# Institutional Placement Preparation Platform

> **Behavior & Outcome Analytics System for Higher Education**

A professional, production-grade placement preparation and behavioral analytics platform for college institutions. Built with native execution on Windows without Docker.

---

## 🎨 Visual Identity: Framer "Tempo Lessons" Inspired

- **Warm Ivory Canvas**: `#FAF6ED`
- **Deep Navy Typography**: `#292444`
- **Coral-Orange Primary Action**: `#FF5B3D`
- **Pure White Surfaces**: `#FFFFFF`
- **Subtle Warm Borders**: `#E8E0D2`

---

## 🚀 Quick Start (Native Windows PowerShell)

### Prerequisites
- Python 3.11+
- Node.js v20+ / v24+
- PostgreSQL 16 (Running as Windows Service `postgresql-x64-16`)

### 1. Backend Service (FastAPI)
```powershell
cd backend
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Docs: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 2. Frontend Application (React + Vite)
```powershell
cd frontend
npm run dev
```
- Web Application: [http://localhost:5173/](http://localhost:5173/)

---

## 🧪 Automated Testing & Verification

- **Backend Pytest**: `cd backend; .\.venv\Scripts\pytest.exe -v`
- **Frontend Build**: `cd frontend; npm run build`

For comprehensive architecture and setup details, see [docs/SETUP_GUIDE.md](file:///d:/Placement%20Portal/docs/SETUP_GUIDE.md).
