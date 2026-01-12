from pydantic import BaseModel
from typing import Generic, Optional, TypeVar, Dict, Any
from uuid import UUID


T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    error: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


class ApiError(BaseModel):
    code: str
    message: str
    details: Optional[list] = None


class PaginationMeta(BaseModel):
    offset: int
    limit: int
    total: int