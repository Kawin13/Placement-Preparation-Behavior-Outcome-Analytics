from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    admin,
    student,
    institutions,
    practice,
    analytics,
    readiness,
    coach,
    placement,
    training,
    dsa,
)

api_router = APIRouter()

# Health telemetry
api_router.include_router(health.router, tags=["Health"])

# DSA Problem-Solving Platform & Online Judge
api_router.include_router(dsa.router, prefix="/dsa", tags=["DSA Problem Solving & Online Judge"])

# Authentication & lifecycle
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Institutions directory
api_router.include_router(institutions.router, prefix="/institutions", tags=["Institutions"])

# Administrative management & audit logs
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])

# Student profile & self-service
api_router.include_router(student.router, prefix="/student", tags=["Student"])

# Assessment Engine & Practice Sessions
api_router.include_router(practice.router, prefix="/practice", tags=["Practice Engine"])

# Behaviour & Performance Analytics
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Skill Gaps"])

# Role-Specific Readiness Intelligence
api_router.include_router(readiness.router, prefix="/readiness", tags=["Role Readiness"])

# AI Learning Coach & Grounded Pedagogical Mentor
api_router.include_router(coach.router, prefix="/coach", tags=["AI Learning Coach"])

# Placement Outcomes & Verification
api_router.include_router(placement.router, prefix="/placement", tags=["Placement Outcomes"])

# Training Effectiveness & Attendance
api_router.include_router(training.router, prefix="/training", tags=["Training Effectiveness"])
