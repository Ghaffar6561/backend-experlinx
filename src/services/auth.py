from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ..models.user import User
from ..core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from ..schemas.auth import UserRegistration, LoginRequest, TokenPair
from ..services.user import get_user_by_email, create_user
from datetime import timedelta
from ..core.config import settings
import uuid


class AuthService:
    @staticmethod
    async def register(db_session: AsyncSession, user_data: UserRegistration) -> User:
        """
        Register a new user.
        
        Args:
            db_session: The database session
            user_data: The user registration data
            
        Returns:
            The created User object
        """
        # Check if user with email already exists
        existing_user = await get_user_by_email(db_session, user_data.email)
        if existing_user:
            raise ValueError(f"User with email {user_data.email} already exists")
        
        # Hash the password
        password_hash = get_password_hash(user_data.password)
        
        # Create the user
        user = await create_user(
            db_session=db_session,
            name=user_data.name,
            email=user_data.email,
            password_hash=password_hash
        )
        
        return user
    
    @staticmethod
    async def login(db_session: AsyncSession, login_data: LoginRequest) -> tuple[User, TokenPair]:
        """
        Authenticate a user and return access and refresh tokens.
        
        Args:
            db_session: The database session
            login_data: The login credentials
            
        Returns:
            A tuple of (User object, TokenPair)
        """
        # Get user by email
        user = await get_user_by_email(db_session, login_data.email)
        if not user or not verify_password(login_data.password, user.password_hash):
            raise ValueError("Incorrect email or password")
        
        # Create access and refresh tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=refresh_token_expires
        )
        
        token_pair = TokenPair(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        return user, token_pair
    
    @staticmethod
    async def refresh_token(db_session: AsyncSession, refresh_token: str) -> Optional[TokenPair]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            db_session: The database session
            refresh_token: The refresh token
            
        Returns:
            A new TokenPair if the refresh is successful, None otherwise
        """
        # In a real implementation, we would check the refresh token against the database
        # For now, we'll just validate the token and create new ones
        # This is a simplified implementation that doesn't track refresh tokens in the database
        
        # TODO: Implement proper refresh token validation against the database
        # This would involve checking if the refresh token exists in the refresh_tokens table,
        # hasn't expired, and hasn't been revoked
        
        # For now, just validate the token and create new ones
        from ..core.security import verify_token
        token_data = verify_token(refresh_token)
        if not token_data:
            return None
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": token_data.user_id, "role": token_data.role},
            expires_delta=access_token_expires
        )
        
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = create_refresh_token(
            data={"sub": token_data.user_id, "role": token_data.role},
            expires_delta=refresh_token_expires
        )
        
        return TokenPair(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    
    @staticmethod
    async def logout(db_session: AsyncSession, user: User, refresh_token: str) -> bool:
        """
        Logout a user by revoking their refresh token.
        
        Args:
            db_session: The database session
            user: The user object
            refresh_token: The refresh token to revoke
            
        Returns:
            True if logout was successful, False otherwise
        """
        # In a real implementation, we would mark the refresh token as revoked in the database
        # For now, we'll just return True to indicate success
        # TODO: Implement proper refresh token revocation in the database
        
        return True
    
    @staticmethod
    async def request_password_reset(db_session: AsyncSession, email: str) -> bool:
        """
        Request a password reset for the given email.
        
        Args:
            db_session: The database session
            email: The email address to send the reset link to
            
        Returns:
            True if the request was processed (whether or not the email exists)
        """
        # In a real implementation, we would:
        # 1. Generate a password reset token
        # 2. Store it in the database
        # 3. Send an email with a reset link
        # For now, we'll just return True to indicate the request was processed
        
        # Find the user by email
        user = await get_user_by_email(db_session, email)
        if not user:
            # Return True even if the user doesn't exist to prevent email enumeration attacks
            return True
        
        # TODO: Implement password reset token generation and email sending
        return True
    
    @staticmethod
    async def reset_password(db_session: AsyncSession, token: str, new_password: str) -> bool:
        """
        Reset a user's password using a reset token.
        
        Args:
            db_session: The database session
            token: The password reset token
            new_password: The new password
            
        Returns:
            True if the password was reset, False otherwise
        """
        # In a real implementation, we would:
        # 1. Validate the reset token
        # 2. Hash the new password
        # 3. Update the user's password in the database
        # 4. Invalidate all refresh tokens for the user
        # For now, we'll just return False to indicate it's not implemented
        
        # TODO: Implement password reset using tokens
        return False