"""
Reusable FastAPI dependency providers.

Avoids repeating session → repository → service wiring in every module.

Example (future Customer module)
--------------------------------
    # app/api/deps.py already provides the helpers below.

    from app.api.deps import get_service
    from app.repositories.customer import CustomerRepository
    from app.services.customer import CustomerService

    get_customer_service = get_service(CustomerService, CustomerRepository)

    @router.get("/{customer_id}")
    async def read_customer(
        customer_id: uuid.UUID,
        service: CustomerService = Depends(get_customer_service),
    ) -> CustomerRead:
        return await service.get_by_id(customer_id)
"""
from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import BaseEntity
from app.db.session import get_db
from app.repositories.base import GenericRepository
from app.services.base import BaseService

ModelT = TypeVar("ModelT", bound=BaseEntity)
RepoT = TypeVar("RepoT", bound=GenericRepository)  # type: ignore[type-arg]
ServiceT = TypeVar("ServiceT", bound=BaseService)  # type: ignore[type-arg]


def get_repository(
    repository_cls: type[RepoT],
) -> Callable[..., RepoT]:
    """
    Build a FastAPI dependency that constructs ``repository_cls(session)``.

    Expects the repository constructor signature::

        def __init__(self, session: AsyncSession) -> None: ...
    """

    def _dependency(session: AsyncSession = Depends(get_db)) -> RepoT:
        return repository_cls(session)

    return _dependency


def get_service(
    service_cls: type[ServiceT],
    repository_cls: type[RepoT],
) -> Callable[..., ServiceT]:
    """
    Build a FastAPI dependency that wires session → repository → service.

    Expects::

        repository_cls(session: AsyncSession)
        service_cls(session: AsyncSession, repository: Repository)

    Future modules only need::

        get_customer_service = get_service(CustomerService, CustomerRepository)
    """

    def _dependency(session: AsyncSession = Depends(get_db)) -> ServiceT:
        repository = repository_cls(session)
        return service_cls(session, repository)

    return _dependency
