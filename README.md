# Institutional Placement Preparation Platform

> **Placement Preparation Behavior & Outcome Analytics System**  
> *A Production-Grade Institutional Learning & Accreditation Analytics Platform for Higher Education*

Built with **100% Native Windows Execution** without Docker, adhering to institutional privacy policies, cryptographic security standards, and strict empirical data integrity (Rule 8 compliance).

---

## 🎨 Visual Identity & Design System

Inspired by the editorial elegance of **Framer Tempo Lessons**:
- **Canvas (Warm Ivory)**: `#FAF6ED`
- **Primary Typography & Header Surface (Deep Navy)**: `#292444`
- **Primary Brand Accent (Coral-Orange)**: `#FF5B3D`
- **Elevated Surfaces**: `#FFFFFF`
- **Subtle Architectural Borders**: `#E8E0D2`
- **Interactive Feedback**: Glassmorphic backdrops, micro-animations, deterministic progress indicators.

---

## 🏛️ Comprehensive Institutional Feature Suite

1. **Phase 1–3: Core Architecture, RBAC & Identity Governance**
   - Multi-tenant institutional data isolation.
   - Server-side Role-Based Access Control (`STUDENT`, `TRAINER`, `PLACEMENT_OFFICER`, `ADMIN`).
   - Bcrypt-12 salted hashing, JWT token authentication, and tamper-resistant password resets.
2. **Phase 4: Student Profiles & Preparation Activity Tracking**
   - Self-service student profiles with institutional roll number validation.
   - Comprehensive preparation activity logging across 5 types and 8 skill domains.
   - Automated learning goal progress tracking against questions solved and study minutes.
3. **Phase 5: Assessment Engine & Formative Mastery Practice**
   - Question bank management with version control and publishing workflows.
   - Candidate sanitization: option correctness and explanations strictly hidden during active sessions.
   - Upsert attempt tracking preventing duplicate submissions.
   - Automatic sync of incorrect responses into the student's personal Mistake Notebook.
4. **Phase 6: Empirical Behavior & Cohort Analytics**
   - Reproducible student progress telemetry with explicit provenance labels.
   - Statistically defensible skill-gap diagnostic thresholds ($N \ge 5$ attempts per topic).
   - Cohort analytical distributions and authorized CSV reporting with immutable audit trails.
5. **Phase 7: Role-Specific Readiness & Grounded AI Coach**
   - Target job profiles mapped to specific skill domains and evidence thresholds.
   - Small-evidence score suppression preventing unreliable readiness ratings.
   - Dual-mode grounded AI Learning Coach: zero-cost deterministic offline mentor or optional Google Gemini provider.
6. **Phase 8: Training Effectiveness & Verified Placement Outcomes**
   - Verification lifecycle: student self-reported offers reviewed, approved, or rejected with provenance.
   - Training curriculum management and attendance tracking with composite uniqueness constraints.
   - Paired pre/post-training statistical comparison using paired t-tests and causal attribution disclaimers.
7. **Phase 9: College Intelligence & Administration Console**
   - 4-Pillar Executive Dossier (Engagement, Skill Accuracy, Training Impact, Placement Conversion).
   - Small-cell privacy suppression ($N < 5$) to prevent student re-identification.
   - Account governance (active/inactive toggling, staff provisioning).
   - Department, cohort, and content bank administration.
   - Immutable security audit logs with CSV export.
8. **Phase 10: Production Quality, Disaster Recovery & Security Audit**
   - 58 automated backend tests passed with 100% success rate.
   - Non-destructive PostgreSQL 16 disaster recovery test verified across all 22 tables and 6,107 rows.
   - Zero stack-trace leakage, XSS sanitization, and parameterized SQL queries.

---

## 🚀 Native Windows Quick Start

### Host Prerequisites
- **Operating System**: Windows 11 (64-bit) or Windows Server 2022
- **Python**: 3.11+
- **Node.js**: v20+ / v24+
- **PostgreSQL**: 16.x (Running as Windows Service `postgresql-x64-16`)

### 1. Backend Service (FastAPI)
```powershell
cd "D:\Placement Portal\backend"
& ".\.venv\Scripts\uvicorn.exe" app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **API Documentation**: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)
- **Service Heartbeat**: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

### 2. Frontend Application (React + Vite)
```powershell
cd "D:\Placement Portal\frontend"
npm run dev
```
- **Web Application Portal**: [http://localhost:5173/](http://localhost:5173/)

---

## 🧪 Verification & Test Suites

```powershell
# Run full automated backend test suite (58 tests across 10 modules)
cd "D:\Placement Portal\backend"
& ".\.venv\Scripts\pytest.exe" -v

# Run non-destructive disaster recovery verification drill
& ".\.venv\Scripts\python.exe" verify_recovery.py

# Run frontend build verification
cd "D:\Placement Portal\frontend"
npm run build
npm run lint
```

---

## 📚 Documentation & Operations Handover

- [docs/COLLEGE_HANDOVER_MANUAL.md](file:///d:/Placement%20Portal/docs/COLLEGE_HANDOVER_MANUAL.md) — Complete institutional operations, disaster recovery, and administrative runbooks.
- [docs/SETUP_GUIDE.md](file:///d:/Placement%20Portal/docs/SETUP_GUIDE.md) — Native Windows installation and architecture specification.

---

## 🔒 Institutional Governance & Attribution Notice

Data tracked by this platform represents empirical observational evidence. Placement readiness ratings and training effectiveness statistics reflect observed institutional correlations and do not constitute an explicit legal guarantee or deterministic prediction of external employment.
