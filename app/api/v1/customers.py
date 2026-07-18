"""Customer API routes — reference HTTP module for the ERP."""
from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_service
from app.core.constants import DEFAULT_PAGE_LIMIT, DEFAULT_SORT_BY, MAX_PAGE_LIMIT
from app.core.query import FilterParams, Pagination, Sorting
from app.repositories.customer import CUSTOMER_SORT_FIELDS, CustomerRepository
from app.schemas.customer import (
    CustomerCreate,
    CustomerListResponse,
    CustomerRead,
    CustomerUpdate,
)
from app.schemas.errors import ErrorResponse
from app.services.customer import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])

get_customer_service = get_service(CustomerService, CustomerRepository)


@router.get(
    "",
    response_model=CustomerListResponse,
    summary="List customers",
    description=(
        "Return a paginated list of customers. "
        "Optional filters use case-insensitive partial matching (ILIKE) on "
        "name, phone, and city. "
        "Sortable columns: "
        + ", ".join(sorted(CUSTOMER_SORT_FIELDS))
        + "."
    ),
    responses={
        200: {"description": "Paginated customer list."},
        400: {"model": ErrorResponse, "description": "Invalid query parameters."},
    },
)
async def list_customers(
    service: Annotated[CustomerService, Depends(get_customer_service)],
    name: Annotated[
        str | None,
        Query(description="Filter by full name (partial, case-insensitive)."),
    ] = None,
    phone: Annotated[
        str | None,
        Query(description="Filter by phone number (partial, case-insensitive)."),
    ] = None,
    city: Annotated[
        str | None,
        Query(description="Filter by city (partial, case-insensitive)."),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=MAX_PAGE_LIMIT, description="Page size."),
    ] = DEFAULT_PAGE_LIMIT,
    offset: Annotated[
        int,
        Query(ge=0, description="Number of rows to skip."),
    ] = 0,
    sort_by: Annotated[
        str,
        Query(description="Column to sort by."),
    ] = DEFAULT_SORT_BY,
    sort_order: Annotated[
        Literal["asc", "desc"],
        Query(description="Sort direction."),
    ] = "desc",
) -> CustomerListResponse:
    pagination = Pagination(limit=limit, offset=offset)
    sorting = Sorting(sort_by=sort_by, sort_order=sort_order)
    filters = FilterParams(name=name, phone=phone, city=city)

    items, total = await service.list_customers(
        pagination=pagination,
        sorting=sorting,
        filters=filters,
    )
    return CustomerListResponse(
        items=[CustomerRead.model_validate(item) for item in items],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerRead,
    summary="Get customer by ID",
    description="Return a single customer resource by its UUID primary key.",
    responses={
        200: {"description": "Customer found."},
        404: {"model": ErrorResponse, "description": "Customer does not exist."},
    },
)
async def get_customer(
    customer_id: uuid.UUID,
    service: Annotated[CustomerService, Depends(get_customer_service)],
) -> CustomerRead:
    customer = await service.get_customer(customer_id)
    return CustomerRead.model_validate(customer)


@router.post(
    "",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create customer",
    description=(
        "Create a new customer. Phone numbers are normalized (Egyptian formats "
        "supported) and must be unique across all customers. "
        "Customers are never deleted via the API."
    ),
    responses={
        201: {"description": "Customer created."},
        400: {"model": ErrorResponse, "description": "Validation failed."},
        409: {"model": ErrorResponse, "description": "Phone number already exists."},
    },
)
async def create_customer(
    body: CustomerCreate,
    service: Annotated[CustomerService, Depends(get_customer_service)],
) -> CustomerRead:
    customer = await service.create_customer(body.model_dump())
    return CustomerRead.model_validate(customer)


@router.put(
    "/{customer_id}",
    response_model=CustomerRead,
    summary="Update customer",
    description=(
        "Update an existing customer. Omitted fields are left unchanged. "
        "Changing ``phone_number`` enforces the same uniqueness rule as create."
    ),
    responses={
        200: {"description": "Customer updated."},
        400: {"model": ErrorResponse, "description": "Validation failed."},
        404: {"model": ErrorResponse, "description": "Customer does not exist."},
        409: {"model": ErrorResponse, "description": "Phone number already exists."},
    },
)
async def update_customer(
    customer_id: uuid.UUID,
    body: CustomerUpdate,
    service: Annotated[CustomerService, Depends(get_customer_service)],
) -> CustomerRead:
    customer = await service.update_customer(
        customer_id,
        body.model_dump(exclude_unset=True),
    )
    return CustomerRead.model_validate(customer)
