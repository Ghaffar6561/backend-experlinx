from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import text
from ...db.session import get_db_session


router = APIRouter()


class HealthCheck(BaseModel):
    status: str


class ReadinessCheck(BaseModel):
    status: str
    database: str
    details: Optional[dict] = None


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint for liveness probe.
    Returns 200 if the service is running.
    """
    return HealthCheck(status="ok")


@router.get("/ready", response_model=ReadinessCheck)
async def readiness_check():
    """
    Readiness check endpoint for readiness probe.
    Returns 200 if the service is ready to accept traffic,
    including database connectivity check.
    """
    # Check database connectivity
    try:
        # Attempt to get a database session and run a simple query
        async with get_db_session() as session:
            await session.execute(text("SELECT 1"))
        
        return ReadinessCheck(
            status="ready",
            database="connected",
            details={"database": "accessible"}
        )
    except Exception as e:
        return ReadinessCheck(
            status="not_ready",
            database="disconnected",
            details={"database": f"connection failed: {str(e)}"}
        )