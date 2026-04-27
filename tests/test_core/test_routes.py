"""Tests for core service routes"""
import pytest
from datetime import date
from httpx import AsyncClient
from core.main import app
from shared.database import get_db


@pytest.mark.asyncio
async def test_get_leads_by_date(auth_token, test_affiliate, test_offer, db_session):
    """Test getting leads grouped by date."""

    # Override database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/leads",
                params={
                    "date_from": "2026-04-01",
                    "date_to": "2026-04-30",
                    "group": "date"
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["group_by"] == "date"
        assert data["affiliate_id"] == test_affiliate.id
        assert "data" in data
        assert "total_count" in data
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_leads_by_offer(auth_token, test_affiliate, test_offer, db_session):
    """Test getting leads grouped by offer."""

    # Override database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/leads",
                params={
                    "date_from": "2026-04-01",
                    "date_to": "2026-04-30",
                    "group": "offer"
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["group_by"] == "offer"
        assert data["affiliate_id"] == test_affiliate.id
        assert "data" in data
        assert "total_count" in data
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_leads_invalid_date_range(auth_token, db_session):
    """Test getting leads with invalid date range."""

    # Override database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/leads",
                params={
                    "date_from": "2026-04-30",
                    "date_to": "2026-04-01",  # End before start
                    "group": "date"
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_leads_invalid_group(auth_token, db_session):
    """Test getting leads with invalid group parameter."""

    # Override database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/leads",
                params={
                    "date_from": "2026-04-01",
                    "date_to": "2026-04-30",
                    "group": "invalid"  # Invalid group
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        assert response.status_code == 422  # Validation error
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
    assert data["service"] == "core-api"
