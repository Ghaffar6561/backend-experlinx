from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UsageLogEntry(BaseModel):
    id: str
    user_id: str
    tool_id: str
    timestamp: datetime
    tokens_used: int
    request_id: str
    response_status: str
    duration_ms: Optional[int] = None

    class Config:
        from_attributes = True


class UsageSummary(BaseModel):
    total_tokens_used: int
    total_requests: int
    avg_duration_ms: Optional[float] = None
    breakdown_by_tool: List[dict]  # List of dicts with tool_id and usage stats
    breakdown_by_day: List[dict]  # List of dicts with date and usage stats

    class Config:
        from_attributes = True