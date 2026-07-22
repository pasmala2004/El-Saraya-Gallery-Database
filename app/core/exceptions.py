"""
Domain exceptions for the ERP application.

These exceptions represent business/domain failures. They must NOT inherit
from FastAPI's HTTPException — API routes (or a global exception handler)
translate them into HTTP responses.

Usage
-----
    raise EntityNotFoundError("Customer", customer_id)
    raise DuplicateEntityError("Quotation", "quotation_number", "Q-2026-0001")
    raise ValidationError("quantity must be greater than zero")
    raise BusinessRuleViolation("Cannot create a Job from a draft Quotation")
"""
from __future__ import annotations

from typing import Any


class DomainError(Exception):
    """Base class for all domain-layer exceptions."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EntityNotFoundError(DomainError):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity_name: str, entity_id: Any) -> None:
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} with id={entity_id} was not found")


class DuplicateEntityError(DomainError):
    """Raised when creating/updating would violate a uniqueness rule."""

    def __init__(
        self,
        entity_name: str,
        field: str,
        value: Any,
        message: str | None = None,
    ) -> None:
        self.entity_name = entity_name
        self.field = field
        self.value = value
        super().__init__(
            message
            or f"{entity_name} with {field}={value!r} already exists"
        )


class ValidationError(DomainError):
    """Raised when input fails domain validation (beyond schema parsing)."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.field = field
        self.details = details or {}
        super().__init__(message)


class BusinessRuleViolation(DomainError):
    """Raised when an operation violates an explicit business rule."""

    def __init__(self, message: str, *, code: str | None = None) -> None:
        self.code = code
        super().__init__(message)


class DatabaseException(DomainError):
    """
    Raised when a database operation fails unexpectedly.
    
    Used for transaction failures, integrity violations, or other
    database-level errors that should trigger rollback.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
