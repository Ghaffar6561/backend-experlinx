from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID
import uuid
import hashlib
from ..models.user import User
from ..models.api_key import APIKey
from ..schemas.user import UserProfile, UserUpdate, ApiKeyInfo, ApiKeyCreated


async def get_user_by_id(db_session: AsyncSession, user_id: str) -> Optional[User]:
    """
    Retrieve a user by their ID.

    Args:
        db_session: The database session
        user_id: The ID of the user to retrieve

    Returns:
        The User object if found, None otherwise
    """
    stmt = select(User).where(User.id == user_id)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_user_by_email(db_session: AsyncSession, email: str) -> Optional[User]:
    """
    Retrieve a user by their email address.

    Args:
        db_session: The database session
        email: The email address of the user to retrieve

    Returns:
        The User object if found, None otherwise
    """
    stmt = select(User).where(User.email == email)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def create_user(
    db_session: AsyncSession,
    name: str,
    email: str,
    password_hash: str,
    role: str = "user"
) -> User:
    """
    Create a new user.

    Args:
        db_session: The database session
        name: The user's name
        email: The user's email address
        password_hash: The hashed password
        role: The user's role (default: "user")

    Returns:
        The created User object
    """
    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        role=role
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class UserService:
    @staticmethod
    async def get_profile(db_session: AsyncSession, user: User) -> UserProfile:
        """
        Get the profile of the current user.

        Args:
            db_session: The database session
            user: The user object

        Returns:
            The user's profile information
        """
        return UserProfile.from_orm(user)

    @staticmethod
    async def update_profile(
        db_session: AsyncSession,
        user: User,
        update_data: UserUpdate
    ) -> User:
        """
        Update the profile of the current user.

        Args:
            db_session: The database session
            user: The user object
            update_data: The data to update

        Returns:
            The updated user object
        """
        # Update fields if they are provided
        if update_data.name is not None:
            user.name = update_data.name
        if update_data.email is not None:
            user.email = update_data.email

        await db_session.commit()
        await db_session.refresh(user)
        return user

    @staticmethod
    async def create_api_key(
        db_session: AsyncSession,
        user: User,
        name: str
    ) -> ApiKeyCreated:
        """
        Create a new API key for the user.

        Args:
            db_session: The database session
            user: The user object
            name: The name for the API key

        Returns:
            The created API key information (including the key itself)
        """
        # Generate a random API key
        import secrets
        api_key = f"jfui_{secrets.token_urlsafe(32)}"

        # Create the hash of the key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Get the first 8 characters as the prefix
        key_prefix = api_key[:8]

        # Create the API key record
        api_key_record = APIKey(
            user_id=user.id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            name=name,
            active=True
        )

        db_session.add(api_key_record)
        await db_session.commit()
        await db_session.refresh(api_key_record)

        # Return the API key with the full key (only shown once)
        return ApiKeyCreated(
            id=str(api_key_record.id),
            name=api_key_record.name,
            key=api_key,  # Full key shown only once
            created_at=api_key_record.created_at
        )

    @staticmethod
    async def list_api_keys(
        db_session: AsyncSession,
        user: User
    ) -> List[ApiKeyInfo]:
        """
        List all API keys for the user.

        Args:
            db_session: The database session
            user: The user object

        Returns:
            A list of API key information
        """
        stmt = select(APIKey).where(APIKey.user_id == user.id)
        result = await db_session.execute(stmt)
        api_keys = result.scalars().all()

        return [ApiKeyInfo.from_orm(key) for key in api_keys]

    @staticmethod
    async def revoke_api_key(
        db_session: AsyncSession,
        user: User,
        key_id: str
    ) -> bool:
        """
        Revoke an API key for the user.

        Args:
            db_session: The database session
            user: The user object
            key_id: The ID of the API key to revoke

        Returns:
            True if the key was revoked, False otherwise
        """
        stmt = select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == user.id
        )
        result = await db_session.execute(stmt)
        api_key = result.scalar_one_or_none()

        if not api_key:
            return False

        api_key.active = False
        await db_session.commit()
        return True