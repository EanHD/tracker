"""add_cash_flow_events_table

Revision ID: ef5ee746e09b
Revises: 21906f1f542a
Create Date: 2025-10-27 10:36:59.676041

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef5ee746e09b'
down_revision: Union[str, Sequence[str], None] = '21906f1f542a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create cash_flow_events table
    op.create_table(
        'cash_flow_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('account', sa.String(length=100), nullable=True),
        sa.Column('memo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient queries
    op.create_index(op.f('ix_cash_flow_events_user_id'), 'cash_flow_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_cash_flow_events_event_date'), 'cash_flow_events', ['event_date'], unique=False)
    op.create_index(op.f('ix_cash_flow_events_event_type'), 'cash_flow_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_cash_flow_events_provider'), 'cash_flow_events', ['provider'], unique=False)
    op.create_index('ix_cfe_user_date', 'cash_flow_events', ['user_id', 'event_date'], unique=False)
    op.create_index('ix_cfe_type_provider', 'cash_flow_events', ['event_type', 'provider'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_cfe_type_provider', table_name='cash_flow_events')
    op.drop_index('ix_cfe_user_date', table_name='cash_flow_events')
    op.drop_index(op.f('ix_cash_flow_events_provider'), table_name='cash_flow_events')
    op.drop_index(op.f('ix_cash_flow_events_event_type'), table_name='cash_flow_events')
    op.drop_index(op.f('ix_cash_flow_events_event_date'), table_name='cash_flow_events')
    op.drop_index(op.f('ix_cash_flow_events_user_id'), table_name='cash_flow_events')
    
    # Drop table
    op.drop_table('cash_flow_events')
