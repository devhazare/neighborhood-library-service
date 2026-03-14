import uuid
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped
from app.core.database import Base

class BorrowTransaction(Base):
    __tablename__ = "borrow_transactions"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id: Mapped[str] = mapped_column(sa.String(36), sa.ForeignKey("books.id"), nullable=False)
    member_id: Mapped[str] = mapped_column(sa.String(36), sa.ForeignKey("members.id"), nullable=False)
    borrow_date: Mapped[datetime.date] = mapped_column(sa.Date, nullable=False)
    due_date: Mapped[datetime.date] = mapped_column(sa.Date, nullable=False)
    return_date: Mapped[datetime.date | None] = mapped_column(sa.Date, nullable=True)
    status: Mapped[str] = mapped_column(sa.String(20), default="borrowed")
    overdue_days: Mapped[int] = mapped_column(sa.Integer, default=0)
    reminder_sent: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime | None] = mapped_column(sa.DateTime, nullable=True, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        sa.Index("ix_borrow_member_id", "member_id"),
        sa.Index("ix_borrow_book_id", "book_id"),
        sa.Index("ix_borrow_status", "status"),
        sa.Index("ix_borrow_due_date", "due_date"),
    )
