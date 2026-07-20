"""Payment API routes — payment management for jobs."""
from __future__ import annotations

import uuid
from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT
from app.core.query import Pagination, Sorting
from app.db.session import get_db
from app.enums.payment import PaymentMethod, PaymentStatus, PaymentType
from app.repositories.job import JobRepository
from app.repositories.payment import PaymentFilters, PaymentRepository
from app.schemas.errors import ErrorResponse
from app.schemas.payment import (
    PaymentCreate,
    PaymentListResponse,
    PaymentRead,
    PaymentStatusUpdate,
    PaymentUpdate,
)
from app.services.payment import PaymentService

router = APIRouter(tags=["payments"])


def get_payment_service(
    session: AsyncSession = Depends(get_db),
) -> PaymentService:
    """Wire payment and job repositories."""
    return PaymentService(
        session,
        PaymentRepository(session),
        JobRepository(session),
    )


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

@router.get(
    "/jobs/{job_id}/payments",
    response_model=PaymentListResponse,
    summary="List payments for a job",
    description=(
        "Paginated payment list for a specific job. "
        "Sort by: id, payment_order, payment_type, payment_method, percentage, "
        "amount, due_date, paid_date, status, created_at, updated_at."
    ),
    responses={404: {"model": ErrorResponse}},
)
async def list_job_payments(
    job_id: uuid.UUID,
    service: Annotated[PaymentService, Depends(get_payment_service)],
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_LIMIT)] = DEFAULT_PAGE_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    sort_by: Annotated[str, Query()] = "payment_order",
    sort_order: Annotated[Literal["asc", "desc"], Query()] = "asc",
) -> PaymentListResponse:
    pagination = Pagination(limit=limit, offset=offset)
    sorting = Sorting(sort_by=sort_by, sort_order=sort_order)
    items, total = await service.list_job_payments(
        job_id,
        pagination=pagination,
        sorting=sorting,
    )
    return PaymentListResponse(
        items=[PaymentRead.model_validate(i) for i in items],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentRead,
    summary="Get payment by ID",
    description="Return a single payment by UUID.",
    responses={404: {"model": ErrorResponse}},
)
async def get_payment(
    payment_id: uuid.UUID,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> PaymentRead:
    payment = await service.get_payment(payment_id)
    return PaymentRead.model_validate(payment)


@router.post(
    "/jobs/{job_id}/payments",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create payment",
    description=(
        "Create a payment for a job. "
        "**Business rules**:\n\n"
        "- Job must exist\n"
        "- payment_order auto-increments per job\n"
        "- 0 < percentage <= 100\n"
        "- amount >= 0\n"
        "- paid_date cannot be before due_date\n"
        "- payment_method required\n"
        "- payment_type required\n\n"
        "Payment starts in ``pending`` status unless paid_date is provided. "
        "Activity log entry created automatically."
    ),
    responses={
        201: {"description": "Payment created."},
        404: {"model": ErrorResponse, "description": "Job not found."},
        422: {"model": ErrorResponse, "description": "Validation error."},
    },
)
async def create_payment(
    job_id: uuid.UUID,
    body: PaymentCreate,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> PaymentRead:
    data = body.model_dump(exclude_none=True)
    data["job_id"] = job_id
    payment = await service.create_payment(data)
    return PaymentRead.model_validate(payment)


@router.put(
    "/payments/{payment_id}",
    response_model=PaymentRead,
    summary="Update payment",
    description=(
        "Update payment details. Cannot update ``job_id`` or ``payment_order``. "
        "All fields are optional. Validates: "
        "0 < percentage <= 100, amount >= 0, paid_date not before due_date."
    ),
    responses={
        200: {"description": "Payment updated."},
        404: {"model": ErrorResponse, "description": "Payment not found."},
        422: {"model": ErrorResponse, "description": "Validation error."},
    },
)
async def update_payment(
    payment_id: uuid.UUID,
    body: PaymentUpdate,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> PaymentRead:
    payment = await service.update_payment(
        payment_id,
        body.model_dump(exclude_unset=True),
    )
    return PaymentRead.model_validate(payment)


@router.patch(
    "/payments/{payment_id}/status",
    response_model=PaymentRead,
    summary="Update payment status",
    description=(
        "**Payment status transitions**\n\n"
        "| Status | Description |\n"
        "|--------|-------------|\n"
        "| `pending` | Payment not yet received |\n"
        "| `paid` | Payment received (terminal) |\n"
        "| `overdue` | Payment past due date |\n"
        "| `cancelled` | Payment cancelled (terminal) |\n\n"
        "**Auto-set fields**:\n"
        "- ``paid`` status → sets ``paid_date`` to today if not set\n\n"
        "Terminal statuses (paid, cancelled) cannot be changed. "
        "Activity log entries created automatically."
    ),
    responses={
        200: {"description": "Status updated."},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse, "description": "Terminal state or business rule violation."},
    },
)
async def update_payment_status(
    payment_id: uuid.UUID,
    body: PaymentStatusUpdate,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> PaymentRead:
    payment = await service.update_status(payment_id, body.status)
    return PaymentRead.model_validate(payment)
