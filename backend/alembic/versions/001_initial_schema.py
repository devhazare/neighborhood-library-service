"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'books',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('author', sa.String(300), nullable=False),
        sa.Column('isbn', sa.String(20), unique=True, nullable=True),
        sa.Column('publisher', sa.String(300), nullable=True),
        sa.Column('published_year', sa.Integer, nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('total_copies', sa.Integer, default=1),
        sa.Column('available_copies', sa.Integer, default=1),
        sa.Column('shelf_location', sa.String(100), nullable=True),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('tags', sa.JSON, nullable=True),
        sa.Column('reading_level', sa.String(50), nullable=True),
        sa.Column('recommended_for', sa.String(200), nullable=True),
        sa.Column('pdf_file_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_books_isbn', 'books', ['isbn'])

    op.create_table(
        'members',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('membership_id', sa.String(50), unique=True, nullable=False),
        sa.Column('full_name', sa.String(300), nullable=False),
        sa.Column('email', sa.String(200), unique=True, nullable=True),
        sa.Column('phone', sa.String(30), nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('joined_date', sa.Date, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_members_membership_id', 'members', ['membership_id'])

    op.create_table(
        'borrow_transactions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('book_id', sa.String(36), sa.ForeignKey('books.id'), nullable=False),
        sa.Column('member_id', sa.String(36), sa.ForeignKey('members.id'), nullable=False),
        sa.Column('borrow_date', sa.Date, nullable=False),
        sa.Column('due_date', sa.Date, nullable=False),
        sa.Column('return_date', sa.Date, nullable=True),
        sa.Column('status', sa.String(20), default='borrowed'),
        sa.Column('overdue_days', sa.Integer, default=0),
        sa.Column('reminder_sent', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_borrow_member_id', 'borrow_transactions', ['member_id'])
    op.create_index('ix_borrow_book_id', 'borrow_transactions', ['book_id'])
    op.create_index('ix_borrow_status', 'borrow_transactions', ['status'])
    op.create_index('ix_borrow_due_date', 'borrow_transactions', ['due_date'])

    op.create_table(
        'ai_enrichment_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(36), nullable=False),
        sa.Column('enrichment_type', sa.String(100), nullable=False),
        sa.Column('input_text', sa.Text, nullable=True),
        sa.Column('output_json', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('ai_enrichment_logs')
    op.drop_index('ix_borrow_due_date', table_name='borrow_transactions')
    op.drop_index('ix_borrow_status', table_name='borrow_transactions')
    op.drop_index('ix_borrow_book_id', table_name='borrow_transactions')
    op.drop_index('ix_borrow_member_id', table_name='borrow_transactions')
    op.drop_table('borrow_transactions')
    op.drop_index('ix_members_membership_id', table_name='members')
    op.drop_table('members')
    op.drop_index('ix_books_isbn', table_name='books')
    op.drop_table('books')
