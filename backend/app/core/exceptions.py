from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Any, Dict


class LibraryBaseException(Exception):
    """Base exception for all library-specific exceptions."""
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(LibraryBaseException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str = "Resource not found", resource_type: str = None, resource_id: str = None):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        super().__init__(message, "NOT_FOUND", details)


class ValidationError(LibraryBaseException):
    """Raised when input validation fails."""
    def __init__(self, message: str = "Validation error", field: str = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, "VALIDATION_ERROR", details)


class BusinessRuleError(LibraryBaseException):
    """Raised when a business rule is violated."""
    def __init__(self, message: str = "Business rule violation", rule: str = None):
        details = {}
        if rule:
            details["rule"] = rule
        super().__init__(message, "BUSINESS_RULE_VIOLATION", details)


class AuthenticationError(LibraryBaseException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(LibraryBaseException):
    """Raised when user lacks permission for an action."""
    def __init__(self, message: str = "Not authorized to perform this action", required_permission: str = None):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class DuplicateError(LibraryBaseException):
    """Raised when attempting to create a duplicate resource."""
    def __init__(self, message: str = "Resource already exists", resource_type: str = None, identifier: str = None):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if identifier:
            details["identifier"] = identifier
        super().__init__(message, "DUPLICATE_ERROR", details)


class RateLimitError(LibraryBaseException):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        super().__init__(message, "RATE_LIMIT_EXCEEDED", details)


class ExternalServiceError(LibraryBaseException):
    """Raised when an external service call fails."""
    def __init__(self, message: str = "External service error", service_name: str = None):
        details = {}
        if service_name:
            details["service"] = service_name
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)


class DatabaseError(LibraryBaseException):
    """Raised when a database operation fails."""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR")


# Exception Handlers
def _create_error_response(status_code: int, exc: LibraryBaseException, request: Request) -> JSONResponse:
    """Create a standardized error response."""
    request_id = getattr(request.state, "request_id", None)
    content = {
        "detail": exc.message,
        "code": exc.code,
    }
    if exc.details:
        content["details"] = exc.details
    if request_id:
        content["request_id"] = request_id
    return JSONResponse(status_code=status_code, content=content)


async def not_found_handler(request: Request, exc: NotFoundError):
    return _create_error_response(404, exc, request)


async def validation_error_handler(request: Request, exc: ValidationError):
    return _create_error_response(422, exc, request)


async def business_rule_error_handler(request: Request, exc: BusinessRuleError):
    return _create_error_response(409, exc, request)


async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return _create_error_response(401, exc, request)


async def authorization_error_handler(request: Request, exc: AuthorizationError):
    return _create_error_response(403, exc, request)


async def duplicate_error_handler(request: Request, exc: DuplicateError):
    return _create_error_response(409, exc, request)


async def rate_limit_error_handler(request: Request, exc: RateLimitError):
    response = _create_error_response(429, exc, request)
    if exc.details.get("retry_after_seconds"):
        response.headers["Retry-After"] = str(exc.details["retry_after_seconds"])
    return response


async def external_service_error_handler(request: Request, exc: ExternalServiceError):
    return _create_error_response(503, exc, request)


async def database_error_handler(request: Request, exc: DatabaseError):
    return _create_error_response(500, exc, request)
