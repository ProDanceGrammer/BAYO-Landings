from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import pycountry


class LeadCreate(BaseModel):
    """Schema for creating a new lead."""

    name: str = Field(..., min_length=1, max_length=255, description="Lead's name")
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$', description="Lead's phone number in E.164 format")
    country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    offer_id: int = Field(..., gt=0, description="ID of the offer")
    affiliate_id: int = Field(..., gt=0, description="ID of the affiliate")

    @field_validator('country')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Validate that country is a valid ISO 3166-1 alpha-2 code."""
        v = v.upper()  # Normalize to uppercase

        country = pycountry.countries.get(alpha_2=v)
        if country is None:
            raise ValueError(
                f"Invalid country code: {v}. Must be ISO 3166-1 alpha-2 format."
            )

        return v


class LeadResponse(BaseModel):
    """Schema for lead response."""

    id: int
    name: str
    phone: str
    country: str
    offer_id: int
    affiliate_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OfferResponse(BaseModel):
    """Schema for offer response."""

    id: int
    name: str

    class Config:
        from_attributes = True


class AffiliateResponse(BaseModel):
    """Schema for affiliate response."""

    id: int
    name: str

    class Config:
        from_attributes = True