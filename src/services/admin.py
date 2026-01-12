from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime, date
from ..models.user import User
from ..models.tool import Tool
from ..models.usage_log import UsageLog
from ..models.subscription import Subscription
from ..schemas.admin import AdminUserView, PlatformUsageStats, ToolCreate, ToolUpdate
from ..schemas.tool import ToolDetail


class AdminService:
    @staticmethod
    async def list_users(
        db_session: AsyncSession,
        skip: int = 0,
        limit: int = 20
    ) -> List[AdminUserView]:
        """
        List all users with pagination.
        
        Args:
            db_session: The database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            A list of user views
        """
        stmt = select(User).offset(skip).limit(limit)
        result = await db_session.execute(stmt)
        users = result.scalars().all()
        
        return [AdminUserView.from_orm(user) for user in users]
    
    @staticmethod
    async def create_tool(
        db_session: AsyncSession,
        tool_data: ToolCreate
    ) -> ToolDetail:
        """
        Create a new tool.
        
        Args:
            db_session: The database session
            tool_data: The tool creation data
            
        Returns:
            The created tool details
        """
        tool = Tool(
            name=tool_data.name,
            description=tool_data.description,
            api_endpoint=tool_data.api_endpoint,
            is_active=tool_data.is_active
        )
        
        db_session.add(tool)
        await db_session.commit()
        await db_session.refresh(tool)
        
        return ToolDetail.from_orm(tool)
    
    @staticmethod
    async def update_tool(
        db_session: AsyncSession,
        tool_id: str,
        tool_data: ToolUpdate
    ) -> Optional[ToolDetail]:
        """
        Update an existing tool.
        
        Args:
            db_session: The database session
            tool_id: The ID of the tool to update
            tool_data: The tool update data
            
        Returns:
            The updated tool details, or None if not found
        """
        stmt = select(Tool).where(Tool.id == tool_id)
        result = await db_session.execute(stmt)
        tool = result.scalar_one_or_none()
        
        if not tool:
            return None
        
        # Update fields if they are provided
        if tool_data.name is not None:
            tool.name = tool_data.name
        if tool_data.description is not None:
            tool.description = tool_data.description
        if tool_data.api_endpoint is not None:
            tool.api_endpoint = tool_data.api_endpoint
        if tool_data.is_active is not None:
            tool.is_active = tool_data.is_active
        
        await db_session.commit()
        await db_session.refresh(tool)
        
        return ToolDetail.from_orm(tool)
    
    @staticmethod
    async def delete_tool(
        db_session: AsyncSession,
        tool_id: str
    ) -> bool:
        """
        Delete a tool.
        
        Args:
            db_session: The database session
            tool_id: The ID of the tool to delete
            
        Returns:
            True if the tool was deleted, False otherwise
        """
        stmt = select(Tool).where(Tool.id == tool_id)
        result = await db_session.execute(stmt)
        tool = result.scalar_one_or_none()
        
        if not tool:
            return False
        
        await db_session.delete(tool)
        await db_session.commit()
        
        return True
    
    @staticmethod
    async def get_platform_stats(
        db_session: AsyncSession
    ) -> PlatformUsageStats:
        """
        Get platform-wide usage statistics.
        
        Args:
            db_session: The database session
            
        Returns:
            Platform usage statistics
        """
        from sqlalchemy import func
        
        # Count total users
        user_count_stmt = select(func.count(User.id))
        user_result = await db_session.execute(user_count_stmt)
        total_users = user_result.scalar()
        
        # Count active subscriptions
        active_sub_count_stmt = select(func.count(Subscription.id)).where(
            Subscription.status == "active"
        )
        active_sub_result = await db_session.execute(active_sub_count_stmt)
        active_subscriptions = active_sub_result.scalar()
        
        # Count total tools
        tool_count_stmt = select(func.count(Tool.id))
        tool_result = await db_session.execute(tool_count_stmt)
        total_tools = tool_result.scalar()
        
        # Count total usage logs
        usage_count_stmt = select(func.count(UsageLog.id))
        usage_result = await db_session.execute(usage_count_stmt)
        total_usage_logs = usage_result.scalar()
        
        # Get usage stats by tool
        tool_usage_stmt = select(
            Tool.id,
            Tool.name,
            func.count(UsageLog.id).label('usage_count'),
            func.sum(UsageLog.tokens_used).label('total_tokens')
        ).select_from(Tool.__table__.join(UsageLog, Tool.id == UsageLog.tool_id)).group_by(Tool.id, Tool.name)
        
        tool_usage_result = await db_session.execute(tool_usage_stmt)
        tool_usage_rows = tool_usage_result.fetchall()
        
        usage_stats_by_tool = [
            {
                "tool_id": row.id,
                "tool_name": row.name,
                "usage_count": row.usage_count,
                "total_tokens": row.total_tokens or 0
            }
            for row in tool_usage_rows
        ]
        
        # Get usage stats by day
        day_usage_stmt = select(
            func.date(UsageLog.timestamp).label('day'),
            func.count(UsageLog.id).label('usage_count'),
            func.sum(UsageLog.tokens_used).label('total_tokens')
        ).group_by(func.date(UsageLog.timestamp)).order_by(func.date(UsageLog.timestamp))
        
        day_usage_result = await db_session.execute(day_usage_stmt)
        day_usage_rows = day_usage_result.fetchall()
        
        usage_stats_by_day = [
            {
                "date": str(row.day),
                "usage_count": row.usage_count,
                "total_tokens": row.total_tokens or 0
            }
            for row in day_usage_rows
        ]
        
        return PlatformUsageStats(
            total_users=total_users,
            active_subscriptions=active_subscriptions,
            total_tools=total_tools,
            total_usage_logs=total_usage_logs,
            usage_stats_by_tool=usage_stats_by_tool,
            usage_stats_by_day=usage_stats_by_day
        )