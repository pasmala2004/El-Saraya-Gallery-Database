"""
Generic service-layer foundation.

Responsibilities (Service)
--------------------------
- Own business rules and domain validation
- Orchestrate one or more repositories
- Control transaction boundaries (``commit`` / ``rollback``)
- Refresh entities after successful writes when callers need DB state

Why commit belongs here
-----------------------
A single use-case often touches multiple repositories (e.g. create
Quotation + QuotationItems). Committing inside a repository would leave
partial writes if a later step fails. The Service decides when the
unit of work is complete and commits once.
"""
from __future__ import annotations

import uuid
from typing import Generic, Protocol, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.core.query import FilterParams, Pagination, Sorting
from app.db.base import BaseEntity
from app.repositories.base import GenericRepository

ModelT = TypeVar("ModelT", bound=BaseEntity)


class ServiceProtocol(Protocol[ModelT]):
    """Structural interface for entity services (typing / tests)."""

    async def get_by_id(self, id: uuid.UUID) -> ModelT: ...

    async def list(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: FilterParams | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ModelT]: ...

    async def create(self, entity: ModelT, *, commit: bool = True) -> ModelT: ...

    async def update(self, entity: ModelT, *, commit: bool = True) -> ModelT: ...

    async def delete(self, id: uuid.UUID, *, commit: bool = True) -> None: ...


class BaseService(Generic[ModelT]):
    """
    Base application service for a single aggregate / entity type.

    Subclasses inject a typed repository and add domain methods::

        class CustomerService(BaseService[Customer]):
            def __init__(
                self,
                session: AsyncSession,
                repository: CustomerRepository,
            ) -> None:
                super().__init__(session, repository, entity_name="Customer")
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: GenericRepository[ModelT],
        *,
        entity_name: str,
    ) -> None:
        self._session = session
        self._repository = repository
        self._entity_name = entity_name

    @property
    def session(self) -> AsyncSession:
        return self._session

    @property
    def repository(self) -> GenericRepository[ModelT]:
        return self._repository

    # ------------------------------------------------------------------
    # Transaction helpers
    # ------------------------------------------------------------------

    async def commit(self) -> None:
        """Persist the current unit of work."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Revert the current unit of work."""
        await self._session.rollback()

    async def refresh(self, entity: ModelT) -> ModelT:
        """Reload ``entity`` from the database (e.g. after commit)."""
        await self._session.refresh(entity)
        return entity

    # ------------------------------------------------------------------
    # Generic use-cases (override in subclasses when needed)
    # ------------------------------------------------------------------

    async def get_by_id(self, id: uuid.UUID) -> ModelT:
        """Load an entity by id or raise ``EntityNotFoundError``."""
        entity = await self._repository.get_by_id(id)
        if entity is None:
            raise EntityNotFoundError(self._entity_name, id)
        return entity

    async def list(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: FilterParams | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ModelT]:
        """Return entities using shared pagination / sorting / filter helpers."""
        return await self._repository.get_all(
            pagination=pagination,
            sorting=sorting,
            filters=filters,
            limit=limit,
            offset=offset,
        )

    async def create(self, entity: ModelT, *, commit: bool = True) -> ModelT:
        """
        Persist a new entity.

        Set ``commit=False`` when composing multi-step use-cases that
        commit once at the end.
        """
        await self._repository.create(entity)
        if commit:
            await self.commit()
            await self.refresh(entity)
        return entity

    async def update(self, entity: ModelT, *, commit: bool = True) -> ModelT:
        """
        Persist changes to an existing tracked entity.

        Set ``commit=False`` for multi-step transactions.
        """
        await self._repository.update(entity)
        if commit:
            await self.commit()
            await self.refresh(entity)
        return entity

    async def delete(self, id: uuid.UUID, *, commit: bool = True) -> None:
        """Delete by id or raise ``EntityNotFoundError``."""
        entity = await self.get_by_id(id)
        await self._repository.delete(entity)
        if commit:
            await self.commit()

    async def exists(self, id: uuid.UUID) -> bool:
        """Return whether an entity with ``id`` exists."""
        return await self._repository.exists(id)
