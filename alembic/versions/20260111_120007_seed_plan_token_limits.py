"""seed plan token limits

Revision ID: 20260111120007
Revises: 20260111120006
Create Date: 2026-01-11 12:00:07.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime

# revision identifiers
revision: str = '20260111120007'
down_revision: Union[str, None] = '20260111120006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This migration sets up default token limits for subscription plans
    # In a real application, this might involve creating a separate table for plan configurations
    # For now, we'll just add a note that these defaults are implemented in the code
    
    # The default token limits are:
    # - Free: 1,000 tokens/month
    # - Pro: 50,000 tokens/month
    # - Enterprise: 500,000 tokens/month
    #
    # These are implemented in the SubscriptionService class in src/services/subscription.py
    pass


def downgrade() -> None:
    # No downgrade needed for this migration
    pass