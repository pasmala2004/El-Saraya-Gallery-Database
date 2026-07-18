"""
Generic async repository foundation.

Responsibilities (Repository)
-----------------------------
- Execute queries against the database
- Persist entities via ``session.add()``
- Delete entities via ``session.delete()``
- ``flush()`` pending state so the DB (and FK checks) run inside the
  current transaction
- Apply reusable list helpers (pagination / sorting / filtering)

Non-responsibilities
--------------------
- Never call ``commit()`` or ``rollback()``
- Never manage transaction boundaries
- Never encode business rules or validation beyond query-param allow-lists
- Never catch broad exceptions

Transaction ownership belongs to the Service layer.
"""
from __future__ import annotations

import uuid
from collections.abc import Mapping
from typing import Any, Generic, Protocol, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.query import (
    FilterParams,
    Pagination,
    Sorting,
    apply_filters,
    apply_pagination,
    apply_sorting,
)
from app.db.base import BaseEntity

ModelT = TypeVar("ModelT", bound=BaseEntity)


class RepositoryProtocol(Protocol[ModelT]):
    """
    Structural interface for repositories.

    Useful for typing and tests without forcing inheritance.
    """

    async def get_by_id(self, id: uuid.UUID) -> ModelT | None: ...

    async def get_all(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: FilterParams | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ModelT]: ...

    async def create(self, entity: ModelT) -> ModelT: ...

    async def update(self, entity: ModelT) -> ModelT: ...

    async def delete(self, entity: ModelT) -> None: ...

    async def exists(self, id: uuid.UUID) -> bool: ...


class GenericRepository(Generic[ModelT]):
    """
    Type-safe async CRUD repository for any ``BaseEntity`` model.

    Subclasses typically only bind the model type::

        class CustomerRepository(GenericRepository[Customer]):
            def __init__(self, session: AsyncSession) -> None:
                super().__init__(session, Customer)
    """

    #: Default columns callers may sort by when they do not pass an allow-list.
    _default_allowed_sort_fields: frozenset[str] = frozenset(
        {"id", "created_at", "updated_at"}
    )

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    @property
    def session(self) -> AsyncSession:
        """Expose the session for advanced queries in subclasses."""
        return self._session

    @property
    def model(self) -> type[ModelT]:
        return self._model

    # ------------------------------------------------------------------
    # Statement helpers (reuse in custom repository queries)
    # ------------------------------------------------------------------

    def base_select(self) -> Select[Any]:
        """Return ``select(Model)`` for composing custom queries."""
        return select(self._model)

    def apply_query_options(
        self,
        statement: Select[Any],
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: FilterParams | None = None,
        allowed_sort_fields: frozenset[str] | None = None,
        filter_field_map: Mapping[str, str] | None = None,
    ) -> Select[Any]:
        """
        Apply filters → sorting → pagination to ``statement``.

        Subclasses should call this from custom list methods instead of
        reimplementing offset/limit/order_by each time.
        """
        if filters is not None:
            statement = apply_filters(
                statement,
                self._model,
                filters,
                field_map=filter_field_map,
            )

        effective_sorting = sorting or Sorting()
        allow = (
            allowed_sort_fields
            if allowed_sort_fields is not None
            else self._default_allowed_sort_fields
        )
        statement = apply_sorting(
            statement,
            self._model,
            effective_sorting,
            allowed_sort_fields=allow,
        )

        if pagination is not None:
            statement = apply_pagination(statement, pagination)

        return statement

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    async def get_by_id(self, id: uuid.UUID) -> ModelT | None:
        """Return the entity with the given primary key, or ``None``."""
        return await self._session.get(self._model, id)

    async def get_all(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: FilterParams | None = None,
        allowed_sort_fields: frozenset[str] | None = None,
        filter_field_map: Mapping[str, str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ModelT]:
        """
        Return entities with optional filtering, sorting, and pagination.

        Prefer ``pagination`` / ``sorting`` / ``filters``. The ``limit`` and
        ``offset`` kwargs remain for simple call sites and build a
        ``Pagination`` when ``pagination`` is omitted.

        When neither ``pagination`` nor ``limit``/``offset`` is provided,
        results are not limited (full list, still sorted).
        """
        effective_pagination = pagination
        if effective_pagination is None and (limit is not None or offset is not None):
            effective_pagination = Pagination.from_optional(limit=limit, offset=offset)

        statement = self.apply_query_options(
            self.base_select(),
            pagination=effective_pagination,
            sorting=sorting,
            filters=filters,
            allowed_sort_fields=allowed_sort_fields,
            filter_field_map=filter_field_map,
        )
        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def create(self, entity: ModelT) -> ModelT:
        """
        Stage ``entity`` for insert and flush so defaults / FKs apply.

        Does not commit — the Service owns the transaction.
        """
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def update(self, entity: ModelT) -> ModelT:
        """
        Flush pending attribute changes on a tracked entity.

        Callers mutate the entity in memory first; this method only
        synchronizes the unit of work. Does not commit.
        """
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def delete(self, entity: ModelT) -> None:
        """Stage ``entity`` for deletion and flush. Does not commit."""
        await self._session.delete(entity)
        await self._session.flush()

    async def exists(self, id: uuid.UUID) -> bool:
        """Return ``True`` if a row with the given primary key exists."""
        stmt = select(self._model.id).where(self._model.id == id).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
