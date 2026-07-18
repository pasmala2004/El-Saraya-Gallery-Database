"""
Reference data runner.

Seeds permanent master data only (product categories + products).

Usage:
    python -m app.database.seeders.reference.run_reference
    python -m app.database.seeders.reference.run_reference --clear
"""
import asyncio
import time

from app.core.logging import configure_logging, get_logger
from app.database.seeders.reference.product_category_seeder import (
    clear_categories,
    seed_categories,
)
from app.database.seeders.reference.product_seeder import (
    clear_products,
    seed_products,
)
from app.db.session import AsyncSessionLocal

configure_logging()
logger = get_logger(__name__)


async def seed_reference() -> None:
    """Seed reference (master) data only. Safe for production."""
    started = time.perf_counter()
    logger.info("Starting reference data seeding")

    async with AsyncSessionLocal() as session:
        categories = await seed_categories(session)
        products = await seed_products(session, categories)

    elapsed = time.perf_counter() - started
    logger.info(
        "Reference seeding complete. categories=%s products=%s elapsed=%.2fs",
        len(categories),
        len(products),
        elapsed,
    )


async def clear_reference() -> None:
    """
    Clear reference data (products then categories).

    Does not touch business tables. Fails if products are still referenced
    by quotation_items (RESTRICT FK).
    """
    logger.warning("Clearing reference data (products, categories)")
    async with AsyncSessionLocal() as session:
        await clear_products(session)
        await clear_categories(session)
    logger.warning("Reference data cleared")


def main() -> None:
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        asyncio.run(clear_reference())
    else:
        asyncio.run(seed_reference())


if __name__ == "__main__":
    main()
