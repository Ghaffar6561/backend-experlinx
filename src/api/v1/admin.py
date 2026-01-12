from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...db.session import get_db_session
from ...schemas.admin import AdminUserView, PlatformUsageStats, ToolCreate, ToolUpdate
from ...schemas.common import ApiResponse
from ...schemas.tool import ToolDetail
from ...services.admin import AdminService
from ...core.dependencies import get_current_user, require_role
from ...models.user import User


router = APIRouter()


@router.get("/users", response_model=ApiResponse[List[AdminUserView]])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_role(["admin"])),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    List all users with pagination (admin only).
    """
    users = await AdminService.list_users(db_session, skip=skip, limit=limit)
    return ApiResponse(data=users)


@router.post("/tools", response_model=ApiResponse[ToolDetail])
async def create_tool(
    tool_data: ToolCreate,
    current_user: User = Depends(require_role(["admin"])),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Create a new tool (admin only).
    """
    tool = await AdminService.create_tool(db_session, tool_data)
    return ApiResponse(data=tool)


@router.patch("/tools/{tool_id}", response_model=ApiResponse[ToolDetail])
async def update_tool(
    tool_id: str,
    tool_data: ToolUpdate,
    current_user: User = Depends(require_role(["admin"])),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Update an existing tool (admin only).
    """
    tool = await AdminService.update_tool(db_session, tool_id, tool_data)
    if not tool:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return ApiResponse(data=tool)


@router.delete("/tools/{tool_id}", response_model=ApiResponse[bool])
async def delete_tool(
    tool_id: str,
    current_user: User = Depends(require_role(["admin"])),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Delete a tool (admin only).
    """
    success = await AdminService.delete_tool(db_session, tool_id)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return ApiResponse(data=success)


@router.get("/usage/stats", response_model=ApiResponse[PlatformUsageStats])
async def get_platform_stats(
    current_user: User = Depends(require_role(["admin"])),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Get platform-wide usage statistics (admin only).
    """
    stats = await AdminService.get_platform_stats(db_session)
    return ApiResponse(data=stats)