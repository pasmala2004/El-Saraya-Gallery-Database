"""MeasurementItem repository."""
from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.query import Pagination, apply_pagination
from app.models.measurement_item import MeasurementItem
from app.repositories.base import GenericRepository


class MeasurementItemRepository(GenericRepository[MeasurementItem]):
    """Repository for measurement item operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MeasurementItem)

    async def list_by_measurement(
        self,
        measurement_id: uuid.UUID,
        *,
        pagination: Pagination | None = None,
    ) -> list[MeasurementItem]:
        """List all items for a measurement."""
        stmt = (
            select(MeasurementItem)
            .where(MeasurementItem.measurement_id == measurement_id)
            .order_by(MeasurementItem.created_at)
        )

        if pagination:
            stmt = apply_pagination(stmt, pagination)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_measurement(self, measurement_id: uuid.UUID) -> int:
        """Count items in a measurement."""
        stmt = (
            select(func.count())
            .select_from(MeasurementItem)
            .where(MeasurementItem.measurement_id == measurement_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

