"""Measurement API endpoints."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.query import Pagination, Sorting
from app.repositories.measurement import MeasurementFilters, MeasurementRepository
from app.repositories.measurement_item import MeasurementItemRepository
from app.schemas.errors import ErrorResponse
from app.schemas.measurement import (
    MeasurementCreate,
    MeasurementItemCreate,
    MeasurementItemRead,
    MeasurementItemUpdate,
    MeasurementListResponse,
    MeasurementRead,
    MeasurementUpdate,
)
from app.services.measurement import MeasurementService

router = APIRouter(tags=["measurements"])


# ------------------------------------------------------------------
# Dependency injection
# ------------------------------------------------------------------


async def get_measurement_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MeasurementService:
    """Dependency: MeasurementService."""
    return MeasurementService(
        session=db,
        repository=MeasurementRepository(db),
        item_repository=MeasurementItemRepository(db),
    )


# ------------------------------------------------------------------
# Measurement endpoints
# ------------------------------------------------------------------


@router.get(
    "/jobs/{job_id}/measurements",
    response_model=MeasurementListResponse,
    summary="List job measurements",
    description=(
        "List all measurements for a job. "
        "A job can have multiple measurements if re-measurement is needed. "
        "Each measurement has a unique measurement_number starting from 1."
    ),
    responses={
        200: {"description": "Measurements retrieved."},
        404: {"model": ErrorResponse, "description": "Job not found."},
    },
)
async def list_job_measurements(
    job_id: UUID,
    service: Annotated[MeasurementService, Depends(get_measurement_service)],
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Number of rows to skip"),
    sort_by: str = Query("measurement_number", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
) -> MeasurementListResponse:
    pagination = Pagination(limit=limit, offset=offset)
    sorting = Sorting(sort_by=sort_by, sort_order=sort_order)

    measurements, total = await service.list_job_measurements(
        job_id,
        pagination=pagination,
        sorting=sorting,
    )

    return MeasurementListResponse(
        items=[MeasurementRead.model_validate(m) for m in measurements],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/jobs/{job_id}/measurements",
    response_model=MeasurementRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create measurement",
    description=(
        "Create a new measurement for a job. "
        "**Business rules**:\n\n"
        "- Job must exist\n"
        "- measurement_number auto-increments from 1\n"
        "- Unlimited measurement visits allowed\n\n"
        "Activity log entry created automatically."
    ),
    responses={
        201: {"description": "Measurement created."},
        404: {"model": ErrorResponse, "description": "Job not found."},
    },
)
async def create_measurement(
    job_id: UUID,
    body: MeasurementCreate,
    service: Annotated[MeasurementService, Depends(get_measurement_service)],
) -> MeasurementRead:
    measurement = await service.create_measurement(
        job_id,
        body.model_dump(exclude_none=True),
    )
    return MeasurementRead.model_validate(measurement)


@router.get(
    "/measurements/{measurement_id}",
    response_model=MeasurementRead,
    summary="Get measurement",
    description="Get a single measurement by ID.",
    responses={
        200: {"description": "Measurement retrieved."},
        404: {"model": ErrorResponse, "description": "Measurement not found."},
    },
)
async def get_measurement(
    measurement_id: UUID,
    service: Annotated[MeasurementService, Depends(get_measurement_service)],
) -> MeasurementRead:
    measurement = await service.get_measurement(measurement_id)
    return MeasurementRead.model_validate(measurement)


@router.put(
    "/measurements/{measurement_id}",
    response_model=MeasurementRead,
    summary="Update measurement",
    description=(
        "Update measurement details (visit_date, measured_by, notes). "
        "Activity log entry created automatically."
    ),
    responses={
        200: {"description": "Measurement updated."},
        404: {"model": ErrorResponse, "description": "Measurement not found."},
    },
)
async def update_measurement(
    measurement_id: UUID,
    body: MeasurementUpdate,
    service: Annotated[MeasurementService, Depends(get_measurement_service)],
) -> MeasurementRead:
    measurement = await service.update_measurement(
        measurement_id,
        body.model_dump(exclude_none=True),
    )
    return MeasurementRead.model_validate(measurement)


# ------------------------------------------------------------------
# Measurement Item endpoints
# ------------------------------------------------------------------


@router.get(
    "/measurements/{measurement_id}/items",
    response_model=list[MeasurementItemRead],
    summary="List measurement items",
    description="List all items for a measurement.",
    responses={
        200: {"description": "Items retrieved."},
        404: {"model": ErrorResponse, "description": "Measurement not found."},
    },
)
async def list_measurement_items(
    measurement_id: UUID,
    service: Annotated[MeasurementService, Depends(get_measurement_service)],
) -> list[MeasurementItemRead]:
    items = await service.list_items(measurement_id)
    return [MeasurementItemRead.model_validate(item) for item in items]


@router.post(
    "/measurements/{measurement_id}/items",
    response_model=MeasurementItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add measurement item",
    description=(
        "Add an item to a measurement. "
        "**Business rules**:\n\n"
        "- Measurement must exist\n"
        "- QuotationItem must exist\n"
        "- QuotationItem must belong to same quotation as Job\n"
        "- width >= 0 (if provided)\n"
        "- height >= 0 (if provided)\n"
        "- quantity > 0\n\n"
        "Activity log entry created automatically."
    ),
    responses={
        201: {"description": "Item added."},
        404: {"model": ErrorResponse, "description": "Measurement or QuotationItem not found."},
        422: {"model": ErrorResponse, "description": "Validation error or business rule violation."},
    },
)
async def add_measurement_item(
    measurement_id: UUID,
    body: MeasurementItemCreate,
    service: Annotated[MeasurementService, Depends(get_measurement_service)],
) -> MeasurementItemRead:
    item = await service.add_item(
        measurement_id,
        body.model_dump(exclude_none=True),
    )
    return MeasurementItemRead.model_validate(item)


@router.put(
    "/measurement-items/{item_id}",
    response_model=MeasurementItemRead,
    summary="Update measurement item",
    description=(
        "Update a measurement item. "
        "**Business rules**:\n\n"
        "- Item must exist\n"
        "- If changing quotation_item_id, must belong to same quotation\n"
        "- width >= 0 (if provided)\n"
        "- height >= 0 (if provided)\n"
        "- quantity > 0 (if provided)\n\n"
        "Activity log entry created automatically."
    ),
    responses={
        200: {"description": "Item updated."},
        404: {"model": ErrorResponse, "description": "Item not found."},
        422: {"model": ErrorResponse, "description": "Validation error or business rule violation."},
    },
)
async def update_measurement_item(
    item_id: UUID,
    body: MeasurementItemUpdate,
    service: Annotated[MeasurementService, Depends(get_measurement_service)],
) -> MeasurementItemRead:
    item = await service.update_item(
        item_id,
        body.model_dump(exclude_none=True),
    )
    return MeasurementItemRead.model_validate(item)

