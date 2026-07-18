"""Product reference seeder.

Seeds the permanent product catalog under product categories.

TODO: Finalize the real product catalog with the business, then populate
PRODUCTS_BY_CATEGORY below with production SKUs only.

Until the catalog is finalized this seeder intentionally inserts nothing.
Do not add placeholder, demo, or randomly generated products here.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.product import Product
from app.models.product_category import ProductCategory

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# TODO: Replace with the finalized production catalog.
#
# Example shape (do not leave fake SKUs in this list):
#   PRODUCTS_BY_CATEGORY = {
#       "Windows": ["Sliding Window", "Casement Window"],
#       "Doors": ["Sliding Door", "French Door"],
#       ...
#   }
# ---------------------------------------------------------------------------
PRODUCTS_BY_CATEGORY: dict[str, list[str]] = {
    "Windows": [],
    "Doors": [],
    "Kitchens": [],
    "Shower Cabins": [],
    "Smart Locks": [],
}


async def seed_products(
    session: AsyncSession,
    categories_map: dict[str, ProductCategory],
) -> list[Product]:
    """
    Upsert catalog products by (category_id, name) (idempotent).

    Returns every matching product found or created. When
    PRODUCTS_BY_CATEGORY is empty, returns an empty list and logs a notice.
    """
    total_defined = sum(len(names) for names in PRODUCTS_BY_CATEGORY.values())
    if total_defined == 0:
        logger.info(
            "Product catalog is empty (TODO: finalize PRODUCTS_BY_CATEGORY). "
            "Skipping product inserts."
        )
        return []

    logger.info("Seeding products (reference data)...")

    all_products: list[Product] = []
    created = 0
    existing = 0

    for category_name, product_names in PRODUCTS_BY_CATEGORY.items():
        category = categories_map.get(category_name)
        if category is None:
            logger.warning(
                "Category %r not found; skipping its products",
                category_name,
            )
            continue

        for product_name in product_names:
            result = await session.execute(
                select(Product).where(
                    Product.name == product_name,
                    Product.category_id == category.id,
                )
            )
            product = result.scalar_one_or_none()

            if product is not None:
                all_products.append(product)
                existing += 1
                continue

            product = Product(
                name=product_name,
                category_id=category.id,
                active=True,
            )
            session.add(product)
            all_products.append(product)
            created += 1

    await session.commit()
    logger.info(
        "Products seeded. created=%s existing=%s",
        created,
        existing,
    )
    return all_products


async def clear_products(session: AsyncSession) -> int:
    """Delete all products. Prefer clear_reference() for ordered deletes."""
    result = await session.execute(select(Product))
    products = list(result.scalars().all())
    for product in products:
        await session.delete(product)
    await session.commit()
    logger.info("Cleared %s products", len(products))
    return len(products)
