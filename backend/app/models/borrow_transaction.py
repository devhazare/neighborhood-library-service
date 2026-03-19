import uuid
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped
from app.core.database import Base

class BorrowTransaction(Base):
    __tablename__ = "borrow_transactions"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    book_id: Mapped[str] = mapped_column(sa.String(36), sa.ForeignKey("books.id", ondelete="RESTRICT"), nullable=False)
    member_id: Mapped[str] = mapped_column(sa.String(36), sa.ForeignKey("members.id", ondelete="RESTRICT"), nullable=False)
    borrow_date: Mapped[datetime.date] = mapped_column(sa.Date, nullable=False)
    due_date: Mapped[datetime.date] = mapped_column(sa.Date, nullable=False)
    return_date: Mapped[datetime.date | None] = mapped_column(sa.Date, nullable=True)
    status: Mapped[str] = mapped_column(sa.String(20), default="borrowed")
    overdue_days: Mapped[int] = mapped_column(sa.Integer, default=0)
    reminder_sent: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    # Fine tracking
    fine_amount: Mapped[float] = mapped_column(sa.Numeric(10, 2), default=0.0)
    fine_paid: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    fine_paid_date: Mapped[datetime.date | None] = mapped_column(sa.Date, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime | None] = mapped_column(sa.DateTime, nullable=True, onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        sa.Index("ix_borrow_member_id", "member_id"),
        sa.Index("ix_borrow_book_id", "book_id"),
        sa.Index("ix_borrow_status", "status"),
        sa.Index("ix_borrow_due_date", "due_date"),
        # Partial unique index for preventing duplicate active borrowings (PostgreSQL)
        sa.Index(
            "ix_unique_active_borrow_orm",
            "member_id", "book_id",
            unique=True,
            postgresql_where=sa.text("status IN ('borrowed', 'overdue')")
        ),
        # Check constraints
        sa.CheckConstraint("status IN ('borrowed', 'overdue', 'returned')", name="ck_borrow_status_orm"),
        sa.CheckConstraint("fine_amount >= 0", name="ck_borrow_fine_positive_orm"),
        sa.CheckConstraint("overdue_days >= 0", name="ck_borrow_overdue_days_positive_orm"),
        sa.CheckConstraint("due_date >= borrow_date", name="ck_borrow_due_after_borrow_orm"),
    )
