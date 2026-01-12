"""create tools table

Revision ID: 20260111120003
Revises: 20260111120002
Create Date: 2026-01-11 12:00:03.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '20260111120003'
down_revision: Union[str, None] = '20260111120002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the tools table
    op.create_table(
        'tools',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('api_endpoint', sa.String(length=500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create indexes
    op.create_index(op.f('ix_tools_name'), 'tools', ['name'], unique=True)
    op.create_index(op.f('ix_tools_is_active'), 'tools', ['is_active'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_tools_name'), table_name='tools')
    op.drop_index(op.f('ix_tools_is_active'), table_name='tools')
    
    # Drop the tools table
    op.drop_table('tools')