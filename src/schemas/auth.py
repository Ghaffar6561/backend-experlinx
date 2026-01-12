from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import re


class UserRegistration(BaseModel):
    name: str
    email: EmailStr
    password: str

    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 1 or len(v.strip()) > 100:
            raise ValueError('Name must be between 1 and 100 characters')
        return v.strip()

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for mixed case, number, and special character
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str
    role: str