from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ToolSummary(BaseModel):
    id: str
    name: str
    description: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ToolDetail(ToolSummary):
    api_endpoint: str
    updated_at: datetime

    class Config:
        from_attributes = True


class ToolInvocationRequest(BaseModel):
    input: Dict[str, Any]


class ToolInvocationResult(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None