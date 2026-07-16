"""Enums for the Job domain."""
import enum


class JobStatus(str, enum.Enum):
    """Status values for a Job."""

    PENDING = "pending"
    MEASURING = "measuring"
    IN_PRODUCTION = "in_production"
    READY_FOR_INSTALLATION = "ready_for_installation"
    INSTALLED = "installed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
