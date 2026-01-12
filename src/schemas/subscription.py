from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class SubscriptionPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SubscriptionPlanInfo(BaseModel):
    plan: SubscriptionPlan
    token_limit: int
    price_monthly: Optional[float] = None  # Price in USD, None for free tier

    class Config:
        use_enum_values = True


class SubscriptionDetail(BaseModel):
    id: str
    plan: SubscriptionPlan
    status: SubscriptionStatus
    token_limit: int
    tokens_used: int
    period_start: datetime
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True