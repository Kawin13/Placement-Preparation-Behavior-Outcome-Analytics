from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, admin, student, institutions

api_router = APIRouter()

# Health telemetry
api_router.include_router(health.router, tags=["Health"])

# Authentication & lifecycle
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Institutions directory
api_router.include_router(institutions.router, prefix="/institutions", tags=["Institutions"])

# Administrative management & audit logs
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])

# Student profile & self-service
api_router.include_router(student.router, prefix="/student", tags=["Student"])
