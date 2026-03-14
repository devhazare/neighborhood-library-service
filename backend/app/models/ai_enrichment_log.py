import uuid
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped
from app.core.database import Base

class AIEnrichmentLog(Base):
    __tablename__ = "ai_enrichment_logs"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(sa.String(36), nullable=False)
    enrichment_type: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    input_text: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    output_json: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
