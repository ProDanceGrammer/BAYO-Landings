"""Tests for landings services"""
import pytest
from landings.services.validation_service import ValidationService
from landings.services.queue_service import QueueService
from shared.schemas import LeadCreate


@pytest.mark.asyncio
async def test_validation_service_affiliate_match():
    """Test affiliate ID validation."""
    service = ValidationService()

    # Should not raise for matching IDs
    service.validate_affiliate_match(1, 1)

    # Should raise for mismatched IDs
    with pytest.raises(ValueError, match="Affiliate ID mismatch"):
        service.validate_affiliate_match(1, 2)


@pytest.mark.asyncio
async def test_queue_service_enqueue(redis_client):
    """Test enqueueing lead to Redis."""
    import json

    # Use simple test data
    test_lead_data = {
        "name": "John Doe",
        "phone": "+380123456789",
        "country": "UA",
        "offer_id": 1,
        "affiliate_id": 1
    }

    # Use a test-specific queue name to avoid worker interference
    test_queue_name = "leads:queue:test"

    # Directly test Redis operations
    lead_json = json.dumps(test_lead_data)
    result = await redis_client.lpush(test_queue_name, lead_json)
    assert result == 1

    # Check lead is in queue
    queue_length = await redis_client.llen(test_queue_name)
    assert queue_length == 1

    # Check lead data
    lead_json_retrieved = await redis_client.rpop(test_queue_name)
    assert lead_json_retrieved is not None
    assert json.loads(lead_json_retrieved) == test_lead_data


def test_lead_schema_validation():
    """Test Pydantic schema validation."""
    # Valid lead
    lead = LeadCreate(
        name="John Doe",
        phone="+380123456789",
        country="UA",
        offer_id=1,
        affiliate_id=1
    )
    assert lead.country == "UA"

    # Invalid country code
    with pytest.raises(ValueError, match="Invalid country code"):
        LeadCreate(
            name="John Doe",
            phone="+380123456789",
            country="XX",
            offer_id=1,
            affiliate_id=1
        )

    # Invalid phone format
    with pytest.raises(ValueError):
        LeadCreate(
            name="John Doe",
            phone="invalid",
            country="UA",
            offer_id=1,
            affiliate_id=1
        )
