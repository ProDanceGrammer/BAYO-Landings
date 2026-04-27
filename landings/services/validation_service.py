import logging
from shared.schemas import LeadCreate


class ValidationService:
    """Service for validating lead data."""

    def __init__(self):
        self.logger = logging.getLogger("landings.validation")

    def validate_affiliate_match(
        self,
        token_affiliate_id: int,
        lead_affiliate_id: int
    ) -> None:
        """
        Validate that affiliate_id in token matches affiliate_id in lead data.

        Args:
            token_affiliate_id: Affiliate ID from JWT token
            lead_affiliate_id: Affiliate ID from lead data

        Raises:
            ValueError: If affiliate IDs don't match
        """
        if token_affiliate_id != lead_affiliate_id:
            self.logger.warning(
                f"Affiliate ID mismatch: token={token_affiliate_id}, "
                f"lead={lead_affiliate_id}"
            )
            raise ValueError(
                f"Affiliate ID mismatch. Token contains {token_affiliate_id}, "
                f"but lead data contains {lead_affiliate_id}"
            )

    def validate_lead_data(self, lead: LeadCreate) -> None:
        """
        Perform additional business validation on lead data.

        Note: Basic validation (format, required fields) is handled by Pydantic.
        This method is for additional business rules if needed.

        Args:
            lead: Lead data to validate

        Raises:
            ValueError: If validation fails
        """
        # Pydantic already validates:
        # - name: min_length=1, max_length=255
        # - phone: E.164 format
        # - country: ISO 3166-1 alpha-2 (via pycountry)
        # - offer_id, affiliate_id: positive integers

        # Additional business rules can be added here if needed
        pass
