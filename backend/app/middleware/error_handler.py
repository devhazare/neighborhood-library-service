"""Global error handling middleware."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from pydantic import ValidationError
from app.core.logging import get_structured_logger

logger = get_structured_logger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """Handle errors globally and return appropriate responses."""
    try:
        response = await call_next(request)
        return response
    except IntegrityError as e:
        logger.error(
            "database_integrity_error",
            error=str(e),
            path=request.url.path,
            method=request.method
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "Database constraint violation. The operation conflicts with existing data.",
                "type": "integrity_error"
            }
        )
    except OperationalError as e:
        logger.error(
            "database_operational_error",
            error=str(e),
            path=request.url.path,
            method=request.method
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Database service unavailable. Please try again later.",
                "type": "operational_error"
            }
        )
    except ValidationError as e:
        logger.warning(
            "validation_error",
            error=str(e),
            path=request.url.path,
            method=request.method
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation failed",
                "errors": e.errors(),
                "type": "validation_error"
            }
        )
    except Exception as e:
        logger.exception(
            "unhandled_error",
            error=str(e),
            error_type=type(e).__name__,
            path=request.url.path,
            method=request.method
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred. Please contact support if the issue persists.",
                "type": "internal_server_error"
            }
        )

