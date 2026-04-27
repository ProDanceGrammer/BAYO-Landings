import asyncio
import json
import logging
from redis.asyncio import Redis
from shared.config import settings
from shared.database import AsyncSessionLocal
from shared.logging_config import setup_logging
from core.services.lead_processor import LeadProcessor

# Setup logging
logger = setup_logging("core-worker")


async def main():
    """Main worker loop for processing leads from Redis queue."""
    logger.info("Worker starting up")

    # Initialize services
    lead_processor = LeadProcessor()
    redis_client = await lead_processor.get_redis_client()

    logger.info("Worker ready, waiting for leads...")

    while True:
        try:
            # Block and wait for lead from queue (5-second timeout)
            result = await redis_client.brpop("leads:queue", timeout=5)

            if result:
                _, lead_data_json = result
                lead_data = json.loads(lead_data_json)

                logger.info(
                    f"Processing lead from queue: name={lead_data.get('name', 'unknown')}, "
                    f"affiliate_id={lead_data.get('affiliate_id')}"
                )

                # Process lead with database session
                async with AsyncSessionLocal() as db_session:
                    success = await lead_processor.process_lead(
                        lead_data,
                        db_session,
                        redis_client
                    )

                    if success:
                        logger.info("Lead processing completed")
                    else:
                        logger.info("Lead skipped (duplicate)")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in queue: {str(e)}")

        except Exception as e:
            logger.error(f"Worker error: {str(e)}", exc_info=True)
            # Back off on error to avoid tight error loop
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker shutting down (KeyboardInterrupt)")
    except Exception as e:
        logger.critical(f"Worker crashed: {str(e)}", exc_info=True)
        raise