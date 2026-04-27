"""Test configuration and fixtures"""
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from redis.asyncio import Redis
from jose import jwt
from shared.models import Base, Affiliate, Offer
from shared.config import settings


# Test database URL (use separate test database)
TEST_DATABASE_URL = "postgresql+asyncpg://leads_user:leads_pass@postgres:5432/leads_test_db"


@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    from sqlalchemy.pool import NullPool
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()
        await session.close()


@pytest.fixture
async def redis_client() -> AsyncGenerator[Redis, None]:
    """Create Redis client for tests."""
    client = Redis.from_url(settings.redis_url, decode_responses=True)

    yield client

    # Clear test keys after test
    await client.flushdb()
    await client.aclose()


@pytest.fixture
async def test_affiliate(db_session: AsyncSession) -> Affiliate:
    """Create test affiliate."""
    affiliate = Affiliate(id=1, name="Test Affiliate")
    db_session.add(affiliate)
    await db_session.commit()
    await db_session.refresh(affiliate)

    yield affiliate

    # Ensure session is closed
    await db_session.close()


@pytest.fixture
async def test_offer(db_session: AsyncSession) -> Offer:
    """Create test offer."""
    offer = Offer(id=1, name="Test Product")
    db_session.add(offer)
    await db_session.commit()
    await db_session.refresh(offer)

    yield offer

    # Ensure session is closed
    await db_session.close()


@pytest.fixture
def auth_token(test_affiliate: Affiliate) -> str:
    """Generate valid JWT token for test affiliate."""
    token = jwt.encode(
        {"id": test_affiliate.id},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    return token


@pytest.fixture
def sample_lead_data(test_affiliate: Affiliate, test_offer: Offer) -> dict:
    """Sample lead data for testing."""
    return {
        "name": "John Doe",
        "phone": "+380123456789",
        "country": "UA",
        "offer_id": test_offer.id,
        "affiliate_id": test_affiliate.id
    }
