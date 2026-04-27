import logging
from fastapi import APIRouter, Depends, HTTPException
from shared.schemas import LeadCreate
from landings.dependencies import get_current_affiliate
from landings.services.validation_service import ValidationService
from landings.services.queue_service import QueueService

router = APIRouter()
logger = logging.getLogger("landings.api")


@router.post(
    "/lead",
    status_code=200,
    summary="Submit a new lead",
    description="Accept lead data from landing page and queue for processing",
    response_description="Lead accepted successfully"
)
async def create_lead(
    lead: LeadCreate,
    affiliate_id: int = Depends(get_current_affiliate)
):
    """
    Accept a new lead from landing page.

    - **name**: Lead's full name
    - **phone**: Phone number in E.164 format (e.g., +380123456789)
    - **country**: ISO 3166-1 alpha-2 country code (e.g., UA, US, GB)
    - **offer_id**: ID of the product offer
    - **affiliate_id**: ID of the affiliate (must match token)
    """
    logger.info(f"Received lead request: affiliate_id={affiliate_id}")

    try:
        # Validate affiliate_id matches token
        validation_service = ValidationService()
        validation_service.validate_affiliate_match(affiliate_id, lead.affiliate_id)
        validation_service.validate_lead_data(lead)

        # Enqueue lead to Redis
        queue_service = QueueService()
        await queue_service.enqueue_lead(lead.model_dump())

        logger.info(
            f"Lead accepted: affiliate_id={affiliate_id}, "
            f"offer_id={lead.offer_id}, name={lead.name}"
        )

        return {"status": "accepted", "message": "Lead queued for processing"}

    except ValueError as e:
        logger.warning(f"Validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
