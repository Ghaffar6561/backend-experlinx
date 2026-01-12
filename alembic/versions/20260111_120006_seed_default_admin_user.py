"""seed default admin user

Revision ID: 20260111120006
Revises: 20260111120005
Create Date: 2026-01-11 12:00:06.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime
import os

# revision identifiers
revision: str = '20260111120006'
down_revision: Union[str, None] = '20260111120005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Hash the default admin password using bcrypt
    # For this migration, we'll use a placeholder hash
    # In a real application, you would hash the actual password
    import bcrypt
    
    admin_password = os.getenv("ADMIN_PASSWORD", "default_admin_password")
    password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Insert the default admin user
    admin_user_id = str(uuid.uuid4())
    op.execute(
        f"""
        INSERT INTO users (id, name, email, password_hash, role, created_at, updated_at)
        VALUES (
            '{admin_user_id}',
            'Admin User',
            'admin@joyfullhub.com',
            '{password_hash}',
            'admin',
            '{datetime.utcnow()}',
            '{datetime.utcnow()}'
        )
        """
    )
    
    # Also create a subscription for the admin user (free tier)
    op.execute(
        f"""
        INSERT INTO subscriptions (id, user_id, plan, status, token_limit, tokens_used, period_start, expires_at, created_at, updated_at)
        VALUES (
            '{str(uuid.uuid4())}',
            '{admin_user_id}',
            'free',
            'active',
            1000,
            0,
            '{datetime.utcnow()}',
            NULL,
            '{datetime.utcnow()}',
            '{datetime.utcnow()}'
        )
        """
    )


def downgrade() -> None:
    # Remove the admin user and their subscription
    op.execute(
        """
        DELETE FROM subscriptions 
        WHERE user_id IN (SELECT id FROM users WHERE email = 'admin@joyfullhub.com')
        """
    )
    op.execute(
        "DELETE FROM users WHERE email = 'admin@joyfullhub.com'"
    )