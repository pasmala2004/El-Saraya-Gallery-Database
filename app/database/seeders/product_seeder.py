"""Product Seeder.

Seeds the products table with realistic products under each category.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.product import Product
from app.models.product_category import ProductCategory

logger = get_logger(__name__)

# Products organized by category
PRODUCTS_BY_CATEGORY = {
    "Windows": [
        "Sliding Window",
        "Casement Window",
        "Fixed Window",
        "Awning Window",
        "Bay Window",
        "Picture Window",
        "Double Hung Window",
        "Hopper Window",
    ],
    "Doors": [
        "Sliding Door",
        "French Door",
        "Bi-Fold Door",
        "Pivot Door",
        "Swing Door",
        "Pocket Door",
        "Glass Door",
        "Wooden Door",
    ],
    "Kitchens": [
        "Modern Kitchen",
        "Classic Kitchen",
        "L-Shaped Kitchen",
        "U-Shaped Kitchen",
        "Island Kitchen",
        "Galley Kitchen",
        "Open Kitchen",
        "Compact Kitchen",
    ],
    "Shower Cabins": [
        "Frameless Shower Cabin",
        "Semi-Frameless Shower Cabin",
        "Framed Shower Cabin",
        "Corner Shower Cabin",
        "Walk-In Shower",
        "Steam Shower Cabin",
        "Curved Shower Cabin",
        "Square Shower Cabin",
    ],
    "Smart Locks": [
        "Smart Lock X100",
        "Smart Lock Pro",
        "Fingerprint Smart Lock",
        "PIN Code Smart Lock",
        "Bluetooth Smart Lock",
        "WiFi Smart Lock",
        "Keyless Entry Lock",
        "Biometric Lock",
    ],
}


async def seed_products(
    session: AsyncSession,
    categories_map: dict[str, ProductCategory],
) -> list[Product]:
    """
    Seed products for all categories.
    
    Args:
        session: Database session
        categories_map: Dictionary mapping category names to ProductCategory instances
        
    Returns:
        List of all products (both newly created and existing)
        
    This operation is idempotent - running multiple times will not create duplicates.
    """
    logger.info("Starting product seeding...")
    
    all_products = []
    created_count = 0
    existing_count = 0
    
    for category_name, product_names in PRODUCTS_BY_CATEGORY.items():
        category = categories_map.get(category_name)
        
        if not category:
            logger.warning(f"Category '{category_name}' not found, skipping products")
            continue
        
        for product_name in product_names:
            # Check if product already exists
            result = await session.execute(
                select(Product).where(
                    Product.name == product_name,
                    Product.category_id == category.id,
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                all_products.append(existing)
                existing_count += 1
                logger.debug(f"Product '{product_name}' already exists")
            else:
                # Create new product
                product = Product(
                    name=product_name,
                    category_id=category.id,
                    active=True,
                )
                session.add(product)
                all_products.append(product)
                created_count += 1
                logger.debug(f"Created product '{product_name}' in category '{category_name}'")
    
    await session.commit()
    
    logger.info(
        f"Product seeding complete. Created: {created_count}, Existing: {existing_count}"
    )
    
    return all_products


async def clear_products(session: AsyncSession) -> None:
    """Clear all products (for testing purposes)."""
    result = await session.execute(select(Product))
    products = result.scalars().all()
    
    for product in products:
        await session.delete(product)
    
    await session.commit()
    logger.info(f"Cleared {len(products)} products")
