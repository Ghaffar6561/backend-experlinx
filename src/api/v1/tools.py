from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...db.session import get_db_session
from ...schemas.tool import ToolSummary, ToolDetail, ToolInvocationRequest, ToolInvocationResult
from ...schemas.common import ApiResponse
from ...services.tool import ToolService
from ...core.dependencies import get_current_user
from ...models.user import User


router = APIRouter()


@router.get("/", response_model=ApiResponse[List[ToolSummary]])
async def list_tools(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    List available tools with pagination.
    """
    tools = await ToolService.list_tools(db_session, skip=skip, limit=limit)
    return ApiResponse(data=tools)


@router.get("/{tool_id}", response_model=ApiResponse[ToolDetail])
async def get_tool(
    tool_id: str,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Get detailed information about a specific tool.
    """
    tool = await ToolService.get_tool(db_session, tool_id)
    if not tool:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return ApiResponse(data=tool)


@router.post("/{tool_id}/invoke", response_model=ApiResponse[ToolInvocationResult])
async def invoke_tool(
    tool_id: str,
    invocation_request: ToolInvocationRequest,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Invoke a tool with the given input.
    """
    result = await ToolService.invoke_tool(db_session, current_user, tool_id, invocation_request)
    return ApiResponse(data=result)