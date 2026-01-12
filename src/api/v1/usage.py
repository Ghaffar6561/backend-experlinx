from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from ...db.session import get_db_session
from ...schemas.usage import UsageLogEntry, UsageSummary
from ...schemas.common import ApiResponse
from ...services.usage import get_usage_history, get_usage_summary
from ...core.dependencies import get_current_user
from ...models.user import User


router = APIRouter()


@router.get("/", response_model=ApiResponse[List[UsageLogEntry]])
async def get_usage_history(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Get usage history for the current user with optional date filtering.
    """
    usage_logs = await get_usage_history(
        db_session, 
        current_user.id, 
        start_date=start_date, 
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return ApiResponse(data=usage_logs)


@router.get("/summary", response_model=ApiResponse[UsageSummary])
async def get_usage_summary_endpoint(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Get usage summary for the current user with optional date filtering.
    """
    summary = await get_usage_summary(
        db_session,
        current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    return ApiResponse(data=summary)