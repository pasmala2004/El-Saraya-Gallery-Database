"""Map domain exceptions to HTTP responses (no SQLAlchemy leakage)."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    BusinessRuleViolation,
    DomainError,
    DuplicateEntityError,
    EntityNotFoundError,
    ValidationError,
)
from app.schemas.errors import ErrorResponse


def _error_body(
    *,
    detail: str,
    code: str,
    field: str | None = None,
    extra: dict | None = None,
) -> dict:
    return ErrorResponse(
        detail=detail,
        code=code,
        field=field,
        extra=extra,
    ).model_dump(exclude_none=True)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach domain → HTTP exception handlers to the FastAPI app."""

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(
        _request: Request,
        exc: EntityNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content=_error_body(
                detail=exc.message,
                code="EntityNotFoundError",
                extra={"entity": exc.entity_name, "id": str(exc.entity_id)},
            ),
        )

    @app.exception_handler(DuplicateEntityError)
    async def duplicate_entity_handler(
        _request: Request,
        exc: DuplicateEntityError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content=_error_body(
                detail=exc.message,
                code="DuplicateEntityError",
                field=exc.field,
                extra={"entity": exc.entity_name, "value": str(exc.value)},
            ),
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(
        _request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=_error_body(
                detail=exc.message,
                code="ValidationError",
                field=exc.field,
                extra=exc.details or None,
            ),
        )

    @app.exception_handler(BusinessRuleViolation)
    async def business_rule_handler(
        _request: Request,
        exc: BusinessRuleViolation,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_body(
                detail=exc.message,
                code=exc.code or "BusinessRuleViolation",
            ),
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(
        _request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        """Fallback for any other domain error."""
        return JSONResponse(
            status_code=400,
            content=_error_body(detail=exc.message, code=type(exc).__name__),
        )
