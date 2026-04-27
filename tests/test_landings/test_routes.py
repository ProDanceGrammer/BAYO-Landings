"""Tests for landings service routes"""
import pytest
from httpx import AsyncClient
from landings.main import app
from shared.database import get_db


@pytest.mark.asyncio
async def test_create_lead_success(auth_token, sample_lead_data, db_session):
    """Test successful lead creation."""

    # Override database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/lead",
                json=sample_lead_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_lead_invalid_country(auth_token, test_affiliate, test_offer, db_session):
    """Test lead creation with invalid country code."""

    # Override database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/lead",
                json={
                    "name": "John Doe",
                    "phone": "+380123456789",
                    "country": "XX",  # Invalid country code
                    "offer_id": test_offer.id,
                    "affiliate_id": test_affiliate.id
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        assert response.status_code == 422  # Validation error
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_lead_missing_auth():
    """Test lead creation without authentication."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/lead",
            json={
                "name": "John Doe",
                "phone": "+380123456789",
                "country": "UA",
                "offer_id": 1,
                "affiliate_id": 1
            }
        )

    assert response.status_code == 403  # Missing auth header


@pytest.mark.asyncio
async def test_create_lead_affiliate_mismatch(auth_token, test_affiliate, test_offer, db_session):
    """Test lead creation with mismatched affiliate_id."""

    # Override database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/lead",
                json={
                    "name": "John Doe",
                    "phone": "+380123456789",
                    "country": "UA",
                    "offer_id": test_offer.id,
                    "affiliate_id": 999  # Different from token
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        assert response.status_code == 400  # Validation error
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "landings"
