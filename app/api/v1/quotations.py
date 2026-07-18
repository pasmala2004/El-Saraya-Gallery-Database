"""Quotation API routes — pre-production commercial workflow."""
from __future__ import annotations

import uuid
from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT
from app.core.query import Pagination, Sorting
from app.db.session import get_db
from app.enums.quotation import QuotationStatus
from app.repositories.customer import CustomerRepository
from app.repositories.product import ProductRepository
from app.repositories.quotation import QUOTATION_SORT_FIELDS, QuotationFilters, QuotationRepository
from app.repositories.quotation_item import QuotationItemRepository
from app.schemas.errors import ErrorResponse
from app.schemas.quotation import (
    QuotationCreate,
    QuotationDetailRead,
    QuotationItemCreate,
    QuotationItemListResponse,
    QuotationItemRead,
    QuotationItemUpdate,
    QuotationListResponse,
    QuotationRead,
    QuotationStatusUpdate,
    QuotationUpdate,
)
from app.services.quotation import QuotationService

router = APIRouter(tags=["quotations"])


def get_quotation_service(
    session: AsyncSession = Depends(get_db),
) -> QuotationService:
    return QuotationService(
        session,
        QuotationRepository(session),
        QuotationItemRepository(session),
        CustomerRepository(session),
        ProductRepository(session),
    )


# ---------------------------------------------------------------------------
# Quotations
# ---------------------------------------------------------------------------

@router.get(
    "/quotations",
    response_model=QuotationListResponse,
    summary="List quotations",
    description=(
        "Paginated quotation search. Filters: ``status``, ``customer``, "
        "``quotation_number`` (partial), ``date_from``, ``date_to``. "
        "Sort aliases: ``date`` → ``quotation_date``. "
        "Allowed sort columns: "
        + ", ".join(sorted(QUOTATION_SORT_FIELDS))
        + "."
    ),
    responses={400: {"model": ErrorResponse}},
)
async def list_quotations(
    service: Annotated[QuotationService, Depends(get_quotation_service)],
    status_filter: Annotated[
        QuotationStatus | None,
        Query(alias="status", description="Exact quotation status."),
    ] = None,
    customer: Annotated[
        uuid.UUID | None,
        Query(description="Filter by customer UUID."),
    ] = None,
    quotation_number: Annotated[
        str | None,
        Query(description="Partial quotation number match."),
    ] = None,
    date_from: Annotated[date | None, Query(description="Inclusive start date.")] = None,
    date_to: Annotated[date | None, Query(description="Inclusive end date.")] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_LIMIT)] = DEFAULT_PAGE_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    sort_by: Annotated[str, Query()] = "date",
    sort_order: Annotated[Literal["asc", "desc"], Query()] = "desc",
) -> QuotationListResponse:
    pagination = Pagination(limit=limit, offset=offset)
    sorting = Sorting(sort_by=sort_by, sort_order=sort_order)
    filters = QuotationFilters(
        status=status_filter,
        customer_id=customer,
        quotation_number=quotation_number,
        date_from=date_from,
        date_to=date_to,
    )
    items, total = await service.list_quotations(
        pagination=pagination,
        sorting=sorting,
        filters=filters,
    )
    return QuotationListResponse(
        items=[QuotationRead.model_validate(i) for i in items],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get(
    "/quotations/{quotation_id}",
    response_model=QuotationDetailRead,
    summary="Get quotation by ID",
    description="Return a quotation and its line items.",
    responses={404: {"model": ErrorResponse}},
)
async def get_quotation(
    quotation_id: uuid.UUID,
    service: Annotated[QuotationService, Depends(get_quotation_service)],
) -> QuotationDetailRead:
    quotation = await service.get_quotation(quotation_id)
    items = await service.list_items(quotation_id)
    payload = QuotationRead.model_validate(quotation).model_dump()
    payload["items"] = [QuotationItemRead.model_validate(i) for i in items]
    return QuotationDetailRead(**payload)


@router.post(
    "/quotations",
    response_model=QuotationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create quotation",
    description=(
        "Create a **draft** quotation for an existing customer. "
        "Add line items via ``POST /quotations/{id}/items`` before sending."
    ),
    responses={
        201: {"description": "Draft quotation created."},
        404: {"model": ErrorResponse, "description": "Customer not found."},
        409: {"model": ErrorResponse, "description": "Duplicate quotation_number."},
    },
)
async def create_quotation(
    body: QuotationCreate,
    service: Annotated[QuotationService, Depends(get_quotation_service)],
) -> QuotationRead:
    quotation = await service.create_quotation(body.model_dump(exclude_none=True))
    return QuotationRead.model_validate(quotation)


@router.put(
    "/quotations/{quotation_id}",
    response_model=QuotationRead,
    summary="Update quotation",
    description=(
        "Update discount, notes, or date. Status changes use "
        "``PATCH /quotations/{id}/status``. Terminal quotations cannot be edited."
    ),
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse, "description": "Terminal / business rule."},
    },
)
async def update_quotation(
    quotation_id: uuid.UUID,
    body: QuotationUpdate,
    service: Annotated[QuotationService, Depends(get_quotation_service)],
) -> QuotationRead:
    quotation = await service.update_quotation(
        quotation_id,
        body.model_dump(exclude_unset=True),
    )
    return QuotationRead.model_validate(quotation)


