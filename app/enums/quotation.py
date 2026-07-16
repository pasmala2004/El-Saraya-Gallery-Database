"""Enums for the Quotation domain."""
import enum


class QuotationStatus(str, enum.Enum):
    """Status values for a Quotation."""

    DRAFT = "draft"
    SENT = "sent"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
