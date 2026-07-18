"""Quotation item repository."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quotation_item import QuotationItem
from app.repositories.base import GenericRepository


class QuotationItemRepository(GenericRepository[QuotationItem]):
    """Data access for ``QuotationItem`` entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, QuotationItem)

    async def list_by_quotation(
        self,
        quotation_id: uuid.UUID,
    ) -> list[QuotationItem]:
        """Return all line items for a quotation, oldest first."""
        result = await self._session.execute(
            select(QuotationItem)
            .where(QuotationItem.quotation_id == quotation_id)
            .order_by(QuotationItem.created_at.asc())
        )
        return list(result.scalars().all())

    async def count_by_quotation(self, quotation_id: uuid.UUID) -> int:
        """Return the number of line items on a quotation."""
        result = await self._session.execute(
            select(QuotationItem.id).where(QuotationItem.quotation_id == quotation_id)
        )
        return len(result.all())
