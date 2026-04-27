import logging
import json
from redis.asyncio import Redis
from shared.config import settings


class QueueService:
    """Service for managing Redis queue operations."""

    def __init__(self):
        self.logger = logging.getLogger("landings.queue")
        self._redis_client = None

    async def get_redis_client(self) -> Redis:
        """Get or create Redis client."""
        if self._redis_client is None:
            self._redis_client = Redis.from_url(
                settings.redis_url,
                decode_responses=True
            )
        return self._redis_client

    async def enqueue_lead(self, lead_data: dict) -> None:
        """
        Enqueue lead data to Redis queue.

        Args:
            lead_data: Lead data dictionary

        Raises:
            Exception: If Redis operation fails
        """
        try:
            redis_client = await self.get_redis_client()
            lead_json = json.dumps(lead_data)

            await redis_client.lpush("leads:queue", lead_json)

            self.logger.info(
                f"Lead enqueued: affiliate_id={lead_data.get('affiliate_id')}, "
                f"offer_id={lead_data.get('offer_id')}"
            )

        except Exception as e:
            self.logger.error(f"Failed to enqueue lead: {str(e)}", exc_info=True)
            raise

    async def close(self):
        """Close Redis connection."""
        if self._redis_client:
            await self._redis_client.close()
