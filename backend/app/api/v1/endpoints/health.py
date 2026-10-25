import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from app.core.logging import logger
from app.schemas.common import HealthResponse, DatabaseHealth

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application & Database Health Telemetry",
    description="Probes the application server and verifies PostgreSQL connection pool readiness and query latency."
)
def check_health(db: Session = Depends(get_db)) -> HealthResponse:
    start_time = time.time()
    try:
        # Perform low-overhead verification query
        result = db.execute(text("SELECT 1")).scalar()
        if result != 1:
            logger.error("Health check database query returned invalid response")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database query returned unexpected result",
            )
        db_latency_ms = round((time.time() - start_time) * 1000, 2)
        db_status = "connected"
    except Exception as exc:
        logger.error(f"Health check failed to communicate with PostgreSQL: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connectivity check failed",
        )

    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
        database=DatabaseHealth(
            status=db_status,
            engine="PostgreSQL 16",
            latency_ms=db_latency_ms,
        ),
    )
