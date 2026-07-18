"""Customer Seeder.

Seeds the customers table with realistic Egyptian customers.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.customer import Customer

logger = get_logger(__name__)

# Realistic Egyptian customer data
CUSTOMERS = [
    {
        "full_name": "أحمد محمد حسن",
        "phone_number": "+20 100 123 4567",
        "alternative_phone": "+20 120 234 5678",
        "address": "15 شارع الجمهورية، الدور الثالث",
        "city": "Cairo",
        "location_url": "https://maps.google.com/?q=30.0444,31.2357",
        "notes": "Prefers morning appointments",
    },
    {
        "full_name": "فاطمة عبد الله إبراهيم",
        "phone_number": "+20 101 234 5678",
        "alternative_phone": None,
        "address": "28 شارع الهرم، أمام محطة المترو",
        "city": "Giza",
        "location_url": "https://maps.google.com/?q=29.9792,31.1342",
        "notes": "New villa project",
    },
    {
        "full_name": "محمود سعيد علي",
        "phone_number": "+20 102 345 6789",
        "alternative_phone": "+20 122 456 7890",
        "address": "42 شارع الشهداء، بجوار مسجد النور",
        "city": "Alexandria",
        "location_url": "https://maps.google.com/?q=31.2001,29.9187",
        "notes": "Commercial project - large order",
    },
    {
        "full_name": "نورا خالد يوسف",
        "phone_number": "+20 103 456 7890",
        "alternative_phone": "+20 123 567 8901",
        "address": "7 شارع النيل، الكورنيش",
        "city": "Cairo",
        "location_url": "https://maps.google.com/?q=30.0561,31.2394",
        "notes": "Apartment renovation",
    },
    {
        "full_name": "خالد حسين محمد",
        "phone_number": "+20 104 567 8901",
        "alternative_phone": None,
        "address": "33 شارع الجيش، المعادي",
        "city": "Cairo",
        "location_url": "https://maps.google.com/?q=29.9602,31.2569",
        "notes": "VIP client - priority service",
    },
    {
        "full_name": "مريم أحمد عبد الرحمن",
        "phone_number": "+20 105 678 9012",
        "alternative_phone": "+20 125 789 0123",
        "address": "19 شارع سعد زغلول، وسط البلد",
        "city": "Alexandria",
        "location_url": "https://maps.google.com/?q=31.1975,29.8925",
        "notes": "Kitchen and bathroom renovation",
    },
    {
        "full_name": "عمر طارق السيد",
        "phone_number": "+20 106 789 0123",
        "alternative_phone": "+20 126 890 1234",
        "address": "51 شارع التحرير، الدقي",
        "city": "Giza",
        "location_url": "https://maps.google.com/?q=30.0385,31.2118",
        "notes": "New construction project",
    },
    {
        "full_name": "سارة محمد فتحي",
        "phone_number": "+20 107 890 1234",
        "alternative_phone": None,
        "address": "12 شارع الشيخ زايد، القاهرة الجديدة",
        "city": "New Cairo",
        "location_url": "https://maps.google.com/?q=30.0131,31.4787",
        "notes": "Modern villa - full installation",
    },
    {
        "full_name": "يوسف عادل حسن",
        "phone_number": "+20 108 901 2345",
        "alternative_phone": "+20 128 012 3456",
        "address": "8 شارع الملك فيصل، الإسماعيلية",
        "city": "Ismailia",
        "location_url": "https://maps.google.com/?q=30.5833,32.2667",
        "notes": "Office building project",
    },
    {
        "full_name": "هدى إبراهيم عبد الله",
        "phone_number": "+20 109 012 3456",
        "alternative_phone": "+20 129 123 4567",
        "address": "25 شارع البحر، المنتزه",
        "city": "Alexandria",
        "location_url": "https://maps.google.com/?q=31.2969,30.0248",
        "notes": "Coastal villa - special requirements",
    },
]


async def seed_customers(session: AsyncSession) -> list[Customer]:
    """
    Seed customers with realistic Egyptian data.
    
    Returns:
        List of all customers (both newly created and existing)
        
    This operation is idempotent - running multiple times will not create duplicates.
    """
    logger.info("Starting customer seeding...")
    
    all_customers = []
    created_count = 0
    existing_count = 0
    
    for customer_data in CUSTOMERS:
        # Check if customer already exists (by phone number)
        result = await session.execute(
            select(Customer).where(
                Customer.phone_number == customer_data["phone_number"]
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            all_customers.append(existing)
            existing_count += 1
            logger.debug(f"Customer '{customer_data['full_name']}' already exists")
        else:
            # Create new customer
            customer = Customer(**customer_data)
            session.add(customer)
            all_customers.append(customer)
            created_count += 1
            logger.debug(f"Created customer '{customer_data['full_name']}'")
    
    await session.commit()
    
    logger.info(
        f"Customer seeding complete. Created: {created_count}, Existing: {existing_count}"
    )
    
    return all_customers


async def clear_customers(session: AsyncSession) -> None:
    """Clear all customers (for testing purposes)."""
    result = await session.execute(select(Customer))
    customers = result.scalars().all()
    
    for customer in customers:
        await session.delete(customer)
    
    await session.commit()
    logger.info(f"Cleared {len(customers)} customers")
