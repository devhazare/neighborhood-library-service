from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.exceptions import (
    NotFoundError, ValidationError, BusinessRuleError,
    not_found_handler, validation_error_handler, business_rule_error_handler,
)
from app.api.routes import books, members, borrow, health

@asynccontextmanager
async def lifespan(app: FastAPI):
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
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(BusinessRuleError, business_rule_error_handler)

app.include_router(health.router)
app.include_router(books.router)
app.include_router(members.router)
app.include_router(borrow.router)
