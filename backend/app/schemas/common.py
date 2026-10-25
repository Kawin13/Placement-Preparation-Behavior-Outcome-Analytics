from typing import Optional, Any
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standardized error response preventing internal trace leaks."""
    error_code: str = Field(..., description="Machine-readable error identifier")
    message: str = Field(..., description="Safe, human-readable error description")
    details: Optional[Any] = Field(None, description="Optional safe contextual details")


class DatabaseHealth(BaseModel):
    status: str = Field(..., description="Connection status (connected / disconnected)")
    engine: str = Field(..., description="Database engine type")
    latency_ms: float = Field(..., description="Query latency in milliseconds")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall service status")
    service: str = Field(..., description="Service name")
    environment: str = Field(..., description="Runtime environment")
    version: str = Field(..., description="API Version")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    database: DatabaseHealth = Field(..., description="Database connectivity status")
