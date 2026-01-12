from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
import uuid
from ..models.usage_log import UsageLog, UsageResponseStatus
from ..schemas.usage import UsageLogEntry, UsageSummary


async def log_tool_invocation(
    db_session: AsyncSession,
    user_id: str,
    tool_id: str,
    tokens_used: int,
    duration_ms: Optional[int] = None,
    response_status: str = "success"
) -> UsageLog:
    """
    Log a tool invocation in the usage logs.

    Args:
        db_session: The database session
        user_id: The ID of the user who invoked the tool
        tool_id: The ID of the tool that was invoked
        tokens_used: The number of tokens consumed by the invocation
        duration_ms: The duration of the invocation in milliseconds
        response_status: The status of the response (success, error, timeout)

    Returns:
        The created UsageLog record
    """
    # Generate a request ID for tracing
    import uuid
    request_id = str(uuid.uuid4())

    usage_log = UsageLog(
        user_id=user_id,
        tool_id=tool_id,
        tokens_used=tokens_used,
        request_id=request_id,
        response_status=response_status,
        duration_ms=duration_ms
    )

    db_session.add(usage_log)
    await db_session.commit()
    await db_session.refresh(usage_log)

    return usage_log


async def get_usage_history(
    db_session: AsyncSession,
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 20
) -> List[UsageLogEntry]:
    """
    Get usage history for a user with optional date filtering.

    Args:
        db_session: The database session
        user_id: The ID of the user
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        A list of usage log entries
    """
    stmt = select(UsageLog).where(UsageLog.user_id == user_id)

    if start_date:
        stmt = stmt.where(UsageLog.timestamp >= start_date)

    if end_date:
        stmt = stmt.where(UsageLog.timestamp <= end_date)

    stmt = stmt.order_by(UsageLog.timestamp.desc()).offset(skip).limit(limit)

    result = await db_session.execute(stmt)
    usage_logs = result.scalars().all()

    return [UsageLogEntry.from_orm(log) for log in usage_logs]


async def get_usage_summary(
    db_session: AsyncSession,
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> UsageSummary:
    """
    Get usage summary for a user with optional date filtering.

    Args:
        db_session: The database session
        user_id: The ID of the user
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering

    Returns:
        Usage summary with aggregated statistics
    """
    from sqlalchemy import func, case

    # Base query with filters
    base_query = select(UsageLog).where(UsageLog.user_id == user_id)

    if start_date:
        base_query = base_query.where(UsageLog.timestamp >= start_date)

    if end_date:
        base_query = base_query.where(UsageLog.timestamp <= end_date)

    # Query for totals
    stmt = select(
        func.sum(UsageLog.tokens_used).label('total_tokens'),
        func.count(UsageLog.id).label('total_requests'),
        func.avg(UsageLog.duration_ms).label('avg_duration')
    ).select_from(base_query.subquery())

    result = await db_session.execute(stmt)
    row = result.fetchone()

    total_tokens = row.total_tokens or 0
    total_requests = row.total_requests or 0
    avg_duration = float(row.avg_duration) if row.avg_duration else None

    # Query for breakdown by tool
    tool_breakdown_stmt = select(
        UsageLog.tool_id,
        func.sum(UsageLog.tokens_used).label('tokens_used'),
        func.count(UsageLog.id).label('request_count'),
        func.avg(UsageLog.duration_ms).label('avg_duration')
    ).where(UsageLog.user_id == user_id)

    if start_date:
        tool_breakdown_stmt = tool_breakdown_stmt.where(UsageLog.timestamp >= start_date)

    if end_date:
        tool_breakdown_stmt = tool_breakdown_stmt.where(UsageLog.timestamp <= end_date)

    tool_breakdown_stmt = tool_breakdown_stmt.group_by(UsageLog.tool_id)

    tool_result = await db_session.execute(tool_breakdown_stmt)
    tool_rows = tool_result.fetchall()

    breakdown_by_tool = [
        {
            "tool_id": row.tool_id,
            "tokens_used": row.tokens_used or 0,
            "request_count": row.request_count or 0,
            "avg_duration": float(row.avg_duration) if row.avg_duration else None
        }
        for row in tool_rows
    ]

    # Query for breakdown by day
    day_breakdown_stmt = select(
        func.date(UsageLog.timestamp).label('day'),
        func.sum(UsageLog.tokens_used).label('tokens_used'),
        func.count(UsageLog.id).label('request_count'),
        func.avg(UsageLog.duration_ms).label('avg_duration')
    ).where(UsageLog.user_id == user_id)

    if start_date:
        day_breakdown_stmt = day_breakdown_stmt.where(UsageLog.timestamp >= start_date)

    if end_date:
        day_breakdown_stmt = day_breakdown_stmt.where(UsageLog.timestamp <= end_date)

    day_breakdown_stmt = day_breakdown_stmt.group_by(func.date(UsageLog.timestamp)).order_by(func.date(UsageLog.timestamp))

    day_result = await db_session.execute(day_breakdown_stmt)
    day_rows = day_result.fetchall()

    breakdown_by_day = [
        {
            "date": str(row.day),
            "tokens_used": row.tokens_used or 0,
            "request_count": row.request_count or 0,
            "avg_duration": float(row.avg_duration) if row.avg_duration else None
        }
        for row in day_rows
    ]

    return UsageSummary(
        total_tokens_used=total_tokens,
        total_requests=total_requests,
        avg_duration_ms=avg_duration,
        breakdown_by_tool=breakdown_by_tool,
        breakdown_by_day=breakdown_by_day
    )