"""
Development-only demo business data.

This module must NEVER be imported by reference seeders or run_all.

It exists so developers can optionally populate a local database with
sample business records for UI/manual testing.

Production databases must not run this module.
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.database.seeders.reference.product_category_seeder import seed_categories
from app.database.seeders.reference.product_seeder import seed_products
from app.enums.job import JobStatus
from app.enums.payment import PaymentMethod, PaymentStatus, PaymentType
from app.enums.quotation import QuotationStatus
from app.models.activity_log import ActivityLog
from app.models.customer import Customer
from app.models.job import Job
from app.models.measurement import Measurement
from app.models.measurement_item import MeasurementItem
from app.models.payment import Payment
from app.models.product import Product
from app.models.quotation import Quotation
from app.models.quotation_item import QuotationItem
from app.models.report import Report

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Demo fixtures — local development only. Never used by production seeding.
# ---------------------------------------------------------------------------

DEMO_CUSTOMERS: list[dict] = [
    {
        "full_name": "Demo Customer One",
        "phone_number": "+20 100 000 0001",
        "alternative_phone": None,
        "address": "1 Demo Street",
        "city": "Cairo",
        "location_url": None,
        "notes": "Development demo record",
    },
    {
        "full_name": "Demo Customer Two",
        "phone_number": "+20 100 000 0002",
        "alternative_phone": None,
        "address": "2 Demo Street",
        "city": "Giza",
        "location_url": None,
        "notes": "Development demo record",
    },
]

PAYMENT_SCHEDULE = [
    {"order": 1, "type": PaymentType.DEPOSIT, "percentage": Decimal("70.00")},
    {"order": 2, "type": PaymentType.PRODUCTION, "percentage": Decimal("20.00")},
    {"order": 3, "type": PaymentType.FINAL, "percentage": Decimal("10.00")},
]


async def seed_demo_data(session: AsyncSession) -> None:
    """
    Insert a small, explicit demo dataset for local development.

    Requires at least one product in the catalog (reference seed + finalized
    PRODUCTS_BY_CATEGORY). Does not invent fake catalog products.
    """
    logger.warning("Seeding DEVELOPMENT demo business data (not for production)")

    categories = await seed_categories(session)
    await seed_products(session, categories)

    products_result = await session.execute(select(Product).where(Product.active.is_(True)))
    products = list(products_result.scalars().all())
    if not products:
        logger.error(
            "No products found. Finalize app.database.seeders.reference.product_seeder "
            "PRODUCTS_BY_CATEGORY, run reference seeding, then retry demo seeding."
        )
        return

    customers = await _seed_demo_customers(session)
    quotations = await _seed_demo_quotations(session, customers, products)
    jobs = await _seed_demo_jobs(session, quotations)
    await _seed_demo_payments(session, jobs)
    await _seed_demo_measurements(session, jobs)
    await _seed_demo_activity_logs(session, jobs)

    logger.warning(
        "Demo seeding finished. customers=%s quotations=%s jobs=%s",
        len(customers),
        len(quotations),
        len(jobs),
    )


async def clear_demo_business_data(session: AsyncSession) -> None:
    """
    Delete business tables in FK-safe order.

    Leaves reference catalog data (categories / products) intact.
    """
    logger.warning("Clearing demo/business tables (reference catalog kept)")

    for model in (
        ActivityLog,
        MeasurementItem,
        Measurement,
        Payment,
        Report,
        Job,
        QuotationItem,
        Quotation,
        Customer,
    ):
        result = await session.execute(select(model))
        rows = list(result.scalars().all())
        for row in rows:
            await session.delete(row)
        logger.info("Cleared %s %s row(s)", len(rows), model.__tablename__)

    await session.commit()
    logger.warning("Business tables cleared")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _seed_demo_customers(session: AsyncSession) -> list[Customer]:
    customers: list[Customer] = []
    for data in DEMO_CUSTOMERS:
        result = await session.execute(
            select(Customer).where(Customer.phone_number == data["phone_number"])
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            customers.append(existing)
            continue
        customer = Customer(**data)
        session.add(customer)
        customers.append(customer)
    await session.commit()
    return customers


async def _seed_demo_quotations(
    session: AsyncSession,
    customers: list[Customer],
    products: list[Product],
) -> list[Quotation]:
    quotations: list[Quotation] = []
    today = date.today()

    for index, customer in enumerate(customers, start=1):
        number = f"DEMO-{today.year}-{index:04d}"
        result = await session.execute(
            select(Quotation).where(Quotation.quotation_number == number)
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            quotations.append(existing)
            continue

        product = products[(index - 1) % len(products)]
        quantity = 2
        unit_price = Decimal("1500.00")
        line_total = unit_price * quantity
        discount = Decimal("0.00")
        status = QuotationStatus.APPROVED if index == 1 else QuotationStatus.DRAFT

        quotation = Quotation(
            quotation_number=number,
            customer_id=customer.id,
            quotation_date=today - timedelta(days=index),
            status=status,
            total_price=line_total,
            discount=discount,
            final_price=line_total - discount,
            notes="Development demo quotation",
        )
        session.add(quotation)
        await session.flush()

        session.add(
            QuotationItem(
                quotation_id=quotation.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=line_total,
                description=f"{product.name} (demo)",
                notes="Development demo line item",
            )
        )
        quotations.append(quotation)

    await session.commit()
    return quotations


async def _seed_demo_jobs(
    session: AsyncSession,
    quotations: list[Quotation],
) -> list[Job]:
    jobs: list[Job] = []
    approved = [q for q in quotations if q.status == QuotationStatus.APPROVED]

    for quotation in approved:
        result = await session.execute(
            select(Job).where(Job.quotation_id == quotation.id)
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            jobs.append(existing)
            continue

        measurement_date = quotation.quotation_date + timedelta(days=3)
        job = Job(
            quotation_id=quotation.id,
            status=JobStatus.MEASURING,
            measurement_date=measurement_date,
            notes="Development demo job",
        )
        session.add(job)
        jobs.append(job)

    await session.commit()
    return jobs


async def _seed_demo_payments(session: AsyncSession, jobs: list[Job]) -> list[Payment]:
    payments: list[Payment] = []

    for job in jobs:
        quotation_result = await session.execute(
            select(Quotation).where(Quotation.id == job.quotation_id)
        )
        quotation = quotation_result.scalar_one()

        for schedule in PAYMENT_SCHEDULE:
            result = await session.execute(
                select(Payment).where(
                    Payment.job_id == job.id,
                    Payment.payment_order == schedule["order"],
                )
            )
            existing = result.scalar_one_or_none()
            if existing is not None:
                payments.append(existing)
                continue

            amount = (
                quotation.final_price * schedule["percentage"] / Decimal("100")
            ).quantize(Decimal("0.01"))
            payment = Payment(
                job_id=job.id,
                payment_order=schedule["order"],
                payment_type=schedule["type"],
                payment_method=PaymentMethod.BANK_TRANSFER,
                percentage=schedule["percentage"],
                amount=amount,
                due_date=quotation.quotation_date + timedelta(days=7 * schedule["order"]),
                paid_date=None,
                status=PaymentStatus.PENDING,
                notes="Development demo payment",
            )
            session.add(payment)
            payments.append(payment)

    await session.commit()
    return payments


async def _seed_demo_measurements(
    session: AsyncSession,
    jobs: list[Job],
) -> list[Measurement]:
    measurements: list[Measurement] = []

    for job in jobs:
        if job.measurement_date is None:
            continue

        result = await session.execute(
            select(Measurement).where(
                Measurement.job_id == job.id,
                Measurement.measurement_number == 1,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            measurements.append(existing)
            continue

        measurement = Measurement(
            job_id=job.id,
            measurement_number=1,
            visit_date=job.measurement_date,
            measured_by="Demo Measurer",
            notes="Development demo measurement",
        )
        session.add(measurement)
        await session.flush()

        items_result = await session.execute(
            select(QuotationItem)
            .join(Quotation)
            .where(Quotation.id == job.quotation_id)
        )
        for quotation_item in items_result.scalars().all():
            session.add(
                MeasurementItem(
                    measurement_id=measurement.id,
                    quotation_item_id=quotation_item.id,
                    room_name="Demo Room",
                    piece_number="1",
                    width=Decimal("120.00"),
                    height=Decimal("140.00"),
                    quantity=1,
                    notes="Development demo measurement item",
                )
            )

        measurements.append(measurement)

    await session.commit()
    return measurements


async def _seed_demo_activity_logs(
    session: AsyncSession,
    jobs: list[Job],
) -> list[ActivityLog]:
    logs: list[ActivityLog] = []

    for job in jobs:
        result = await session.execute(
            select(ActivityLog).where(ActivityLog.job_id == job.id)
        )
        existing = list(result.scalars().all())
        if existing:
            logs.extend(existing)
            continue

        log = ActivityLog(
            job_id=job.id,
            action="Job Created",
            description="Development demo activity log",
        )
        session.add(log)
        logs.append(log)

    await session.commit()
    return logs
