# Institutional Placement Portal — Operations & Handover Manual

> **Document Classification**: Institutional Operations, Deployment & Administrative Handover  
> **Platform Version**: 1.0.0 (Windows Native Stack · No Docker)  
> **Database Engine**: PostgreSQL 16 (Windows Service: `postgresql-x64-16`)  
> **Backend Framework**: Python 3.11+ / FastAPI / SQLAlchemy / Alembic  
> **Frontend Engine**: React 19 / TypeScript 5 / Vite 8 / Framer Tempo Design  

---

## 1. System Overview & Architecture

The **Institutional Placement Preparation Behavior & Outcome Analytics Platform** is an enterprise-grade academic intelligence system designed for higher education institutions. It tracks student placement preparation, provides diagnostic skill-gap analytics, manages deterministic assessment tracks, verifies placement hiring outcomes, calculates training program effectiveness via paired t-tests, and synthesizes 4-pillar executive dossiers with strict small-cell privacy ($N < 5$).

### Architectural Principles
1. **100% Native Windows Execution**: Operates natively on Windows Server or Windows 11 host environments. **Docker and container abstraction layers are strictly prohibited.**
2. **Deterministic Data Integrity (Rule 8)**: Zero hardcoded metrics, fake charts, or hallucinated counts. All operational statistics derive from audited PostgreSQL records.
3. **Observational Attribution Guardrails**: Non-causal disclaimers are enforced across analytical dossiers. Correlation between preparation and placement is explicitly documented as observational, not a guarantee of hiring.
4. **Small-Cell Privacy ($k$-Anonymity Suppression)**: Any cohort or department filter with sample size $N < 5$ automatically masks granular percentage distributions to prevent indirect student re-identification.
5. **Defense-in-Depth Security**: Bcrypt-12 cryptographic password hashing, role-based access control (RBAC), signed JWT token authentication, and sanitization against SQL injection and XSS.

---

## 2. Environment Configuration Reference

Configuration is managed via environment files (`.env`). Secrets are never committed to version control.

### Backend Configuration (`backend/.env`)

| Variable | Type | Default / Example | Purpose |
| :--- | :--- | :--- | :--- |
| `PROJECT_NAME` | string | `"Placement Preparation Behavior & Outcome Analytics"` | Application title in API docs and OpenAPI specs |
| `API_V1_STR` | string | `"/api/v1"` | URL prefix for REST API version 1 |
| `ENVIRONMENT` | string | `"production"` | Environment mode (`development` or `production`) |
| `SECRET_KEY` | string | `[64-character hex string]` | Cryptographic secret for signing JWT access tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `1440` | JWT token validity lifetime (1440 minutes = 24 hours) |
| `DATABASE_URL` | string | `postgresql://<user>:<pwd>@localhost:5432/placement_portal` | PostgreSQL native connection URI |
| `CORS_ORIGINS` | JSON list | `["https://portal.college.edu", "http://localhost:5173"]` | Authorized frontend host domains allowed for CORS |
| `AI_PROVIDER` | string | `"offline"` or `"gemini"` | Coach engine: `offline` (deterministic mentor) or `gemini` |
| `GEMINI_API_KEY` | string | `[API Key or null]` | Optional Gemini API key if `AI_PROVIDER=gemini` |
| `AI_MODEL_NAME` | string | `"gemini-1.5-flash"` | Target LLM model if external provider enabled |
| `AI_TIMEOUT_SECONDS` | int | `8` | Maximum timeout before fallback to offline mentor |

### Frontend Configuration (`frontend/.env`)

| Variable | Type | Example | Purpose |
| :--- | :--- | :--- | :--- |
| `VITE_API_BASE_URL` | string | `http://localhost:8000/api/v1` or `https://portal.college.edu/api/v1` | Base API target URL for the React single-page app |

---

## 3. Native Windows PowerShell Runbooks

### Starting the Platform
Launch backend and frontend as background daemons or Windows Services:

```powershell
# 1. Start PostgreSQL Windows Service (if not set to Automatic)
Start-Service -Name "postgresql-x64-16"

# 2. Launch FastAPI Backend Service
cd "D:\Placement Portal\backend"
& ".\.venv\Scripts\uvicorn.exe" app.main:app --host 127.0.0.1 --port 8000

# 3. Launch Frontend Production Server
cd "D:\Placement Portal\frontend"
npm run build
npm run preview -- --host 127.0.0.1 --port 5173
```

### Stopping the Platform
```powershell
# Gracefully terminate uvicorn and vite processes
Get-Process | Where-Object { $_.ProcessName -match "uvicorn|node" } | Stop-Process -Force
```

### Health & Connectivity Check
```powershell
# Check backend and PostgreSQL heartbeat
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -Method Get
```

Expected response:
```json
{
  "status": "healthy",
  "database": {
    "status": "connected",
    "latency_ms": 1.2
  },
  "timestamp": "2026-10-25T13:30:00Z"
}
```

