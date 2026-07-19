"""Enums for the Quotation domain."""
import enum


class QuotationStatus(str, enum.Enum):
    """Status values for a Quotation lifecycle."""

    DRAFT = "draft"
    WAITING_FOR_MEASUREMENT = "waiting_for_measurement"
    MEASURED = "measured"
    UNDER_NEGOTIATION = "under_negotiation"
    SENT = "sent"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
