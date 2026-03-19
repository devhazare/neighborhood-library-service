from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.exceptions import (
    NotFoundError, ValidationError, BusinessRuleError,
    not_found_handler, validation_error_handler, business_rule_error_handler,
)
from app.core.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
)
from app.api.routes import books, members, borrow, health, auth

# Initialize logger at module level
logger = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global logger
    configure_logging()
    logger = get_logger(__name__)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
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
# Note: Fines endpoints are included in borrow.router (/fines/pay, /fines/unpaid, /members/{id}/fines)
