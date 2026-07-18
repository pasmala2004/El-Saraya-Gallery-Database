"""Product category API routes."""
from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_service
from app.core.constants import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT
from app.core.query import FilterParams, Pagination, Sorting
from app.repositories.product_category import (
    CATEGORY_SORT_FIELDS,
    ProductCategoryRepository,
)
from app.schemas.errors import ErrorResponse
from app.schemas.product_category import (
    ProductCategoryCreate,
    ProductCategoryListResponse,
    ProductCategoryRead,
)
from app.services.product_category import ProductCategoryService

router = APIRouter(prefix="/product-categories", tags=["product-categories"])

get_category_service = get_service(ProductCategoryService, ProductCategoryRepository)


@router.get(
    "",
    response_model=ProductCategoryListResponse,
    summary="List product categories",
    description=(
        "Return a paginated list of product categories. "
        "Optional ``name`` filter uses case-insensitive partial matching. "
        "Sortable columns: "
        + ", ".join(sorted(CATEGORY_SORT_FIELDS))
        + "."
    ),
    responses={
        200: {"description": "Paginated category list."},
        400: {"model": ErrorResponse, "description": "Invalid query parameters."},
    },
)
async def list_product_categories(
    service: Annotated[ProductCategoryService, Depends(get_category_service)],
    name: Annotated[
        str | None,
        Query(description="Filter by category name (partial, case-insensitive)."),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_LIMIT)] = DEFAULT_PAGE_LIMIT,
    offset: Annotated[int, Query(ge=0)] = 0,
    sort_by: Annotated[str, Query()] = "name",
    sort_order: Annotated[Literal["asc", "desc"], Query()] = "asc",
) -> ProductCategoryListResponse:
    pagination = Pagination(limit=limit, offset=offset)
    sorting = Sorting(sort_by=sort_by, sort_order=sort_order)
    filters = FilterParams(name=name)

    items, total = await service.list_categories(
        pagination=pagination,
        sorting=sorting,
        filters=filters,
    )
    return ProductCategoryListResponse(
        items=[ProductCategoryRead.model_validate(item) for item in items],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.post(
    "",
    response_model=ProductCategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create product category",
    description="Create a catalog category. Category names must be unique.",
    responses={
        201: {"description": "Category created."},
        400: {"model": ErrorResponse, "description": "Validation failed."},
        409: {"model": ErrorResponse, "description": "Category name already exists."},
    },
)
async def create_product_category(
    body: ProductCategoryCreate,
    service: Annotated[ProductCategoryService, Depends(get_category_service)],
) -> ProductCategoryRead:
    category = await service.create_category(body.model_dump())
    return ProductCategoryRead.model_validate(category)
