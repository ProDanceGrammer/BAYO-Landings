"""Tests for core services"""
import pytest
from core.services.lead_processor import LeadProcessor
from shared.models import Lead


@pytest.mark.asyncio
async def test_lead_processor_deduplication(db_session, redis_client, sample_lead_data):
    """Test lead deduplication logic."""
    processor = LeadProcessor()

    # First lead should be processed
    result1 = await processor.process_lead(sample_lead_data, db_session, redis_client)
    assert result1 is True

    # Same lead within 10 minutes should be skipped
    result2 = await processor.process_lead(sample_lead_data, db_session, redis_client)
    assert result2 is False

    # Verify only one lead in database
    from sqlalchemy import select
    result = await db_session.execute(select(Lead))
    leads = result.scalars().all()
    assert len(leads) == 1


@pytest.mark.asyncio
async def test_lead_processor_different_leads(db_session, redis_client, sample_lead_data):
    """Test processing different leads."""
    processor = LeadProcessor()

    # Process first lead
    result1 = await processor.process_lead(sample_lead_data, db_session, redis_client)
    assert result1 is True

    # Process different lead (different phone)
    different_lead = sample_lead_data.copy()
    different_lead["phone"] = "+380987654321"
    result2 = await processor.process_lead(different_lead, db_session, redis_client)
    assert result2 is True

    # Verify two leads in database
    from sqlalchemy import select
    result = await db_session.execute(select(Lead))
    leads = result.scalars().all()
    assert len(leads) == 2


@pytest.mark.asyncio
async def test_lead_processor_check_duplicate(db_session, redis_client, sample_lead_data):
    """Test duplicate checking."""
    processor = LeadProcessor()

    # Initially not a duplicate
    is_dup1 = await processor.check_duplicate(sample_lead_data, db_session, redis_client)
    assert is_dup1 is False

    # Process the lead
    await processor.process_lead(sample_lead_data, db_session, redis_client)

    # Now it's a duplicate
    is_dup2 = await processor.check_duplicate(sample_lead_data, db_session, redis_client)
    assert is_dup2 is True
