"""Shared API error response schema."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Consistent error body returned for domain and validation failures."""

    detail: str = Field(description="Human-readable error message.")
    code: str | None = Field(
        default=None,
        description="Machine-readable error code (exception class name).",
    )
    field: str | None = Field(
        default=None,
        description="Optional field associated with the error.",
    )
    extra: dict[str, Any] | None = Field(
        default=None,
        description="Optional structured details.",
    )
