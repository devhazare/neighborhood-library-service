from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql://library:library@localhost:5432/library_db"
    SECRET_KEY: str = "change-me-in-production"
    OPENAI_API_KEY: Optional[str] = None
    PDF_UPLOAD_DIR: str = "./uploads/pdfs"
    MAX_BORROW_DAYS: int = 14
    MAX_ACTIVE_BORROWINGS: int = 5
    FINE_PER_DAY: float = 0.50  # Fine amount per overdue day
    MAX_FINE_AMOUNT: float = 25.00  # Maximum fine cap
    APP_NAME: str = "Neighborhood Library Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    AWS_REGION: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

settings = Settings()
