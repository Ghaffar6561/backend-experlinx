from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...db.session import get_db_session
from ...schemas.user import UserProfile, UserUpdate, ApiKeyInfo, ApiKeyCreated
from ...schemas.common import ApiResponse
from ...services.user import UserService
from ...core.dependencies import get_current_user
from ...models.user import User


router = APIRouter()


@router.get("/me", response_model=ApiResponse[UserProfile])
async def get_profile(
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Get the profile of the current user.
    """
    profile = await UserService.get_profile(db_session, current_user)
    return ApiResponse(data=profile)


@router.patch("/me", response_model=ApiResponse[UserProfile])
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Update the profile of the current user.
    """
    updated_user = await UserService.update_profile(db_session, current_user, update_data)
    profile = await UserService.get_profile(db_session, updated_user)
    return ApiResponse(data=profile)


@router.get("/me/api-keys", response_model=ApiResponse[List[ApiKeyInfo]])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    List all API keys for the current user.
    """
    api_keys = await UserService.list_api_keys(db_session, current_user)
    return ApiResponse(data=api_keys)


@router.post("/me/api-keys", response_model=ApiResponse[ApiKeyCreated])
async def create_api_key(
    name: str,  # In a real app, this would be in the request body
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Create a new API key for the current user.
    """
    api_key = await UserService.create_api_key(db_session, current_user, name)
    return ApiResponse(data=api_key)


@router.delete("/me/api-keys/{key_id}", response_model=ApiResponse[bool])
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Revoke an API key for the current user.
    """
    success = await UserService.revoke_api_key(db_session, current_user, key_id)
    return ApiResponse(data=success)