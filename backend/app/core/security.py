"""
Security utilities and middleware for the application.
"""
from functools import wraps
from typing import Callable, Dict
import time
import hashlib
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import re

# =============================================================================
# Rate Limiting
# =============================================================================

class RateLimiter:
    """Simple in-memory rate limiter. Use Redis in production for distributed systems."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        return ip

    def is_allowed(self, request: Request) -> bool:
        """Check if request is allowed under rate limit."""
        client_id = self._get_client_id(request)
        current_time = time.time()
        minute_ago = current_time - 60

        # Clean old requests
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > minute_ago
        ]

        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False

        self.requests[client_id].append(current_time)
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting to all requests."""

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute)

    async def dispatch(self, request: Request, call_next):
        if not self.limiter.is_allowed(request):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        return await call_next(request)


# =============================================================================
# Input Sanitization
# =============================================================================

def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize a string input to prevent injection attacks."""
    if not value:
        return value

    # Truncate to max length
    value = value[:max_length]

    # Remove null bytes
    value = value.replace('\x00', '')

    # Strip control characters (except newlines and tabs)
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)

    return value.strip()


def sanitize_html(value: str) -> str:
    """Remove HTML tags from a string."""
    if not value:
        return value
    return re.sub(r'<[^>]+>', '', value)


# =============================================================================
# Security Headers Middleware
# =============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent XSS attacks
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy (adjust as needed)
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Strict Transport Security (enable in production with HTTPS)
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


# =============================================================================
# Request ID for Tracing
# =============================================================================

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID for tracing/debugging."""

    async def dispatch(self, request: Request, call_next):
        request_id = hashlib.md5(
            f"{time.time()}{request.client.host if request.client else ''}".encode()
        ).hexdigest()[:12]

        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


# =============================================================================
# Request Logging Middleware
# =============================================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests with timing information."""

    async def dispatch(self, request: Request, call_next):
        import logging
        logger = logging.getLogger("api.access")

        start_time = time.time()

        # Get request details
        method = request.method
        path = request.url.path
        query = str(request.url.query) if request.url.query else ""
        client_ip = request.headers.get("X-Forwarded-For",
                    request.client.host if request.client else "unknown")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Get request ID if available
        request_id = getattr(request.state, "request_id", "-")

        # Log the request (skip health checks to reduce noise)
        if not path.startswith("/health"):
            logger.info({
                "request_id": request_id,
                "method": method,
                "path": path,
                "query": query,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
            })

        # Add timing header
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        return response


# =============================================================================
# SQL Injection Prevention (additional layer)
# =============================================================================

DANGEROUS_SQL_PATTERNS = [
    r";\s*--",
    r";\s*drop\s+",
    r";\s*delete\s+",
    r";\s*update\s+",
    r";\s*insert\s+",
    r"union\s+select",
    r"'\s*or\s+'1'\s*=\s*'1",
    r'"\s*or\s+"1"\s*=\s*"1',
]

def check_sql_injection(value: str) -> bool:
    """Check if a string contains potential SQL injection patterns."""
    if not value:
        return False

    lower_value = value.lower()
    for pattern in DANGEROUS_SQL_PATTERNS:
        if re.search(pattern, lower_value):
            return True
    return False


def validate_input(value: str, field_name: str = "input") -> str:
    """Validate and sanitize user input."""
    if check_sql_injection(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid characters in {field_name}"
        )
    return sanitize_string(value)

