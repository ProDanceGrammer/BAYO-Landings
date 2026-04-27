import logging
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.config import settings
from shared.models import Affiliate


class AuthService:
    """Service for handling JWT authentication."""

    def __init__(self):
        self.logger = logging.getLogger("shared.auth")

    def decode_token(self, token: str) -> int:
        """
        Decode JWT token and extract affiliate_id.

        Args:
            token: JWT token string

        Returns:
            int: Affiliate ID from token payload

        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
            affiliate_id = payload.get("id")

            if affiliate_id is None:
                raise JWTError("Token payload missing 'id' field")

            return int(affiliate_id)

        except JWTError as e:
            self.logger.warning(f"JWT decode failed: {str(e)}")
            raise

    async def verify_affiliate_exists(
        self,
        affiliate_id: int,
        db_session: AsyncSession
    ) -> bool:
        """
        Verify that affiliate exists in database.

        Args:
            affiliate_id: ID of the affiliate
            db_session: Database session

        Returns:
            bool: True if affiliate exists, False otherwise
        """
        result = await db_session.execute(
            select(Affiliate).where(Affiliate.id == affiliate_id)
        )
        affiliate = result.scalar_one_or_none()

        if affiliate is None:
            self.logger.warning(f"Affiliate not found: id={affiliate_id}")
            return False

        return True
