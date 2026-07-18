"""Product Category Seeder.

Seeds the product_categories table with main business categories.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.product_category import ProductCategory

logger = get_logger(__name__)

CATEGORIES = [
    "Windows",
    "Doors",
    "Kitchens",
    "Shower Cabins",
    "Smart Locks",
]


async def seed_categories(session: AsyncSession) -> dict[str, ProductCategory]:
    """
    Seed product categories.
    
    Returns a dictionary mapping category names to ProductCategory instances
    for use by other seeders.
    
    This operation is idempotent - running multiple times will not create duplicates.
    """
    logger.info("Starting category seeding...")
    
    categories_map = {}
    created_count = 0
    existing_count = 0
    
    for category_name in CATEGORIES:
        # Check if category already exists
        result = await session.execute(
            select(ProductCategory).where(ProductCategory.name == category_name)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            categories_map[category_name] = existing
            existing_count += 1
            logger.debug(f"Category '{category_name}' already exists")
        else:
            # Create new category
            category = ProductCategory(name=category_name)
            session.add(category)
            categories_map[category_name] = category
            created_count += 1
            logger.debug(f"Created category '{category_name}'")
    
    await session.commit()
    
    logger.info(
        f"Category seeding complete. Created: {created_count}, Existing: {existing_count}"
    )
    
    return categories_map


async def clear_categories(session: AsyncSession) -> None:
    """Clear all categories (for testing purposes)."""
    result = await session.execute(select(ProductCategory))
    categories = result.scalars().all()
    
    for category in categories:
        await session.delete(category)
    
    await session.commit()
    logger.info(f"Cleared {len(categories)} categories")
