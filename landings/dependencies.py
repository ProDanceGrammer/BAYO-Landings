import logging
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db
from shared.services.auth_service import AuthService

logger = logging.getLogger("landings.dependencies")

# Security scheme for Swagger UI
security = HTTPBearer()


async def get_auth_service() -> AuthService:
    """Dependency for getting AuthService instance."""
    return AuthService()


async def get_current_affiliate(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> int:
    """
    Dependency for extracting and validating affiliate from JWT token.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session
        auth_service: Authentication service

    Returns:
        int: Affiliate ID from token

    Raises:
        HTTPException: If authentication fails
    """
    try:
        token = credentials.credentials

        # Decode token and extract affiliate_id
        affiliate_id = auth_service.decode_token(token)

        # Verify affiliate exists in database
        if not await auth_service.verify_affiliate_exists(affiliate_id, db):
            raise HTTPException(
                status_code=401,
                detail="Invalid affiliate"
            )

        logger.debug(f"Authentication successful: affiliate_id={affiliate_id}")
        return affiliate_id

    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
