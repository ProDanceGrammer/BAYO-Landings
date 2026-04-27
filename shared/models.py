from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Affiliate(Base):
    """Affiliate (webmaster) who brings leads to the system."""

    __tablename__ = "affiliates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # Relationships
    leads = relationship("Lead", back_populates="affiliate")


class Offer(Base):
    """Product offer that leads are interested in."""

    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # Relationships
    leads = relationship("Lead", back_populates="offer")


class Lead(Base):
    """Lead (potential customer) from landing page."""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    country = Column(String(2), nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    offer = relationship("Offer", back_populates="leads")
    affiliate = relationship("Affiliate", back_populates="leads")