from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class AdminUserView(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlatformUsageStats(BaseModel):
    total_users: int
    active_subscriptions: int
    total_tools: int
    total_usage_logs: int
    usage_stats_by_tool: List[Dict[str, Any]]  # List of tool usage stats
    usage_stats_by_day: List[Dict[str, Any]]   # List of daily usage stats

    class Config:
        from_attributes = True


class ToolCreate(BaseModel):
    name: str
    description: str
    api_endpoint: str
    is_active: bool = True


class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    api_endpoint: Optional[str] = None
    is_active: Optional[bool] = None