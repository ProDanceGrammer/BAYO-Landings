import logging
from datetime import date, timedelta
from typing import Dict, List, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models import Lead, Offer


class AnalyticsService:
    """Service for generating analytics reports."""

    def __init__(self):
        self.logger = logging.getLogger("core.analytics")

    async def get_leads_by_date(
        self,
        affiliate_id: int,
        date_from: date,
        date_to: date,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get leads grouped by date.

        Args:
            affiliate_id: ID of the affiliate
            date_from: Start date (inclusive)
            date_to: End date (inclusive)
            db_session: Database session

        Returns:
            dict: Leads grouped by date with counts
        """
        self.logger.info(
            f"Analytics query: affiliate_id={affiliate_id}, "
            f"date_from={date_from}, date_to={date_to}, group=date"
        )

        # Query leads grouped by date
        query = (
            select(
                func.date(Lead.created_at).label('date'),
                func.count(Lead.id).label('count')
            )
            .where(
                Lead.affiliate_id == affiliate_id,
                Lead.created_at >= date_from,
                Lead.created_at < date_to + timedelta(days=1)
            )
            .group_by(func.date(Lead.created_at))
            .order_by(func.date(Lead.created_at))
        )

        result = await db_session.execute(query)
        rows = result.all()

        # Format response
        data = []
        total_count = 0

        for row in rows:
            data.append({
                "date": row.date.isoformat(),
                "count": row.count
            })
            total_count += row.count

        return {
            "affiliate_id": affiliate_id,
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "group_by": "date",
            "total_count": total_count,
            "data": data
        }

    async def get_leads_by_offer(
        self,
        affiliate_id: int,
        date_from: date,
        date_to: date,
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get leads grouped by offer.

        Args:
            affiliate_id: ID of the affiliate
            date_from: Start date (inclusive)
            date_to: End date (inclusive)
            db_session: Database session

        Returns:
            dict: Leads grouped by offer with counts
        """
        self.logger.info(
            f"Analytics query: affiliate_id={affiliate_id}, "
            f"date_from={date_from}, date_to={date_to}, group=offer"
        )

        # Query leads grouped by offer
        query = (
            select(
                Lead.offer_id,
                Offer.name.label('offer_name'),
                func.count(Lead.id).label('count')
            )
            .join(Offer, Lead.offer_id == Offer.id)
            .where(
                Lead.affiliate_id == affiliate_id,
                Lead.created_at >= date_from,
                Lead.created_at < date_to + timedelta(days=1)
            )
            .group_by(Lead.offer_id, Offer.name)
            .order_by(Lead.offer_id)
        )

        result = await db_session.execute(query)
        rows = result.all()

        # Format response
        data = []
        total_count = 0

        for row in rows:
            data.append({
                "offer_id": row.offer_id,
                "offer_name": row.offer_name,
                "count": row.count
            })
            total_count += row.count

        return {
            "affiliate_id": affiliate_id,
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "group_by": "offer",
            "total_count": total_count,
            "data": data
        }
