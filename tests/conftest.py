"""
Pytest fixtures for API tests.

Uses an isolated in-memory SQLite database so tests do not require Postgres.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.session import get_db
from app.main import app
from app.models.activity_log import ActivityLog
from app.models.customer import Customer
from app.models.job import Job
from app.models.measurement import Measurement
from app.models.measurement_item import MeasurementItem
from app.models.payment import Payment
from app.models.product import Product
from app.models.product_category import ProductCategory
from app.models.quotation import Quotation
from app.models.quotation_item import QuotationItem


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        for table in (
            ProductCategory.__table__,
            Product.__table__,
            Customer.__table__,
            Quotation.__table__,
            QuotationItem.__table__,
            Job.__table__,
            ActivityLog.__table__,
            Measurement.__table__,
            MeasurementItem.__table__,
            Payment.__table__,
        ):
            await conn.run_sync(
                lambda sync_conn, t=table: t.create(sync_conn, checkfirst=True)
            )

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
