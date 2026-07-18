"""Job Seeder.

Seeds jobs for approved quotations with realistic lifecycle dates.
"""
import random
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.enums.job import JobStatus
from app.enums.quotation import QuotationStatus
from app.models.job import Job
from app.models.quotation import Quotation

logger = get_logger(__name__)


async def seed_jobs(
    session: AsyncSession,
    quotations: list[Quotation],
) -> list[Job]:
    """
    Seed jobs for approved quotations.
    
    Only creates jobs for quotations with APPROVED status.
    Generates realistic lifecycle dates based on job status.
    
    Args:
        session: Database session
        quotations: List of Quotation instances
        
    Returns:
        List of all jobs (both newly created and existing)
        
    This operation is idempotent based on quotation_id (1:1 relationship).
    """
    logger.info("Starting job seeding...")
    
    # Filter only approved quotations
    approved_quotations = [
        q for q in quotations if q.status == QuotationStatus.APPROVED
    ]
    
    if not approved_quotations:
        logger.warning("No approved quotations found, skipping job seeding")
        return []
    
    all_jobs = []
    created_count = 0
    existing_count = 0
    
    for quotation in approved_quotations:
        # Check if job already exists for this quotation
        result = await session.execute(
            select(Job).where(Job.quotation_id == quotation.id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            all_jobs.append(existing)
            existing_count += 1
            logger.debug(f"Job for quotation '{quotation.quotation_number}' already exists")
            continue
        
        # Generate job configuration
        job_config = _generate_job_config(quotation)
        
        # Create job
        job = Job(
            quotation_id=quotation.id,
            status=job_config["status"],
            measurement_date=job_config.get("measurement_date"),
            production_start=job_config.get("production_start"),
            production_end=job_config.get("production_end"),
            installation_date=job_config.get("installation_date"),
            delivery_date=job_config.get("delivery_date"),
            completion_date=job_config.get("completion_date"),
            notes=job_config.get("notes"),
        )
        session.add(job)
        all_jobs.append(job)
        created_count += 1
        logger.debug(
            f"Created job for quotation '{quotation.quotation_number}' "
            f"with status '{job_config['status'].value}'"
        )
    
    await session.commit()
    
    logger.info(
        f"Job seeding complete. Created: {created_count}, Existing: {existing_count}"
    )
    
    return all_jobs


def _generate_job_config(quotation: Quotation) -> dict:
    """
    Generate realistic job configuration with lifecycle dates.
    
    Jobs progress through stages with appropriate dates:
    - PENDING: No dates yet
    - MEASURING: measurement_date set
    - IN_PRODUCTION: measurement + production_start set
    - READY_FOR_INSTALLATION: production dates + installation_date set
    - INSTALLED: all dates up to installation_date set
    - COMPLETED: all dates set including completion_date
    """
    # Start from quotation date
    base_date = quotation.quotation_date
    
    # Randomly distribute jobs across different statuses
    status_distribution = [
        JobStatus.PENDING,
        JobStatus.MEASURING,
        JobStatus.IN_PRODUCTION,
        JobStatus.IN_PRODUCTION,  # More jobs in production
        JobStatus.READY_FOR_INSTALLATION,
        JobStatus.INSTALLED,
        JobStatus.COMPLETED,
        JobStatus.COMPLETED,  # More completed jobs
    ]
    
    status = random.choice(status_distribution)
    
    config = {
        "status": status,
        "measurement_date": None,
        "production_start": None,
        "production_end": None,
        "installation_date": None,
        "delivery_date": None,
        "completion_date": None,
        "notes": None,
    }
    
    # Generate dates based on status progression
    current_date = base_date
    
    if status == JobStatus.PENDING:
        config["notes"] = "Waiting for measurement scheduling"
        return config
    
    # MEASURING and beyond: set measurement_date
    if status in [
        JobStatus.MEASURING,
        JobStatus.IN_PRODUCTION,
        JobStatus.READY_FOR_INSTALLATION,
        JobStatus.INSTALLED,
        JobStatus.COMPLETED,
    ]:
        config["measurement_date"] = current_date + timedelta(days=random.randint(3, 7))
        current_date = config["measurement_date"]
        
        if status == JobStatus.MEASURING:
            config["notes"] = "Measurement visit scheduled"
            return config
    
    # IN_PRODUCTION and beyond: set production dates
    if status in [
        JobStatus.IN_PRODUCTION,
        JobStatus.READY_FOR_INSTALLATION,
        JobStatus.INSTALLED,
        JobStatus.COMPLETED,
    ]:
        config["production_start"] = current_date + timedelta(days=random.randint(2, 5))
        production_duration = random.randint(10, 25)  # 10-25 days production
        config["production_end"] = config["production_start"] + timedelta(days=production_duration)
        current_date = config["production_end"]
        
        if status == JobStatus.IN_PRODUCTION:
            config["notes"] = "Currently in production"
            return config
    
    # READY_FOR_INSTALLATION and beyond: set installation date
    if status in [
        JobStatus.READY_FOR_INSTALLATION,
        JobStatus.INSTALLED,
        JobStatus.COMPLETED,
    ]:
        config["installation_date"] = current_date + timedelta(days=random.randint(2, 7))
        # Delivery date is usually same or 1 day before installation
        config["delivery_date"] = config["installation_date"] - timedelta(days=random.randint(0, 1))
        current_date = config["installation_date"]
        
        if status == JobStatus.READY_FOR_INSTALLATION:
            config["notes"] = "Ready for installation"
            return config
    
    # INSTALLED: installation completed
    if status == JobStatus.INSTALLED:
        config["notes"] = "Installation completed, pending final inspection"
        return config
    
    # COMPLETED: all dates set
    if status == JobStatus.COMPLETED:
        config["completion_date"] = current_date + timedelta(days=random.randint(1, 3))
        config["notes"] = "Job completed successfully"
        return config
    
    return config


async def clear_jobs(session: AsyncSession) -> None:
    """Clear all jobs (for testing purposes)."""
    result = await session.execute(select(Job))
    jobs = result.scalars().all()
    
    for job in jobs:
        await session.delete(job)
    
    await session.commit()
    logger.info(f"Cleared {len(jobs)} jobs")
