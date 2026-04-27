"""Script to seed database with test data for development and testing."""
import asyncio
from jose import jwt
from shared.database import AsyncSessionLocal
from shared.models import Affiliate, Offer
from shared.config import settings


async def seed_data():
    """Seed database with test affiliates and offers."""
    async with AsyncSessionLocal() as session:
        # Create test affiliates
        affiliates = [
            Affiliate(id=1, name="Test Affiliate 1"),
            Affiliate(id=2, name="Test Affiliate 2"),
            Affiliate(id=3, name="Demo Affiliate"),
        ]

        # Create test offers
        offers = [
            Offer(id=1, name="Premium Product"),
            Offer(id=2, name="Standard Product"),
            Offer(id=3, name="Basic Product"),
        ]

        # Use merge to handle existing records (upsert)
        for affiliate in affiliates:
            await session.merge(affiliate)

        for offer in offers:
            await session.merge(offer)

        await session.commit()

        print("Database seeded successfully!")
        print("\nTest Affiliates:")
        for affiliate in affiliates:
            print(f"  - ID: {affiliate.id}, Name: {affiliate.name}")

        print("\nTest Offers:")
        for offer in offers:
            print(f"  - ID: {offer.id}, Name: {offer.name}")

        # Generate JWT tokens for testing
        print("\nJWT Tokens for testing:")
        for affiliate in affiliates:
            token = jwt.encode(
                {"id": affiliate.id},
                settings.jwt_secret,
                algorithm=settings.jwt_algorithm
            )
            print(f"\nAffiliate {affiliate.id} ({affiliate.name}):")
            print(f"  Token: {token}")


if __name__ == "__main__":
    print("Seeding database with test data...\n")
    asyncio.run(seed_data())
