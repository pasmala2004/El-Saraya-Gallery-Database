"""Customer application service — reference business-logic implementation."""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError, ValidationError
from app.core.query import FilterParams, Pagination, Sorting
from app.models.customer import Customer
from app.repositories.customer import CustomerRepository
from app.services.base import BaseService
from app.utils.phone import normalize_phone_number


def _trim_optional(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed if trimmed else None


class CustomerService(BaseService[Customer]):
    """
    Customer use-cases.

    Customers are never physically deleted — there is no delete API.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: CustomerRepository,
    ) -> None:
        super().__init__(session, repository, entity_name="Customer")
        self._customers = repository

    async def get_customer(self, customer_id: uuid.UUID) -> Customer:
        """Return a customer by id or raise ``EntityNotFoundError``."""
        return await self.get_by_id(customer_id)

    async def list_customers(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: FilterParams | None = None,
    ) -> tuple[list[Customer], int]:
        """Return ``(customers, total)`` matching the query options."""
        return await self._customers.search(
            pagination=pagination,
            sorting=sorting,
            filters=filters,
        )

    async def create_customer(self, data: dict[str, Any]) -> Customer:
        """
        Create a customer after normalizing phones and enforcing uniqueness.
        """
        payload = self._normalize_payload(data, require_phone=True)
        await self._ensure_phone_unique(payload["phone_number"])

        customer = Customer(**payload)
        return await self.create(customer, commit=True)

    async def update_customer(
        self,
        customer_id: uuid.UUID,
        data: dict[str, Any],
    ) -> Customer:
        """
        Update an existing customer.

        Only keys present in ``data`` are applied (partial update).
        Phone uniqueness is enforced when ``phone_number`` changes.
        """
        customer = await self.get_customer(customer_id)
        payload = self._normalize_payload(data, require_phone=False)

        if "phone_number" in payload:
            await self._ensure_phone_unique(
                payload["phone_number"],
                exclude_id=customer.id,
            )

        for field, value in payload.items():
            setattr(customer, field, value)

        return await self.update(customer, commit=True)

    def _normalize_payload(
        self,
        data: dict[str, Any],
        *,
        require_phone: bool,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}

        if "full_name" in data:
            name = (data["full_name"] or "").strip()
            if not name:
                raise ValidationError("full_name must not be empty", field="full_name")
            payload["full_name"] = name

        if "phone_number" in data or require_phone:
            if data.get("phone_number") is None and require_phone:
                raise ValidationError("phone_number is required", field="phone_number")
            if "phone_number" in data and data["phone_number"] is not None:
                payload["phone_number"] = normalize_phone_number(str(data["phone_number"]))

        if "alternative_phone" in data:
            alt = data["alternative_phone"]
            payload["alternative_phone"] = (
                normalize_phone_number(str(alt)) if alt not in (None, "") else None
            )

        for field in ("address", "city", "location_url", "notes"):
            if field in data:
                payload[field] = _trim_optional(data[field])

        return payload

    async def _ensure_phone_unique(
        self,
        phone_number: str,
        *,
        exclude_id: uuid.UUID | None = None,
    ) -> None:
        existing = await self._customers.get_by_phone(phone_number)
        if existing is None:
            return
        if exclude_id is not None and existing.id == exclude_id:
            return
        raise DuplicateEntityError("Customer", "phone_number", phone_number)
