"""Add fine tracking fields to borrow_transactions

Revision ID: 003
Revises: 002_add_users_table
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add fine tracking columns to borrow_transactions table
    op.add_column('borrow_transactions', sa.Column('fine_amount', sa.Numeric(10, 2), nullable=False, server_default='0'))
    op.add_column('borrow_transactions', sa.Column('fine_paid', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('borrow_transactions', sa.Column('fine_paid_date', sa.Date(), nullable=True))

    # Add index for finding unpaid fines
    op.create_index('ix_borrow_fine_paid', 'borrow_transactions', ['fine_paid'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_borrow_fine_paid', table_name='borrow_transactions')
    op.drop_column('borrow_transactions', 'fine_paid_date')
    op.drop_column('borrow_transactions', 'fine_paid')
    op.drop_column('borrow_transactions', 'fine_amount')

