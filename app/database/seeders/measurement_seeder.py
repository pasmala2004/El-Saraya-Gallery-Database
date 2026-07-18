"""Measurement Seeder.

Seeds measurements and measurement items for jobs that have reached measurement stage.
"""
import random
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.job import Job
from app.models.measurement import Measurement
from app.models.measurement_item import MeasurementItem
from app.models.quotation import Quotation
from app.models.quotation_item import QuotationItem

logger = get_logger(__name__)

# Egyptian names for measurers
MEASURERS = [
    "محمد أحمد",
    "عمر حسن",
    "خالد محمود",
    "يوسف علي",
    "أحمد سعيد",
]

# Room names for measurements
ROOM_NAMES = [
    "Living Room",
    "Master Bedroom",
    "Bedroom 1",
    "Bedroom 2",
    "Kitchen",
    "Bathroom",
    "Guest Room",
    "Dining Room",
    "Office",
    "Entrance",
]


async def seed_measurements(
    session: AsyncSession,
    jobs: list[Job],
) -> list[Measurement]:
    """
    Seed measurements and measurement items for jobs.
    
    Only creates measurements for jobs that have measurement_date set.
    Creates realistic measurement items linked to quotation items.
    
    Args:
        session: Database session
        jobs: List of Job instances
        
    Returns:
        List of all measurements (both newly created and existing)
        
    This operation is idempotent based on (job_id, measurement_number).
    """
    logger.info("Starting measurement seeding...")
    
    # Filter jobs that have measurements scheduled
    jobs_with_measurements = [j for j in jobs if j.measurement_date is not None]
    
    if not jobs_with_measurements:
        logger.warning("No jobs with measurement dates found, skipping measurement seeding")
        return []
    
    all_measurements = []
    created_measurements = 0
    created_items = 0
    existing_measurements = 0
    
    for job in jobs_with_measurements:
        # Some jobs get re-measured (10% chance)
        num_measurements = 2 if random.random() < 0.1 else 1
        
        for measurement_number in range(1, num_measurements + 1):
            # Check if measurement already exists
            result = await session.execute(
                select(Measurement).where(
                    Measurement.job_id == job.id,
                    Measurement.measurement_number == measurement_number,
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                all_measurements.append(existing)
                existing_measurements += 1
                continue
            
            # Calculate visit date
            if measurement_number == 1:
                visit_date = job.measurement_date
            else:
                # Re-measurement is 7-14 days after first measurement
                visit_date = job.measurement_date + timedelta(days=random.randint(7, 14))
            
            # Create measurement
            measurement = Measurement(
                job_id=job.id,
                measurement_number=measurement_number,
                visit_date=visit_date,
                measured_by=random.choice(MEASURERS),
                notes=_generate_measurement_notes(measurement_number),
            )
            session.add(measurement)
            await session.flush()  # Get measurement ID
            all_measurements.append(measurement)
            created_measurements += 1
            
            # Create measurement items for each quotation item
            quotation_items_result = await session.execute(
                select(QuotationItem)
                .join(Quotation)
                .where(Quotation.id == job.quotation_id)
            )
            quotation_items = quotation_items_result.scalars().all()
            
            for qi in quotation_items:
                # Create 1-3 measurement items per quotation item (different pieces/rooms)
                num_pieces = random.randint(1, min(3, qi.quantity))
                
                for piece in range(num_pieces):
                    item = MeasurementItem(
                        measurement_id=measurement.id,
                        quotation_item_id=qi.id,
                        room_name=random.choice(ROOM_NAMES),
                        piece_number=_generate_piece_number(qi, piece + 1),
                        width=Decimal(str(random.uniform(80, 250))).quantize(Decimal("0.01")),
                        height=Decimal(str(random.uniform(100, 300))).quantize(Decimal("0.01")),
                        quantity=1,
                        notes=_generate_measurement_item_notes(),
                    )
                    session.add(item)
                    created_items += 1
    
    await session.commit()
    
    logger.info(
        f"Measurement seeding complete. Created: {created_measurements} measurements "
        f"with {created_items} items, Existing: {existing_measurements}"
    )
    
    return all_measurements


def _generate_measurement_notes(measurement_number: int) -> str | None:
    """Generate realistic measurement notes."""
    if measurement_number == 1:
        notes_options = [
            "Initial site measurements completed",
            "All measurements verified with customer",
            "Site conditions noted for production",
            "Special requirements discussed on-site",
            None,
        ]
    else:
        notes_options = [
            "Re-measurement due to site changes",
            "Customer requested measurement verification",
            "Updated measurements after wall modifications",
            "Final confirmation measurements",
        ]
    
    return random.choice(notes_options)


def _generate_piece_number(quotation_item: QuotationItem, piece_index: int) -> str:
    """Generate piece number identifier."""
    # Get product name from relationship (will be loaded)
    product_type = quotation_item.product.name.split()[0]  # e.g., "Sliding" from "Sliding Window"
    
    piece_identifiers = [
        f"{product_type} {piece_index}",
        f"{product_type} - Unit {piece_index}",
        f"{product_type} #{piece_index}",
    ]
    
    return random.choice(piece_identifiers)


def _generate_measurement_item_notes() -> str | None:
    """Generate realistic measurement item notes."""
    notes_options = [
        None,
        None,  # More likely to have no notes
        "Standard installation",
        "Custom fitting required",
        "Wall preparation needed",
        "Check clearance for opening",
        "Customer confirmed dimensions",
        "Special attention to alignment",
    ]
    
    return random.choice(notes_options)


async def clear_measurements(session: AsyncSession) -> None:
    """Clear all measurements and measurement items (for testing purposes)."""
    # Clear measurement items first (foreign key constraint)
    result = await session.execute(select(MeasurementItem))
    items = result.scalars().all()
    for item in items:
        await session.delete(item)
    
    # Clear measurements
    result = await session.execute(select(Measurement))
    measurements = result.scalars().all()
    for measurement in measurements:
        await session.delete(measurement)
    
    await session.commit()
    logger.info(f"Cleared {len(measurements)} measurements and {len(items)} items")
