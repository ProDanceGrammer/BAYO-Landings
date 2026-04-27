import logging
import json
import hashlib
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from shared.config import settings
from shared.models import Lead


class LeadProcessor:
    """Service for processing leads from queue."""

    def __init__(self):
        self.logger = logging.getLogger("core.processor")
        self._redis_client = None

    async def get_redis_client(self) -> Redis:
        """Get or create Redis client."""
        if self._redis_client is None:
            self._redis_client = Redis.from_url(
                settings.redis_url,
                decode_responses=True
            )
        return self._redis_client

    def _generate_dedup_key(self, lead_data: dict) -> str:
        """
        Generate deduplication key from lead data.

        Args:
            lead_data: Lead data dictionary

        Returns:
            str: Redis key for deduplication
        """
        # Create hash from name + phone + offer_id + affiliate_id
        dedup_string = (
            f"{lead_data['name']}|{lead_data['phone']}|"
            f"{lead_data['offer_id']}|{lead_data['affiliate_id']}"
        )
        dedup_hash = hashlib.md5(dedup_string.encode()).hexdigest()
        return f"lead:dedup:{dedup_hash}"

    async def check_duplicate(
        self,
        lead_data: dict,
        db_session: AsyncSession,
        redis_client: Redis
    ) -> bool:
        """
        Check if lead is a duplicate within 10-minute window.

        Args:
            lead_data: Lead data dictionary
            db_session: Database session (unused, kept for interface consistency)
            redis_client: Redis client

        Returns:
            bool: True if duplicate, False otherwise
        """
        dedup_key = self._generate_dedup_key(lead_data)

        # Check if key exists in Redis
        exists = await redis_client.exists(dedup_key)

        if exists:
            self.logger.info(
                f"Duplicate detected: name={lead_data['name']}, "
                f"phone={lead_data['phone']}, offer_id={lead_data['offer_id']}"
            )
            return True

        return False

    async def process_lead(
        self,
        lead_data: dict,
        db_session: AsyncSession,
        redis_client: Redis
    ) -> bool:
        """
        Process lead: check for duplicates and save to database.

        Args:
            lead_data: Lead data dictionary
            db_session: Database session
            redis_client: Redis client

        Returns:
            bool: True if lead was processed, False if skipped (duplicate)

        Raises:
            Exception: If database operation fails
        """
        # Check for duplicate
        if await self.check_duplicate(lead_data, db_session, redis_client):
            self.logger.info(
                f"Duplicate lead skipped: name={lead_data['name']}, "
                f"phone={lead_data['phone']}"
            )
            return False

        try:
            # Create lead record
            lead = Lead(**lead_data)
            db_session.add(lead)
            await db_session.commit()
            await db_session.refresh(lead)

            # Set deduplication key with 10-minute TTL
            dedup_key = self._generate_dedup_key(lead_data)
            await redis_client.setex(dedup_key, 600, "1")  # 600 seconds = 10 minutes

            self.logger.info(
                f"Lead processed: id={lead.id}, affiliate_id={lead.affiliate_id}, "
                f"offer_id={lead.offer_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to process lead: {str(e)}", exc_info=True)
            await db_session.rollback()
            raise

    async def close(self):
        """Close Redis connection."""
        if self._redis_client:
            await self._redis_client.close()
