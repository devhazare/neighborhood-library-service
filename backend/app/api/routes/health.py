from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/live")
def liveness_check():
    """
    Kubernetes liveness probe.
    Returns 200 if the application is running.
    """
    return {"status": "alive"}


@router.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    """
    Kubernetes readiness probe.
    Checks if the application can handle traffic (DB connection, etc.)
    """
    checks = {
        "database": False,
        "status": "not_ready"
    }

    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        checks["database_error"] = str(e)

    # Overall status
    if checks["database"]:
        checks["status"] = "ready"
        return checks

    # Return 503 if not ready
    from fastapi import HTTPException
    raise HTTPException(status_code=503, detail=checks)


@router.get("/health/detailed")
def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with system information.
    For monitoring and debugging purposes.
    """
    import platform
    import sys

    checks = {
        "status": "ok",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "development" if settings.DEBUG else "production",
        "checks": {
            "database": {"status": "unknown"}
        },
        "system": {
            "python_version": sys.version,
            "platform": platform.platform()
        }
    }

    # Database check with response time
    try:
        import time
        start = time.time()
        db.execute(text("SELECT 1"))
        duration = (time.time() - start) * 1000
        checks["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": round(duration, 2)
        }
    except Exception as e:
        checks["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        checks["status"] = "degraded"

    return checks

