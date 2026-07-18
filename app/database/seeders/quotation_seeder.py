"""Quotation Seeder.

Seeds quotations and quotation items with realistic data.
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.enums.quotation import QuotationStatus
from app.models.customer import Customer
from app.models.product import Product
from app.models.quotation import Quotation
from app.models.quotation_item import QuotationItem

logger = get_logger(__name__)


async def seed_quotations(
    session: AsyncSession,
    customers: list[Customer],
    products: list[Product],
) -> list[Quotation]:
    """
    Seed quotations with realistic data.
    
    Creates quotations for customers with various statuses and line items.
    
    Args:
        session: Database session
        customers: List of Customer instances
        products: List of Product instances
        
    Returns:
        List of all quotations (both newly created and existing)
        
    This operation is idempotent based on quotation_number.
    """
    logger.info("Starting quotation seeding...")
    
    all_quotations = []
    created_count = 0
    existing_count = 0
    
    # Generate quotations for each customer (some get multiple quotations)
    quotation_configs = _generate_quotation_configs(customers, products)
    
    for config in quotation_configs:
        # Check if quotation already exists
        result = await session.execute(
            select(Quotation).where(
                Quotation.quotation_number == config["quotation_number"]
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            all_quotations.append(existing)
            existing_count += 1
            logger.debug(f"Quotation '{config['quotation_number']}' already exists")
            continue
        
        # Create quotation
        quotation = Quotation(
            quotation_number=config["quotation_number"],
            customer_id=config["customer_id"],
            quotation_date=config["quotation_date"],
            status=config["status"],
            total_price=config["total_price"],
            discount=config["discount"],
            final_price=config["final_price"],
            notes=config.get("notes"),
        )
        session.add(quotation)
        await session.flush()  # Get quotation ID
        
        # Create quotation items
        for item_data in config["items"]:
            item = QuotationItem(
                quotation_id=quotation.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                total_price=item_data["total_price"],
                description=item_data.get("description"),
                notes=item_data.get("notes"),
            )
            session.add(item)
        
        all_quotations.append(quotation)
        created_count += 1
        logger.debug(
            f"Created quotation '{config['quotation_number']}' "
            f"with {len(config['items'])} items"
        )
    
    await session.commit()
    
    logger.info(
        f"Quotation seeding complete. Created: {created_count}, "
        f"Existing: {existing_count}"
    )
    
    return all_quotations


def _generate_quotation_configs(
    customers: list[Customer],
    products: list[Product],
) -> list[dict]:
    """Generate quotation configurations with realistic data."""
    configs = []
    base_date = date.today() - timedelta(days=90)  # Start 90 days ago
    quotation_counter = 1
    
    # Distribute quotations across customers
    for i, customer in enumerate(customers):
        # Some customers get 1 quotation, some get 2
        num_quotations = 1 if i % 3 != 0 else 2
        
        for j in range(num_quotations):
            quotation_date = base_date + timedelta(days=i * 8 + j * 30)
            quotation_number = f"Q-{date.today().year}-{quotation_counter:04d}"
            quotation_counter += 1
            
            # Determine status (realistic distribution)
            if i % 5 == 0:
                status = QuotationStatus.DRAFT
            elif i % 5 == 1:
                status = QuotationStatus.SENT
            elif i % 5 == 2:
                status = QuotationStatus.REJECTED
            elif i % 5 == 3:
                status = QuotationStatus.CANCELLED
            else:
                status = QuotationStatus.APPROVED
            
            # Generate items (2-5 items per quotation)
            num_items = random.randint(2, 5)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            items = []
            total_price = Decimal("0.00")
            
            for product in selected_products:
                quantity = random.randint(1, 6)
                # Unit prices range from 1,000 to 50,000 EGP
                unit_price = Decimal(random.randint(100, 5000) * 10)
                item_total = unit_price * quantity
                
                items.append({
                    "product_id": product.id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": item_total,
                    "description": f"{product.name} - Custom specifications",
                    "notes": _generate_item_notes(product.name),
                })
                
                total_price += item_total
            
            # Apply discount (0-15%)
            discount_percentage = Decimal(random.choice([0, 5, 10, 15]))
            discount = (total_price * discount_percentage / 100).quantize(Decimal("0.01"))
            final_price = total_price - discount
            
            configs.append({
                "quotation_number": quotation_number,
                "customer_id": customer.id,
                "quotation_date": quotation_date,
                "status": status,
                "total_price": total_price,
                "discount": discount,
                "final_price": final_price,
                "notes": _generate_quotation_notes(status),
                "items": items,
            })
    
    return configs


def _generate_item_notes(product_name: str) -> str | None:
    """Generate realistic notes for quotation items."""
    notes_options = [
        None,
        "Standard finish",
        "Premium quality materials",
        "Installation included",
        "Custom measurements required",
        "Special order - 2 week lead time",
        "Customer provided dimensions",
    ]
    return random.choice(notes_options)


def _generate_quotation_notes(status: QuotationStatus) -> str | None:
    """Generate realistic notes based on quotation status."""
    if status == QuotationStatus.DRAFT:
        return "Pending final pricing confirmation"
    elif status == QuotationStatus.SENT:
        return "Awaiting customer response"
    elif status == QuotationStatus.APPROVED:
        return "Approved - proceed with production"
    elif status == QuotationStatus.REJECTED:
        return random.choice([
            "Customer found cheaper alternative",
            "Budget constraints",
            "Timeline too long",
        ])
    elif status == QuotationStatus.CANCELLED:
        return random.choice([
            "Project cancelled by customer",
            "Duplicate quotation",
            "Customer no longer interested",
        ])
    return None


async def clear_quotations(session: AsyncSession) -> None:
    """Clear all quotations and quotation items (for testing purposes)."""
    # Clear quotation items first (foreign key constraint)
    result = await session.execute(select(QuotationItem))
    items = result.scalars().all()
    for item in items:
        await session.delete(item)
    
    # Clear quotations
    result = await session.execute(select(Quotation))
    quotations = result.scalars().all()
    for quotation in quotations:
        await session.delete(quotation)
    
    await session.commit()
    logger.info(f"Cleared {len(quotations)} quotations and {len(items)} items")
