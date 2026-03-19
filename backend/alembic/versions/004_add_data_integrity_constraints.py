"""Add data integrity constraints

Revision ID: 004
Revises: 003
Create Date: 2024-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add unique partial index to prevent duplicate active borrowings
    # A member cannot borrow the same book twice while it's still borrowed/overdue
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_unique_active_borrow 
        ON borrow_transactions (member_id, book_id) 
        WHERE status IN ('borrowed', 'overdue')
    """)

    # Add check constraint for status values
    op.execute("""
        ALTER TABLE borrow_transactions 
        ADD CONSTRAINT ck_borrow_status 
        CHECK (status IN ('borrowed', 'overdue', 'returned'))
    """)

    # Add check constraint for member status values
    op.execute("""
        ALTER TABLE members 
        ADD CONSTRAINT ck_member_status 
        CHECK (status IN ('active', 'inactive'))
    """)

    # Add check constraint for available_copies <= total_copies
    op.execute("""
        ALTER TABLE books 
        ADD CONSTRAINT ck_books_copies 
        CHECK (available_copies >= 0 AND available_copies <= total_copies)
    """)

    # Add check constraint for total_copies >= 0
    op.execute("""
        ALTER TABLE books 
        ADD CONSTRAINT ck_books_total_copies_positive 
        CHECK (total_copies >= 0)
    """)

    # Add check constraint for fine_amount >= 0
    op.execute("""
        ALTER TABLE borrow_transactions 
        ADD CONSTRAINT ck_borrow_fine_positive 
        CHECK (fine_amount >= 0)
    """)

    # Add check constraint for overdue_days >= 0
    op.execute("""
        ALTER TABLE borrow_transactions 
        ADD CONSTRAINT ck_borrow_overdue_days_positive 
        CHECK (overdue_days >= 0)
    """)

    # Add check constraint for due_date >= borrow_date
    op.execute("""
        ALTER TABLE borrow_transactions 
        ADD CONSTRAINT ck_borrow_due_after_borrow 
        CHECK (due_date >= borrow_date)
    """)

    # Add check constraint for return_date >= borrow_date (when not null)
    op.execute("""
        ALTER TABLE borrow_transactions 
        ADD CONSTRAINT ck_borrow_return_after_borrow 
        CHECK (return_date IS NULL OR return_date >= borrow_date)
    """)


def downgrade() -> None:
    # Remove constraints in reverse order
    op.execute("ALTER TABLE borrow_transactions DROP CONSTRAINT IF EXISTS ck_borrow_return_after_borrow")
    op.execute("ALTER TABLE borrow_transactions DROP CONSTRAINT IF EXISTS ck_borrow_due_after_borrow")
    op.execute("ALTER TABLE borrow_transactions DROP CONSTRAINT IF EXISTS ck_borrow_overdue_days_positive")
    op.execute("ALTER TABLE borrow_transactions DROP CONSTRAINT IF EXISTS ck_borrow_fine_positive")
    op.execute("ALTER TABLE books DROP CONSTRAINT IF EXISTS ck_books_total_copies_positive")
    op.execute("ALTER TABLE books DROP CONSTRAINT IF EXISTS ck_books_copies")
    op.execute("ALTER TABLE members DROP CONSTRAINT IF EXISTS ck_member_status")
    op.execute("ALTER TABLE borrow_transactions DROP CONSTRAINT IF EXISTS ck_borrow_status")
    op.execute("DROP INDEX IF EXISTS ix_unique_active_borrow")

