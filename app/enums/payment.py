"""Enums for the Payment domain."""
import enum


class PaymentType(str, enum.Enum):
    """Payment type — represents the business milestone."""

    DEPOSIT = "deposit"
    PRODUCTION = "production"
    FINAL = "final"


class PaymentMethod(str, enum.Enum):
    """Payment method — how the customer pays."""

    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    INSTAPAY = "instapay"
    CHEQUE = "cheque"
    OTHER = "other"


class PaymentStatus(str, enum.Enum):
    """Payment status values."""

    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
