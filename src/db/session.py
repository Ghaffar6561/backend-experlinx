from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from ..core.config import settings


# Create the async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Ensures connections are valid before use
)

# Create the async session maker
AsyncSessionFactory = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


async def get_db_session() -> AsyncSession:
    """
    Dependency function that yields a database session.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()