@router.patch(
    "/quotations/{quotation_id}/status",
    response_model=QuotationRead,
    summary="Update quotation status",
    description=(
        "**Supported transitions (frozen enum)**\n\n"
        "- `draft` → `sent` | `cancelled` (sent requires ≥1 item)\n"
        "- `sent` → `draft` | `approved` | `rejected` | `cancelled` "
        "(approved requires ≥1 item; `sent`→`draft` = renegotiation)\n"
        "- `approved` / `rejected` / `cancelled` → *(terminal)*\n\n"
        "Statuses waiting_for_measurement / measured / under_negotiation / expired "
        "are **not** in the frozen database enum; negotiation is `draft`↔`sent`."
    ),
    responses={
        200: {"description": "Status updated."},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse, "description": "Invalid transition or missing items."},
    },
)
async def update_quotation_status(
    quotation_id: uuid.UUID,
    body: QuotationStatusUpdate,
    service: Annotated[QuotationService, Depends(get_quotation_service)],
) -> QuotationRead:
    quotation = await service.update_status(quotation_id, body.status)
    return QuotationRead.model_validate(quotation)


@router.get(
    "/customers/{customer_id}/quotations",
    response_model=QuotationListResponse,
    summary="List quotations for a customer",
    description="Paginated quotations belonging to one customer.",
    responses={404: {"model": ErrorResponse, "description": "Customer not found."}},
)
async def list_customer_quotations(
    customer_id: uuid.UUID,
    service: Annotated[QuotationService, Depends(get_quotation_service)],
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_LIMIT)] = DEFAULT_PAGE_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    sort_by: Annotated[str, Query()] = "date",
    sort_order: Annotated[Literal["asc", "desc"], Query()] = "desc",
) -> QuotationListResponse:
    pagination = Pagination(limit=limit, offset=offset)
    sorting = Sorting(sort_by=sort_by, sort_order=sort_order)
    items, total = await service.list_customer_quotations(
        customer_id,
        pagination=pagination,
        sorting=sorting,
    )
    return QuotationListResponse(
        items=[QuotationRead.model_validate(i) for i in items],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


# ---------------------------------------------------------------------------
# Quotation items
# ---------------------------------------------------------------------------

@router.get(
    "/quotations/{quotation_id}/items",
    response_model=QuotationItemListResponse,
    summary="List quotation items",
    responses={404: {"model": ErrorResponse}},
)
async def list_quotation_items(
    quotation_id: uuid.UUID,
    service: Annotated[QuotationService, Depends(get_quotation_service)],
) -> QuotationItemListResponse:
    items = await service.list_items(quotation_id)
    return QuotationItemListResponse(
        items=[QuotationItemRead.model_validate(i) for i in items],
        total=len(items),
    )


@router.post(
    "/quotations/{quotation_id}/items",
    response_model=QuotationItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add quotation item",
    description=(
        "Append a customized product line. Recalculates "
        "``total_price`` and ``final_price`` on the parent quotation."
    ),
    responses={
        201: {"description": "Item created; quotation totals refreshed."},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
async def add_quotation_item(
    quotation_id: uuid.UUID,
    body: QuotationItemCreate,
    service: Annotated[QuotationService, Depends(get_quotation_service)],
) -> QuotationItemRead:
    item = await service.add_item(quotation_id, body.model_dump())
    return QuotationItemRead.model_validate(item)


@router.put(
    "/quotation-items/{item_id}",
    response_model=QuotationItemRead,
    summary="Update quotation item",
    description="Update a line item and recalculate parent quotation totals.",
    responses={
        200: {"description": "Item updated."},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
async def update_quotation_item(
    item_id: uuid.UUID,
    body: QuotationItemUpdate,
    service: Annotated[QuotationService, Depends(get_quotation_service)],
) -> QuotationItemRead:
    item = await service.update_item(item_id, body.model_dump(exclude_unset=True))
    return QuotationItemRead.model_validate(item)