---

## 4. Database Schema & Migration Runbook

The schema comprises 22 relational tables managed via Alembic:

### Migration History
1. `9116e1c383bc`: Initial core schema (Institutions, Departments, Cohorts, Users, Student Profiles, Skills, Questions, Options, Assessments, Sessions, Attempts, Mistake Notebook, Audit Logs).
2. `633d6852277a`: Preparation Activities & Learning Goals tracking.
3. `622f9a29d4e0`: Content versioning and session tracking extensions.
4. `3c082f8c7dad` *(head)*: Training Programs, Training Sessions, Attendance, and Placement Outcomes.

### Executing Migrations
```powershell
cd "D:\Placement Portal\backend"

# Inspect current database revision
& ".\.venv\Scripts\alembic.exe" current

# Upgrade to latest revision (head)
& ".\.venv\Scripts\alembic.exe" upgrade head

# Rollback one revision (if emergency migration reversal is required)
& ".\.venv\Scripts\alembic.exe" downgrade -1
```

---

## 5. Disaster Recovery & Backup Playbook

### Standard Backup Procedure (Automated Scheduled Task)
Execute `pg_dump` to create an encrypted or restricted custom-format archive:

```powershell
$Env:PGPASSWORD = "your_secure_password"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = "D:\Backups\PlacementPortal"
$BackupFile = "$BackupDir\placement_portal_backup_$Timestamp.sql"

& "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe" `
  -h localhost `
  -p 5432 `
  -U postgres `
  -d placement_portal `
  -F c `
  -f $BackupFile
```

### Non-Destructive Restoration Verification Drill
To verify backup integrity **without touching production records**:

```powershell
cd "D:\Placement Portal\backend"
& ".\.venv\Scripts\python.exe" verify_recovery.py
```

*The script dumps the source database, creates a temporary isolated database `placement_portal_recovery_verify`, restores all 22 tables, validates record counts, and tears down cleanly.*

---

## 6. Role-Based User Operations Guides

### A. Student Guide
- **Account Registration**: Self-registration assigns the `STUDENT` role with anti-privilege escalation.
- **Student Workspace**: View tracked practice volume, active time, and learning goals.
- **Practice Runner**: Complete formative mastery assessments with randomized options, deterministic scoring, and explanations.
- **Mistake Notebook**: Automatically logs incorrect answers with personal notes and revision toggles.
- **Role Readiness & Coach**: Evaluate readiness score against target profiles (`SDE`, `DATA_ANALYST`, etc.). Launch grounded AI Coach for mistake explanations.
- **Placement Self-Reporting**: Submit job offers with proof document URLs for placement officer verification.

### B. Trainer Guide
- **Assessment Management**: Create, review, and publish problem sets grouped by topic and difficulty.
- **Training Programs**: Create training curricula with scheduled sessions.
- **Attendance Ledger**: Mark session attendance; unique composite constraints prevent double logging.
- **Cohort Performance Telemetry**: Monitor topic-level accuracy across assigned student cohorts.

### C. Placement Officer Guide
- **Placement Outcome Ledger**: Review student self-reported offers. Verify or reject with reason notes.
- **Batch CSV Import**: Import institutional offer lists with provenance tracking.
- **Training Effectiveness Analyzer**: Compare pre-training vs. post-training performance using paired t-test analytics.
- **Verified Placement Reports**: Export institutional placement ledger directly to CSV.

### D. Institutional Administrator Guide
- **Executive Dossier**: Real-time 4-Pillar institutional dossier (Engagement, Skill Accuracy, Training Impact, Placement Conversion).
- **Small-Cell Privacy Suppression ($N < 5$)**: Protect student privacy when inspecting small cohorts.
- **User Account Governance**: List accounts, toggle activation states, and provision staff.
- **Academic Structure**: Create departments, manage graduation year cohorts, and bulk-assign students.
- **Content Bank Inspection**: Monitor question distribution across domains.
- **Security Audit Trail**: Inspect and export immutable security audit logs to CSV.

---

## 7. Security & Observational Data Guardrails

1. **Non-Causal Notice**: The portal does not guarantee placement. Analytical correlations represent historical observations.
2. **No Code Execution on Server**: The platform deterministically checks submitted answers against model answers without server-side interpreters.
3. **Audit Trail Immutability**: Administrative privilege changes, user creations, and verification actions are logged into `audit_logs`.
4. **Error Masking**: Internal server errors return sanitized JSON structures with zero stack-trace leakage.

---

## 8. Institutional Handover & Maintenance Contacts

- **Application Custodian**: Institutional Placement & Training Cell (Dean / Placement Director)
- **IT Infrastructure Owner**: College IT Systems Administration (Server Management, PostgreSQL Backup Automation)
- **Handover Date**: October 2026
- **License**: Institutional Commercial / Proprietary (Internal Campus Use)
