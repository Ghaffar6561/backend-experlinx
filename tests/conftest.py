import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.db.base import Base
from src.main import app
from src.db.session import get_db_session


# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def create_test_database():
    """Create the test database and tables."""
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}  # Required for SQLite
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(create_test_database):
    """Create a database session for testing."""
    engine = create_test_database
    async_session = sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    """Create a test client with a database session override."""
    from fastapi.testclient import TestClient
    
    def override_get_db_session():
        yield db_session
    
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()