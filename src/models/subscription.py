from enum import Enum
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..db.base import Base


class SubscriptionPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    plan = Column(String(20), nullable=False)  # Using string instead of enum for simplicity
    status = Column(String(20), nullable=False, default=SubscriptionStatus.ACTIVE.value)
    token_limit = Column(Integer, nullable=False)  # Tokens allowed per billing period
    tokens_used = Column(Integer, nullable=False, default=0)  # Tokens consumed this period
    period_start = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Subscription expiration
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship
    user = relationship("User", backref="subscription")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan='{self.plan}', status='{self.status}')>"