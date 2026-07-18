"""
Quotation application service — central pre-production workflow.

Frozen schema statuses (``QuotationStatus``)
--------------------------------------------
``draft``, ``sent``, ``approved``, ``rejected``, ``cancelled``

The richer conceptual workflow (waiting for measurement / measured /
under negotiation / expired) is **not** in the frozen enum or database.
Until a future migration expands ``quotation_status``, negotiation is
modeled as ``draft`` ↔ ``sent`` before a terminal outcome.
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BusinessRuleViolation,
    DuplicateEntityError,
    EntityNotFoundError,
    ValidationError,
)
from app.core.query import Pagination, Sorting
from app.enums.quotation import QuotationStatus
from app.models.quotation import Quotation
from app.models.quotation_item import QuotationItem
from app.repositories.customer import CustomerRepository
from app.repositories.product import ProductRepository
from app.repositories.quotation import QuotationFilters, QuotationRepository
from app.repositories.quotation_item import QuotationItemRepository
from app.services.base import BaseService

# Terminal outcomes — no further status changes.
_TERMINAL_STATUSES: frozenset[QuotationStatus] = frozenset(
    {
        QuotationStatus.APPROVED,
        QuotationStatus.REJECTED,
        QuotationStatus.CANCELLED,
    }
)

# Allowed transitions on the frozen enum.
# draft ↔ sent models negotiation before approval.
_ALLOWED_TRANSITIONS: dict[QuotationStatus, frozenset[QuotationStatus]] = {
    QuotationStatus.DRAFT: frozenset(
        {QuotationStatus.SENT, QuotationStatus.CANCELLED}
    ),
    QuotationStatus.SENT: frozenset(
        {
            QuotationStatus.DRAFT,  # renegotiation / return to editing
            QuotationStatus.APPROVED,
            QuotationStatus.REJECTED,
            QuotationStatus.CANCELLED,
        }
    ),
    QuotationStatus.APPROVED: frozenset(),
    QuotationStatus.REJECTED: frozenset(),
    QuotationStatus.CANCELLED: frozenset(),
}


class QuotationService(BaseService[Quotation]):
    """Quotation workflow, line items, and total calculation."""

    def __init__(
        self,
        session: AsyncSession,
        repository: QuotationRepository,
        item_repository: QuotationItemRepository | None = None,
        customer_repository: CustomerRepository | None = None,
        product_repository: ProductRepository | None = None,
    ) -> None:
        super().__init__(session, repository, entity_name="Quotation")
        self._quotations = repository
        self._items = item_repository or QuotationItemRepository(session)
        self._customers = customer_repository or CustomerRepository(session)
        self._products = product_repository or ProductRepository(session)

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    async def get_quotation(self, quotation_id: uuid.UUID) -> Quotation:
        return await self.get_by_id(quotation_id)

    async def list_quotations(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: QuotationFilters | None = None,
    ) -> tuple[list[Quotation], int]:
        return await self._quotations.search(
            pagination=pagination,
            sorting=sorting,
            filters=filters,
        )

    async def list_customer_quotations(
        self,
        customer_id: uuid.UUID,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
    ) -> tuple[list[Quotation], int]:
        customer = await self._customers.get_by_id(customer_id)
        if customer is None:
            raise EntityNotFoundError("Customer", customer_id)
        return await self._quotations.list_by_customer(
            customer_id,
            pagination=pagination,
            sorting=sorting,
        )

    async def list_items(self, quotation_id: uuid.UUID) -> list[QuotationItem]:
        await self.get_quotation(quotation_id)
        return await self._items.list_by_quotation(quotation_id)

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    async def create_quotation(self, data: dict[str, Any]) -> Quotation:
        customer_id = uuid.UUID(str(data["customer_id"]))
        customer = await self._customers.get_by_id(customer_id)
        if customer is None:
            raise EntityNotFoundError("Customer", customer_id)

        quotation_number = await self._allocate_quotation_number(
            data.get("quotation_number")
        )
        quotation_date = data.get("quotation_date") or date.today()
        if isinstance(quotation_date, str):
            quotation_date = date.fromisoformat(quotation_date)

        discount = self._as_money(data.get("discount", Decimal("0.00")), field="discount")
        notes = self._trim_optional(data.get("notes"))

        quotation = Quotation(
            quotation_number=quotation_number,
            customer_id=customer_id,
            quotation_date=quotation_date,
            status=QuotationStatus.DRAFT,
            total_price=Decimal("0.00"),
            discount=discount,
            final_price=Decimal("0.00"),
            notes=notes,
        )
        self._apply_totals(quotation, item_total=Decimal("0.00"))
        return await self.create(quotation, commit=True)

    async def update_quotation(
        self,
        quotation_id: uuid.UUID,
        data: dict[str, Any],
    ) -> Quotation:
        quotation = await self.get_quotation(quotation_id)
        self._ensure_editable(quotation)

        if "quotation_date" in data and data["quotation_date"] is not None:
            value = data["quotation_date"]
            quotation.quotation_date = (
                date.fromisoformat(value) if isinstance(value, str) else value
            )

        if "discount" in data and data["discount"] is not None:
            quotation.discount = self._as_money(data["discount"], field="discount")

        if "notes" in data:
            quotation.notes = self._trim_optional(data["notes"])

        await self._recalculate_totals(quotation, commit=False)
        return await self.update(quotation, commit=True)

    async def update_status(
        self,
        quotation_id: uuid.UUID,
        new_status: QuotationStatus,
    ) -> Quotation:
        quotation = await self.get_quotation(quotation_id)
        await self._validate_transition(quotation, new_status)
        quotation.status = new_status
        return await self.update(quotation, commit=True)

    async def add_item(
        self,
        quotation_id: uuid.UUID,
        data: dict[str, Any],
    ) -> QuotationItem:
        quotation = await self.get_quotation(quotation_id)
        self._ensure_editable(quotation)

        product_id = uuid.UUID(str(data["product_id"]))
        product = await self._products.get_by_id(product_id)
        if product is None:
            raise EntityNotFoundError("Product", product_id)

        quantity = int(data.get("quantity", 1))
        if quantity < 1:
            raise ValidationError("quantity must be >= 1", field="quantity")

        unit_price = self._as_money(data["unit_price"], field="unit_price")
        line_total = (unit_price * Decimal(quantity)).quantize(Decimal("0.01"))

        item = QuotationItem(
            quotation_id=quotation.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=line_total,
            description=self._trim_optional(data.get("description")),
            notes=self._trim_optional(data.get("notes")),
        )
        await self._items.create(item)
        await self._recalculate_totals(quotation, commit=False)
        await self.commit()
        await self._session.refresh(item)
        await self.refresh(quotation)
        return item

    async def update_item(
        self,
        item_id: uuid.UUID,
        data: dict[str, Any],
    ) -> QuotationItem:
        item = await self._items.get_by_id(item_id)
        if item is None:
            raise EntityNotFoundError("QuotationItem", item_id)

        quotation = await self.get_quotation(item.quotation_id)
        self._ensure_editable(quotation)

        if "product_id" in data and data["product_id"] is not None:
            product_id = uuid.UUID(str(data["product_id"]))
            product = await self._products.get_by_id(product_id)
            if product is None:
                raise EntityNotFoundError("Product", product_id)
            item.product_id = product_id

        if "quantity" in data and data["quantity"] is not None:
            quantity = int(data["quantity"])
            if quantity < 1:
                raise ValidationError("quantity must be >= 1", field="quantity")
            item.quantity = quantity

        if "unit_price" in data and data["unit_price"] is not None:
            item.unit_price = self._as_money(data["unit_price"], field="unit_price")

        if "description" in data:
            item.description = self._trim_optional(data["description"])

        if "notes" in data:
            item.notes = self._trim_optional(data["notes"])

        item.total_price = (
            item.unit_price * Decimal(item.quantity)
        ).quantize(Decimal("0.01"))

        await self._items.update(item)
        await self._recalculate_totals(quotation, commit=False)
        await self.commit()
        await self._session.refresh(item)
        return item

    # ------------------------------------------------------------------
    # Totals & transitions
    # ------------------------------------------------------------------

    async def _recalculate_totals(
        self,
        quotation: Quotation,
        *,
        commit: bool,
    ) -> None:
        items = await self._items.list_by_quotation(quotation.id)
        item_total = sum(
            (item.total_price for item in items),
            start=Decimal("0.00"),
        )
        self._apply_totals(quotation, item_total=item_total)
        await self._quotations.update(quotation)
        if commit:
            await self.commit()
            await self.refresh(quotation)

    def _apply_totals(self, quotation: Quotation, *, item_total: Decimal) -> None:
        total = item_total.quantize(Decimal("0.01"))
        discount = quotation.discount.quantize(Decimal("0.01"))
        if discount < 0:
            raise ValidationError("discount cannot be negative", field="discount")
        final_price = (total - discount).quantize(Decimal("0.01"))
        if final_price < 0:
            raise ValidationError(
                "discount cannot make final_price negative",
                field="discount",
            )
        quotation.total_price = total
        quotation.final_price = final_price

    async def _validate_transition(
        self,
        quotation: Quotation,
        new_status: QuotationStatus,
    ) -> None:
        current = quotation.status
        if current == new_status:
            return

        allowed = _ALLOWED_TRANSITIONS.get(current, frozenset())
        if new_status not in allowed:
            raise BusinessRuleViolation(
                f"Invalid status transition: {current.value} → {new_status.value}",
                code="invalid_quotation_status_transition",
            )

        # Leaving draft or approving requires at least one line item.
        needs_items = new_status in {
            QuotationStatus.SENT,
            QuotationStatus.APPROVED,
        }
        if needs_items:
            count = await self._items.count_by_quotation(quotation.id)
            if count < 1:
                raise BusinessRuleViolation(
                    f"Quotation must have at least one item before status "
                    f"{new_status.value}",
                    code="quotation_requires_items",
                )

    def _ensure_editable(self, quotation: Quotation) -> None:
        if quotation.status in _TERMINAL_STATUSES:
            raise BusinessRuleViolation(
                f"Quotation in terminal status {quotation.status.value} "
                "cannot be modified",
                code="quotation_terminal",
            )

    async def _allocate_quotation_number(self, requested: Any | None) -> str:
        if requested is not None:
            number = str(requested).strip()
            if not number:
                raise ValidationError(
                    "quotation_number must not be empty",
                    field="quotation_number",
                )
            existing = await self._quotations.get_by_number(number)
            if existing is not None:
                raise DuplicateEntityError("Quotation", "quotation_number", number)
            return number

        # Auto: Q-YYYY-XXXXXXXX (unique via UUID fragment)
        year = date.today().year
        for _ in range(5):
            candidate = f"Q-{year}-{uuid.uuid4().hex[:8].upper()}"
            if await self._quotations.get_by_number(candidate) is None:
                return candidate
        raise ValidationError("Unable to allocate quotation_number")

    @staticmethod
    def _as_money(value: Any, *, field: str) -> Decimal:
        try:
            amount = Decimal(str(value))
        except Exception as exc:  # noqa: BLE001 — convert to domain error
            raise ValidationError(f"Invalid money value for {field}", field=field) from exc
        if amount < 0:
            raise ValidationError(f"{field} cannot be negative", field=field)
        return amount.quantize(Decimal("0.01"))

    @staticmethod
    def _trim_optional(value: Any) -> str | None:
        if value is None:
            return None
        trimmed = str(value).strip()
        return trimmed if trimmed else None
