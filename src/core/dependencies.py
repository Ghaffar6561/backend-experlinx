from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from typing import Optional, Callable
from ..db.session import get_db_session
from ..models.user import User
from ..core.security import verify_token
from ..schemas.auth import TokenData
from ..services.user import get_user_by_id


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_session: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Dependency to get the current authenticated user from the JWT token.
    
    Args:
        credentials: The HTTP authorization credentials containing the JWT token
        db_session: The database session
    
    Returns:
        The authenticated User object
    
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_id(db_session, token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def require_role(required_roles: list[str]) -> Callable:
    """
    Factory function to create a dependency that checks if the current user has one of the required roles.

    Args:
        required_roles: List of roles that are allowed to access the endpoint

    Returns:
        A dependency function that checks the user's role
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted",
            )
        return current_user

    return role_checker


from ..models.api_key import APIKey
from sqlalchemy.future import select


async def get_api_key_user(
    request: Request,
    db_session: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """
    Dependency to get the current user from an API key header.

    Args:
        request: The incoming request
        db_session: The database session

    Returns:
        The authenticated User object or None if no API key is provided
    """
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None

    # Hash the provided API key to compare with stored hash
    import hashlib
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Look up the API key in the database
    stmt = select(APIKey).join(User).where(
        APIKey.key_hash == key_hash,
        APIKey.active == True
    ).options(selectinload(APIKey.user))

    result = await db_session.execute(stmt)
    api_key_record = result.scalar_one_or_none()

    if not api_key_record or not api_key_record.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"},
        )

    # Update the last used timestamp
    api_key_record.last_used_at = func.now()
    await db_session.commit()

    return api_key_record.user