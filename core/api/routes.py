import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db
from core.dependencies import get_current_affiliate
from core.services.analytics_service import AnalyticsService

router = APIRouter()
logger = logging.getLogger("core.api")


@router.get(
    "/leads",
    summary="Get leads analytics",
    description="Get leads summary for affiliate grouped by date or offer",
    response_description="Analytics data with lead counts"
)
async def get_leads(
    date_from: date = Query(..., description="Start date (YYYY-MM-DD)"),
    date_to: date = Query(..., description="End date (YYYY-MM-DD)"),
    group: str = Query(..., regex="^(date|offer)$", description="Group by: 'date' or 'offer'"),
    affiliate_id: int = Depends(get_current_affiliate),
    db: AsyncSession = Depends(get_db)
):
    """
    Get leads analytics for the authenticated affiliate.

    - **date_from**: Start date for the report (inclusive)
    - **date_to**: End date for the report (inclusive)
    - **group**: Grouping method - 'date' for daily breakdown, 'offer' for breakdown by product
    """
    logger.info(
        f"Analytics request: affiliate_id={affiliate_id}, "
        f"date_from={date_from}, date_to={date_to}, group={group}"
    )

    # Validate date range
    if date_from > date_to:
        logger.warning(f"Invalid date range: {date_from} > {date_to}")
        raise HTTPException(
            status_code=400,
            detail="date_from must be less than or equal to date_to"
        )

    try:
        analytics_service = AnalyticsService()

        if group == "date":
            result = await analytics_service.get_leads_by_date(
                affiliate_id, date_from, date_to, db
            )
        else:  # group == "offer"
            result = await analytics_service.get_leads_by_offer(
                affiliate_id, date_from, date_to, db
            )

        logger.info(f"Analytics query completed: total_count={result['total_count']}")
        return result

    except Exception as e:
        logger.error(f"Analytics query failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
