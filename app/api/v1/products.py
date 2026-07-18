"""Product API routes — catalog module (no pricing)."""
from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_PAGE_LIMIT, DEFAULT_SORT_BY, MAX_PAGE_LIMIT
from app.core.query import Pagination, Sorting
from app.db.session import get_db
from app.repositories.product import PRODUCT_SORT_FIELDS, ProductFilters, ProductRepository
from app.repositories.product_category import ProductCategoryRepository
from app.schemas.errors import ErrorResponse
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductRead,
    ProductUpdate,
)
from app.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])


def get_product_service(
    session: AsyncSession = Depends(get_db),
) -> ProductService:
    """Wire product + category repositories for catalog use-cases."""
    return ProductService(
        session,
        ProductRepository(session),
        ProductCategoryRepository(session),
    )


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List products",
    description=(
        "Return a paginated product catalog. "
        "Filter by ``name`` (partial), ``category`` (category UUID), and ``active``. "
        "Sortable columns: "
        + ", ".join(sorted(PRODUCT_SORT_FIELDS))
        + ". Pricing is not part of this resource."
    ),
    responses={
        200: {"description": "Paginated product list."},
        400: {"model": ErrorResponse, "description": "Invalid query parameters."},
    },
)
async def list_products(
    service: Annotated[ProductService, Depends(get_product_service)],
    name: Annotated[
        str | None,
        Query(description="Filter by product name (partial, case-insensitive)."),
    ] = None,
    category: Annotated[
        uuid.UUID | None,
        Query(description="Filter by product category UUID."),
    ] = None,
    active: Annotated[
        bool | None,
        Query(description="Filter by active flag (true = catalog-visible only)."),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_LIMIT)] = DEFAULT_PAGE_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    sort_by: Annotated[str, Query()] = DEFAULT_SORT_BY,
    sort_order: Annotated[Literal["asc", "desc"], Query()] = "desc",
) -> ProductListResponse:
    pagination = Pagination(limit=limit, offset=offset)
    sorting = Sorting(sort_by=sort_by, sort_order=sort_order)
    filters = ProductFilters(name=name, category_id=category, active=active)

    items, total = await service.list_products(
        pagination=pagination,
        sorting=sorting,
        filters=filters,
    )
    return ProductListResponse(
        items=[ProductRead.model_validate(item) for item in items],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    summary="Get product by ID",
    description="Return a single catalog product by UUID.",
    responses={
        200: {"description": "Product found."},
        404: {"model": ErrorResponse, "description": "Product does not exist."},
    },
)
async def get_product(
    product_id: uuid.UUID,
    service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductRead:
    product = await service.get_product(product_id)
    return ProductRead.model_validate(product)


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description=(
        "Create a catalog product under an existing category. "
        "Names must be unique within the category. "
        "Does not accept or store pricing."
    ),
    responses={
        201: {"description": "Product created."},
        400: {"model": ErrorResponse, "description": "Validation failed."},
        404: {"model": ErrorResponse, "description": "Category does not exist."},
        409: {"model": ErrorResponse, "description": "Duplicate product name in category."},
    },
)
async def create_product(
    body: ProductCreate,
    service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductRead:
    product = await service.create_product(body.model_dump())
    return ProductRead.model_validate(product)


@router.put(
    "/{product_id}",
    response_model=ProductRead,
    summary="Update product",
    description=(
        "Update a catalog product. Omitted fields are left unchanged. "
        "Renaming or moving categories enforces uniqueness within the target category."
    ),
    responses={
        200: {"description": "Product updated."},
        400: {"model": ErrorResponse, "description": "Validation failed."},
        404: {"model": ErrorResponse, "description": "Product or category not found."},
        409: {"model": ErrorResponse, "description": "Duplicate product name in category."},
    },
)
async def update_product(
    product_id: uuid.UUID,
    body: ProductUpdate,
    service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductRead:
    product = await service.update_product(
        product_id,
        body.model_dump(exclude_unset=True),
    )
    return ProductRead.model_validate(product)
