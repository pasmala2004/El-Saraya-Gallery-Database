"""Payment Seeder.

Seeds payments for jobs with realistic payment schedules.
Every job gets 3 payments: 70% Deposit, 20% Production, 10% Final.
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.enums.payment import PaymentMethod, PaymentStatus, PaymentType
from app.models.job import Job
from app.models.payment import Payment
from app.models.quotation import Quotation

logger = get_logger(__name__)

# Payment split: 70% Deposit, 20% Production, 10% Final
PAYMENT_SCHEDULE = [
    {
        "order": 1,
        "type": PaymentType.DEPOSIT,
        "percentage": Decimal("70.00"),
    },
    {
        "order": 2,
        "type": PaymentType.PRODUCTION,
        "percentage": Decimal("20.00"),
    },
    {
        "order": 3,
        "type": PaymentType.FINAL,
        "percentage": Decimal("10.00"),
    },
]


async def seed_payments(
    session: AsyncSession,
    jobs: list[Job],
) -> list[Payment]:
    """
    Seed payments for all jobs.
    
    Creates 3 payments for each job:
    - 70% Deposit
    - 20% Production
    - 10% Final
    
    Payment status and dates are set realistically based on job status.
    
    Args:
        session: Database session
        jobs: List of Job instances
        
    Returns:
        List of all payments (both newly created and existing)
        
    This operation is idempotent based on (job_id, payment_order).
    """
    logger.info("Starting payment seeding...")
    
    if not jobs:
        logger.warning("No jobs found, skipping payment seeding")
        return []
    
    all_payments = []
    created_count = 0
    existing_count = 0
    
    for job in jobs:
        # Get quotation to calculate payment amounts
        result = await session.execute(
            select(Quotation).where(Quotation.id == job.quotation_id)
        )
        quotation = result.scalar_one()
        
        total_amount = quotation.final_price
        
        for payment_config in PAYMENT_SCHEDULE:
            # Check if payment already exists
            result = await session.execute(
                select(Payment).where(
                    Payment.job_id == job.id,
                    Payment.payment_order == payment_config["order"],
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                all_payments.append(existing)
                existing_count += 1
                continue
            
            # Calculate payment amount
            amount = (total_amount * payment_config["percentage"] / 100).quantize(
                Decimal("0.01")
            )
            
            # Generate payment details based on job status and payment type
            payment_details = _generate_payment_details(
                job, payment_config, quotation.quotation_date, amount
            )
            
            # Create payment
            payment = Payment(
                job_id=job.id,
                payment_order=payment_config["order"],
                payment_type=payment_config["type"],
                payment_method=payment_details["method"],
                percentage=payment_config["percentage"],
                amount=amount,
                due_date=payment_details["due_date"],
                paid_date=payment_details.get("paid_date"),
                status=payment_details["status"],
                notes=payment_details.get("notes"),
            )
            session.add(payment)
            all_payments.append(payment)
            created_count += 1
    
    await session.commit()
    
    logger.info(
        f"Payment seeding complete. Created: {created_count}, Existing: {existing_count}"
    )
    
    return all_payments


def _generate_payment_details(
    job: Job,
    payment_config: dict,
    quotation_date: date,
    amount: Decimal,
) -> dict:
    """
    Generate realistic payment details based on job status and payment type.
    
    Payment progression:
    - Deposit: Due immediately, usually paid early
    - Production: Due when production starts, paid during production
    - Final: Due at completion, paid after installation
    """
    payment_type = payment_config["type"]
    base_date = quotation_date
    
    # Random payment method
    methods = [
        PaymentMethod.CASH,
        PaymentMethod.BANK_TRANSFER,
        PaymentMethod.BANK_TRANSFER,  # Bank transfer most common
        PaymentMethod.INSTAPAY,
        PaymentMethod.CHEQUE,
    ]
    payment_method = random.choice(methods)
    
    # Deposit payment (70%)
    if payment_type == PaymentType.DEPOSIT:
        due_date = base_date + timedelta(days=3)
        
        # Deposit is usually paid for jobs in progress
        if job.status.value in ["pending", "measuring"]:
            # Not yet paid
            return {
                "method": payment_method,
                "due_date": due_date,
                "paid_date": None,
                "status": PaymentStatus.PENDING,
                "notes": "Deposit payment pending",
            }
        else:
            # Paid
            paid_date = due_date + timedelta(days=random.randint(0, 5))
            return {
                "method": payment_method,
                "due_date": due_date,
                "paid_date": paid_date,
                "status": PaymentStatus.PAID,
                "notes": f"Deposit paid via {payment_method.value}",
            }
    
    # Production payment (20%)
    elif payment_type == PaymentType.PRODUCTION:
        if job.production_start:
            due_date = job.production_start
        else:
            due_date = base_date + timedelta(days=15)
        
        # Production payment paid for advanced jobs
        if job.status.value in ["pending", "measuring", "in_production"]:
            # Not yet paid or pending
            if job.status.value == "in_production" and random.choice([True, False]):
                # 50% chance paid during production
                paid_date = due_date + timedelta(days=random.randint(0, 10))
                return {
                    "method": payment_method,
                    "due_date": due_date,
                    "paid_date": paid_date,
                    "status": PaymentStatus.PAID,
                    "notes": f"Production payment paid via {payment_method.value}",
                }
            else:
                return {
                    "method": payment_method,
                    "due_date": due_date,
                    "paid_date": None,
                    "status": PaymentStatus.PENDING,
                    "notes": "Production payment pending",
                }
        else:
            # Paid
            paid_date = due_date + timedelta(days=random.randint(0, 7))
            return {
                "method": payment_method,
                "due_date": due_date,
                "paid_date": paid_date,
                "status": PaymentStatus.PAID,
                "notes": f"Production payment paid via {payment_method.value}",
            }
    
    # Final payment (10%)
    elif payment_type == PaymentType.FINAL:
        if job.completion_date:
            due_date = job.completion_date
        elif job.installation_date:
            due_date = job.installation_date + timedelta(days=2)
        else:
            due_date = base_date + timedelta(days=40)
        
        # Final payment only paid for completed jobs
        if job.status.value == "completed":
            paid_date = due_date + timedelta(days=random.randint(0, 5))
            return {
                "method": payment_method,
                "due_date": due_date,
                "paid_date": paid_date,
                "status": PaymentStatus.PAID,
                "notes": f"Final payment paid via {payment_method.value}",
            }
        elif job.status.value == "installed":
            # 30% chance paid early
            if random.random() < 0.3:
                paid_date = date.today()
                return {
                    "method": payment_method,
                    "due_date": due_date,
                    "paid_date": paid_date,
                    "status": PaymentStatus.PAID,
                    "notes": f"Final payment paid early via {payment_method.value}",
                }
        
        # Check if overdue
        if due_date < date.today() and job.status.value in ["ready_for_installation", "installed"]:
            return {
                "method": payment_method,
                "due_date": due_date,
                "paid_date": None,
                "status": PaymentStatus.OVERDUE,
                "notes": "Final payment overdue - follow up required",
            }
        
        return {
            "method": payment_method,
            "due_date": due_date,
            "paid_date": None,
            "status": PaymentStatus.PENDING,
            "notes": "Final payment pending completion",
        }
    
    # Fallback
    return {
        "method": payment_method,
        "due_date": base_date + timedelta(days=7),
        "paid_date": None,
        "status": PaymentStatus.PENDING,
        "notes": None,
    }


async def clear_payments(session: AsyncSession) -> None:
    """Clear all payments (for testing purposes)."""
    result = await session.execute(select(Payment))
    payments = result.scalars().all()
    
    for payment in payments:
        await session.delete(payment)
    
    await session.commit()
    logger.info(f"Cleared {len(payments)} payments")
