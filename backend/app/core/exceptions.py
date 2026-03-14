from fastapi import Request
from fastapi.responses import JSONResponse

class NotFoundError(Exception):
    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(self.message)

class ValidationError(Exception):
    def __init__(self, message: str = "Validation error"):
        self.message = message
        super().__init__(self.message)

class BusinessRuleError(Exception):
    def __init__(self, message: str = "Business rule violation"):
        self.message = message
        super().__init__(self.message)

async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.message})

async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.message})

async def business_rule_error_handler(request: Request, exc: BusinessRuleError):
    return JSONResponse(status_code=409, content={"detail": exc.message})
