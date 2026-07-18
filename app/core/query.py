"""
Reusable list-query helpers: pagination, sorting, and filtering.

These types are framework-agnostic (no FastAPI). Repositories apply them
to SQLAlchemy ``Select`` statements; services/routes construct them from
request input later.

Example (future repository)
---------------------------
    from app.core.query import FilterParams, Pagination, Sorting, apply_filters

    class CustomerFilters(FilterParams):
        # inherit name/phone/city/status; add more fields when needed
        pass

    class CustomerRepository(GenericRepository[Customer]):
        async def list_customers(
            self,
            *,
            pagination: Pagination | None = None,
            sorting: Sorting | None = None,
            filters: CustomerFilters | None = None,
        ) -> list[Customer]:
            return await self.get_all(
                pagination=pagination,
                sorting=sorting,
                filters=filters,
                # Map generic filter keys → Customer columns when they differ:
                filter_field_map={"name": "full_name", "phone": "phone_number"},
                allowed_sort_fields=frozenset({
                    "full_name", "phone_number", "city", "created_at", "updated_at",
                }),
            )
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields
from typing import Any, Literal, TypeVar

from sqlalchemy import Select, asc, desc
from sqlalchemy.orm import DeclarativeBase

from app.core.constants import (
    DEFAULT_PAGE_LIMIT,
    DEFAULT_SORT_BY,
    DEFAULT_SORT_ORDER,
    MAX_PAGE_LIMIT,
)
from app.core.exceptions import ValidationError

SortOrder = Literal["asc", "desc"]
ALLOWED_SORT_ORDERS: frozenset[str] = frozenset({"asc", "desc"})

StatementT = TypeVar("StatementT", bound=Select[Any])


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Pagination:
    """
    Offset/limit pagination with defaults and a hard maximum.

    - ``limit`` defaults to ``DEFAULT_PAGE_LIMIT`` and is capped at
      ``MAX_PAGE_LIMIT``.
    - ``offset`` defaults to ``0`` and must be non-negative.
    """

    limit: int = DEFAULT_PAGE_LIMIT
    offset: int = 0

    def __post_init__(self) -> None:
        if self.offset < 0:
            raise ValidationError("offset must be >= 0", field="offset")
        if self.limit < 1:
            raise ValidationError("limit must be >= 1", field="limit")
        # Cap oversized pages without rejecting the request.
        if self.limit > MAX_PAGE_LIMIT:
            object.__setattr__(self, "limit", MAX_PAGE_LIMIT)

    @classmethod
    def from_optional(
        cls,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Pagination:
        """Build from optional raw integers (e.g. legacy call sites)."""
        return cls(
            limit=DEFAULT_PAGE_LIMIT if limit is None else limit,
            offset=0 if offset is None else offset,
        )


def apply_pagination(statement: StatementT, pagination: Pagination) -> StatementT:
    """Apply ``OFFSET`` / ``LIMIT`` to a SQLAlchemy select."""
    return statement.offset(pagination.offset).limit(pagination.limit)


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Sorting:
    """
    Column sort specification.

    ``sort_order`` must be ``asc`` or ``desc``. Column allow-lists are
    enforced when the sort is applied to a statement (see ``apply_sorting``).
    """

    sort_by: str = DEFAULT_SORT_BY
    sort_order: SortOrder = DEFAULT_SORT_ORDER  # type: ignore[assignment]

    def __post_init__(self) -> None:
        order = self.sort_order.lower() if isinstance(self.sort_order, str) else self.sort_order
        if order not in ALLOWED_SORT_ORDERS:
            raise ValidationError(
                f"sort_order must be one of {sorted(ALLOWED_SORT_ORDERS)}",
                field="sort_order",
            )
        if not self.sort_by or not str(self.sort_by).strip():
            raise ValidationError("sort_by must be a non-empty column name", field="sort_by")
        object.__setattr__(self, "sort_order", order)
        object.__setattr__(self, "sort_by", str(self.sort_by).strip())


def apply_sorting(
    statement: StatementT,
    model: type[DeclarativeBase],
    sorting: Sorting,
    *,
    allowed_sort_fields: frozenset[str] | None = None,
) -> StatementT:
    """
    Apply ``ORDER BY`` for ``sorting.sort_by`` on ``model``.

    Raises ``ValidationError`` if the column is unknown or not allow-listed.
    """
    column_name = sorting.sort_by

    if allowed_sort_fields is not None and column_name not in allowed_sort_fields:
        raise ValidationError(
            f"sort_by must be one of {sorted(allowed_sort_fields)}",
            field="sort_by",
        )

    if not hasattr(model, column_name):
        raise ValidationError(
            f"Unknown sort column: {column_name!r}",
            field="sort_by",
        )

    column = getattr(model, column_name)
    order_expr = asc(column) if sorting.sort_order == "asc" else desc(column)
    return statement.order_by(order_expr)


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class FilterParams:
    """
    Optional, reusable filter bag for list endpoints.

    Modules subclass this to add fields without rewriting apply logic::

        @dataclass(frozen=True, slots=True)
        class QuotationFilters(FilterParams):
            quotation_number: str | None = None

    Base fields cover common ERP lookups (name, phone, city, status).
    Only non-``None`` values participate in the query.
    """

    name: str | None = None
    phone: str | None = None
    city: str | None = None
    status: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return all declared filter fields (including ``None``)."""
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def active(self) -> dict[str, Any]:
        """Return only filters with a non-``None`` value."""
        return {key: value for key, value in self.as_dict().items() if value is not None}


def apply_filters(
    statement: StatementT,
    model: type[DeclarativeBase],
    filters: FilterParams,
    *,
    field_map: Mapping[str, str] | None = None,
) -> StatementT:
    """
    Apply active filters to ``statement``.

    ``field_map`` remaps filter attribute names to model column names when
    they differ (e.g. ``{"name": "full_name", "phone": "phone_number"}``).

    Matching rules
    --------------
    - ``status`` → equality (``column == value``)
    - other string filters → case-insensitive contains (``ilike %value%``)
    - unknown / unmapped columns on the model are skipped (subclasses should
      pass an explicit ``field_map`` for their schema)

    Does not implement Customer-specific behaviour — callers supply the map.
    """
    mapping: dict[str, str] = {
        "name": "name",
        "phone": "phone",
        "city": "city",
        "status": "status",
    }
    if field_map:
        mapping.update(field_map)

    for key, value in filters.active().items():
        column_name = mapping.get(key, key)
        if not hasattr(model, column_name):
            continue

        column = getattr(model, column_name)
        if key == "status":
            statement = statement.where(column == value)
        elif isinstance(value, str):
            statement = statement.where(column.ilike(f"%{value}%"))
        else:
            statement = statement.where(column == value)

    return statement
