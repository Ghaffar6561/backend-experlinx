from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
import re


class UserProfile(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) < 1 or len(v.strip()) > 100:
                raise ValueError('Name must be between 1 and 100 characters')
            return v.strip()
        return v


class ApiKeyInfo(BaseModel):
    id: str
    name: str
    key_prefix: str
    active: bool
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApiKeyCreated(BaseModel):
    id: str
    name: str
    key: str  # Full key shown only once at creation
    created_at: datetime

    class Config:
        from_attributes = True