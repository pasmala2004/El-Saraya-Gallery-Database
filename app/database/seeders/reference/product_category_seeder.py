"""Product category reference seeder.

Seeds permanent product categories used by the catalog.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.product_category import ProductCategory

logger = get_logger(__name__)

# Permanent master data — safe for production.
CATEGORIES: list[str] = [
    "Windows",
    "Doors",
    "Kitchens",
    "Shower Cabins",
    "Smart Locks",
]


async def seed_categories(session: AsyncSession) -> dict[str, ProductCategory]:
    """
    Upsert product categories by name (idempotent).

    Returns a map of category name → ProductCategory for callers that
    need to attach products under these categories.
    """
    logger.info("Seeding product categories (reference data)...")

    categories_map: dict[str, ProductCategory] = {}
    created = 0
    existing = 0

    for name in CATEGORIES:
        result = await session.execute(
            select(ProductCategory).where(ProductCategory.name == name)
        )
        category = result.scalar_one_or_none()

        if category is not None:
            categories_map[name] = category
            existing += 1
            continue

        category = ProductCategory(name=name)
        session.add(category)
        categories_map[name] = category
        created += 1

    await session.commit()
    logger.info(
        "Product categories seeded. created=%s existing=%s",
        created,
        existing,
    )
    return categories_map


async def clear_categories(session: AsyncSession) -> int:
    """Delete all product categories. Prefer clear_reference() for ordered deletes."""
    result = await session.execute(select(ProductCategory))
    categories = list(result.scalars().all())
    for category in categories:
        await session.delete(category)
    await session.commit()
    logger.info("Cleared %s product categories", len(categories))
    return len(categories)
