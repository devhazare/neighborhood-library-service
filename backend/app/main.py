from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.exceptions import (
    NotFoundError, ValidationError, BusinessRuleError,
    AuthenticationError, AuthorizationError, DuplicateError,
    RateLimitError, ExternalServiceError, DatabaseError,
    not_found_handler, validation_error_handler, business_rule_error_handler,
    authentication_error_handler, authorization_error_handler, duplicate_error_handler,
    rate_limit_error_handler, external_service_error_handler, database_error_handler,
)
from app.core.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
)
from app.middleware.error_handler import error_handler_middleware
from app.api.routes import books, members, borrow, health, auth, fines

# Prometheus monitoring
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Initialize logger at module level
logger = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global logger
    configure_logging()
    logger = get_logger(__name__)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    if PROMETHEUS_AVAILABLE:
        logger.info("Prometheus metrics enabled at /metrics")

    yield
    logger.info("Shutting down")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Initialize Prometheus metrics BEFORE adding other middleware
if PROMETHEUS_AVAILABLE:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Global error handler middleware (must be added first to catch all errors)
app.middleware("http")(error_handler_middleware)

# Security Middleware (order matters - first added = last executed)
app.add_middleware(RequestLoggingMiddleware)  # Log all requests
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
if not settings.DEBUG:
    # Only enable rate limiting in production
    app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API version header to all responses
@app.middleware("http")
async def add_api_version_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-API-Version"] = settings.APP_VERSION
    return response

# Custom exception handlers
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(BusinessRuleError, business_rule_error_handler)
app.add_exception_handler(AuthenticationError, authentication_error_handler)
app.add_exception_handler(AuthorizationError, authorization_error_handler)
app.add_exception_handler(DuplicateError, duplicate_error_handler)
app.add_exception_handler(RateLimitError, rate_limit_error_handler)
app.add_exception_handler(ExternalServiceError, external_service_error_handler)
app.add_exception_handler(DatabaseError, database_error_handler)

# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for any unhandled exceptions."""
    error_logger = get_logger("app.errors")
    request_id = getattr(request.state, "request_id", "unknown")
    error_logger.error(
        f"Unhandled exception [request_id={request_id}]: {type(exc).__name__}: {exc}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id
        }
    )

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(members.router)
app.include_router(borrow.router)
app.include_router(fines.router)
