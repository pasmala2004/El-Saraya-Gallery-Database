"""Measurement repository."""
from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.query import Pagination, Sorting, apply_pagination, apply_sorting
from app.models.measurement import Measurement
from app.repositories.base import GenericRepository

MEASUREMENT_SORT_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "measurement_number",
        "visit_date",
        "measured_by",
        "created_at",
        "updated_at",
    }
)


class MeasurementFilters:
    """Filters for measurement search."""

    def __init__(
        self,
        *,
        job_id: uuid.UUID | None = None,
        measurement_number: int | None = None,
        measured_by: str | None = None,
        visit_date_from: date | None = None,
        visit_date_to: date | None = None,
        created_after: date | None = None,
        created_before: date | None = None,
    ) -> None:
        self.job_id = job_id
        self.measurement_number = measurement_number
        self.measured_by = measured_by
        self.visit_date_from = visit_date_from
        self.visit_date_to = visit_date_to
        self.created_after = created_after
        self.created_before = created_before


class MeasurementRepository(GenericRepository[Measurement]):
    """Repository for measurement operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Measurement)

    async def get_by_id(
        self,
        measurement_id: uuid.UUID,
        *,
        load_items: bool = False,
    ) -> Measurement | None:
        """Get measurement by ID with optional eager loading."""
        stmt = select(Measurement).where(Measurement.id == measurement_id)
        if load_items:
            stmt = stmt.options(selectinload(Measurement.items))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_job(
        self,
        job_id: uuid.UUID,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
    ) -> tuple[list[Measurement], int]:
        """List all measurements for a job."""
        filters = MeasurementFilters(job_id=job_id)
        return await self.search(
            pagination=pagination,
            sorting=sorting,
            filters=filters,
        )

    async def get_next_measurement_number(self, job_id: uuid.UUID) -> int:
        """Get the next measurement number for a job."""
        stmt = (
            select(func.max(Measurement.measurement_number))
            .where(Measurement.job_id == job_id)
        )
        result = await self._session.execute(stmt)
        max_number = result.scalar_one_or_none()
        return 1 if max_number is None else max_number + 1

    async def search(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: MeasurementFilters | None = None,
    ) -> tuple[list[Measurement], int]:
        """Search measurements with filters, sorting, and pagination."""
        stmt = select(Measurement)
        count_stmt = select(func.count()).select_from(Measurement)

        # Apply filters
        if filters:
            conditions = self._build_filter_conditions(filters)
            if conditions:
                stmt = stmt.where(and_(*conditions))
                count_stmt = count_stmt.where(and_(*conditions))

        # Get total count
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        # Apply sorting
        if sorting:
            stmt = apply_sorting(
                stmt,
                Measurement,
                sorting,
                allowed_sort_fields=MEASUREMENT_SORT_FIELDS,
            )
        else:
            # Default sort by measurement_number descending
            stmt = stmt.order_by(Measurement.measurement_number.desc())

        # Apply pagination
        if pagination:
            stmt = apply_pagination(stmt, pagination)

        # Execute query
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    def _build_filter_conditions(self, filters: MeasurementFilters) -> list[Any]:
        """Build SQLAlchemy filter conditions."""
        conditions = []

        if filters.job_id:
            conditions.append(Measurement.job_id == filters.job_id)

        if filters.measurement_number is not None:
            conditions.append(Measurement.measurement_number == filters.measurement_number)

        if filters.measured_by:
            # Case-insensitive partial match
            conditions.append(
                Measurement.measured_by.ilike(f"%{filters.measured_by}%")
            )

        if filters.visit_date_from:
            conditions.append(Measurement.visit_date >= filters.visit_date_from)

        if filters.visit_date_to:
            conditions.append(Measurement.visit_date <= filters.visit_date_to)

        if filters.created_after:
            conditions.append(
                func.date(Measurement.created_at) >= filters.created_after
            )

        if filters.created_before:
            conditions.append(
                func.date(Measurement.created_at) <= filters.created_before
            )

        return conditions

