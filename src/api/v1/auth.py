from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from ...db.session import get_db_session
from ...schemas.auth import UserRegistration, LoginRequest, TokenPair
from ...schemas.common import ApiResponse
from ...services.auth import AuthService
from ...core.dependencies import security
from fastapi.security import HTTPAuthorizationCredentials


router = APIRouter()


@router.post("/register", response_model=ApiResponse[Any])
async def register(
    user_data: UserRegistration,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Register a new user.
    """
    try:
        user = await AuthService.register(db_session, user_data)
        return ApiResponse(data={"message": "User registered successfully", "user_id": str(user.id)})
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=ApiResponse[TokenPair])
async def login(
    login_data: LoginRequest,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Authenticate a user and return access and refresh tokens.
    """
    try:
        user, token_pair = await AuthService.login(db_session, login_data)
        return ApiResponse(data=token_pair)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=ApiResponse[TokenPair])
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Refresh an access token using a refresh token.
    """
    # Extract the refresh token from the Authorization header
    refresh_token_str = credentials.credentials
    
    token_pair = await AuthService.refresh_token(db_session, refresh_token_str)
    if not token_pair:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return ApiResponse(data=token_pair)


@router.post("/logout", response_model=ApiResponse[Any])
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Logout a user by revoking their refresh token.
    """
    # Extract the refresh token from the Authorization header
    refresh_token_str = credentials.credentials
    
    # Get current user (to validate the token and get user info)
    from ...core.dependencies import get_current_user
    current_user = await get_current_user(credentials, db_session)
    
    success = await AuthService.logout(db_session, current_user, refresh_token_str)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )
    
    return ApiResponse(data={"message": "Logged out successfully"})


@router.post("/password-reset", response_model=ApiResponse[Any])
async def request_password_reset(
    email: str,  # In a real app, this would be in the request body
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Request a password reset for the given email.
    """
    success = await AuthService.request_password_reset(db_session, email)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset request failed"
        )
    
    return ApiResponse(data={"message": "Password reset email sent if account exists"})


@router.post("/password-reset/{token}", response_model=ApiResponse[Any])
async def reset_password(
    token: str,
    new_password: str,  # In a real app, this would be in the request body
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Reset a user's password using a reset token.
    """
    success = await AuthService.reset_password(db_session, token, new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset failed"
        )
    
    return ApiResponse(data={"message": "Password reset successfully"})