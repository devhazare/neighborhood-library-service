import uuid
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped
from app.core.database import Base

class Book(Base):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    author: Mapped[str] = mapped_column(sa.String(300), nullable=False)
    isbn: Mapped[str | None] = mapped_column(sa.String(20), unique=True, nullable=True)
    publisher: Mapped[str | None] = mapped_column(sa.String(300), nullable=True)
    published_year: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    category: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    total_copies: Mapped[int] = mapped_column(sa.Integer, default=1)
    available_copies: Mapped[int] = mapped_column(sa.Integer, default=1)
    shelf_location: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    summary: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    tags: Mapped[list | None] = mapped_column(sa.JSON, nullable=True)
    reading_level: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    recommended_for: Mapped[str | None] = mapped_column(sa.String(200), nullable=True)
    pdf_file_path: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime | None] = mapped_column(sa.DateTime, nullable=True, onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        sa.Index("ix_books_isbn", "isbn"),
        # Check constraints for data integrity
        sa.CheckConstraint("total_copies >= 0", name="ck_books_total_copies_positive_orm"),
        sa.CheckConstraint("available_copies >= 0 AND available_copies <= total_copies", name="ck_books_copies_orm"),
    )
