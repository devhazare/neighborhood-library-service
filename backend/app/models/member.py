import uuid
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped
from app.core.database import Base

class Member(Base):
    __tablename__ = "members"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    membership_id: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(sa.String(300), nullable=False)
    email: Mapped[str | None] = mapped_column(sa.String(200), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(sa.String(30), nullable=True)
    address: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    status: Mapped[str] = mapped_column(sa.String(20), default="active")
    joined_date: Mapped[datetime.date | None] = mapped_column(sa.Date, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime | None] = mapped_column(sa.DateTime, nullable=True, onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    __table_args__ = (
        sa.Index("ix_members_membership_id", "membership_id"),
    )
