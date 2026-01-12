"""create usage logs table

Revision ID: 20260111120005
Revises: 20260111120004
Create Date: 2026-01-11 12:00:05.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '20260111120005'
down_revision: Union[str, None] = '20260111120004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the usage_logs table
    op.create_table(
        'usage_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tool_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=False),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('response_status', sa.String(length=20), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tool_id'], ['tools.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_usage_logs_user_id'), 'usage_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_usage_logs_tool_id'), 'usage_logs', ['tool_id'], unique=False)
    op.create_index(op.f('ix_usage_logs_timestamp'), 'usage_logs', ['timestamp'], unique=False)
    op.create_index(op.f('ix_usage_logs_user_timestamp'), 'usage_logs', ['user_id', 'timestamp'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_usage_logs_user_id'), table_name='usage_logs')
    op.drop_index(op.f('ix_usage_logs_tool_id'), table_name='usage_logs')
    op.drop_index(op.f('ix_usage_logs_timestamp'), table_name='usage_logs')
    op.drop_index(op.f('ix_usage_logs_user_timestamp'), table_name='usage_logs')
    
    # Drop the usage_logs table
    op.drop_table('usage_logs')