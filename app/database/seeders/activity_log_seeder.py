"""Activity Log Seeder.

Seeds activity logs for jobs to track lifecycle events.
"""
import random
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.activity_log import ActivityLog
from app.models.job import Job

logger = get_logger(__name__)


async def seed_activity_logs(
    session: AsyncSession,
    jobs: list[Job],
) -> list[ActivityLog]:
    """
    Seed activity logs for all jobs.
    
    Creates realistic activity log entries based on job lifecycle:
    - Job creation
    - Status changes
    - Measurement events
    - Production milestones
    - Installation events
    - Completion
    
    Args:
        session: Database session
        jobs: List of Job instances
        
    Returns:
        List of all activity logs (both newly created and existing)
        
    This operation is idempotent - checks for existing logs and only creates new ones.
    """
    logger.info("Starting activity log seeding...")
    
    if not jobs:
        logger.warning("No jobs found, skipping activity log seeding")
        return []
    
    all_logs = []
    created_count = 0
    
    for job in jobs:
        # Check if logs already exist for this job
        result = await session.execute(
            select(ActivityLog).where(ActivityLog.job_id == job.id)
        )
        existing_logs = result.scalars().all()
        
        if existing_logs:
            all_logs.extend(existing_logs)
            logger.debug(f"Job {job.id} already has {len(existing_logs)} activity logs")
            continue
        
        # Generate activity logs based on job lifecycle
        logs = _generate_activity_logs_for_job(job)
        
        for log_data in logs:
            log = ActivityLog(
                job_id=job.id,
                action=log_data["action"],
                description=log_data["description"],
            )
            session.add(log)
            all_logs.append(log)
            created_count += 1
    
    await session.commit()
    
    logger.info(f"Activity log seeding complete. Created: {created_count}")
    
    return all_logs


def _generate_activity_logs_for_job(job: Job) -> list[dict]:
    """Generate realistic activity log entries for a job's lifecycle."""
    logs = []
    
    # 1. Job creation (always present)
    logs.append({
        "action": "Job Created",
        "description": f"Job created from approved quotation with status: {job.status.value}",
    })
    
    # 2. Measurement scheduling
    if job.measurement_date:
        logs.append({
            "action": "Measurement Scheduled",
            "description": f"Site measurement scheduled for {job.measurement_date.strftime('%Y-%m-%d')}",
        })
        
        # 3. Measurement completed (if job progressed beyond measuring)
        if job.status.value not in ["pending", "measuring"]:
            logs.append({
                "action": "Measurement Completed",
                "description": "On-site measurements completed and verified",
            })
    
    # 4. Production events
    if job.production_start:
        logs.append({
            "action": "Production Started",
            "description": f"Production commenced on {job.production_start.strftime('%Y-%m-%d')}",
        })
        
        # Mid-production update
        if job.status.value not in ["pending", "measuring", "in_production"]:
            logs.append({
                "action": "Production Progress",
                "description": random.choice([
                    "50% production milestone reached",
                    "Quality check passed - production on track",
                    "Materials prepared and assembly in progress",
                ]),
            })
        
        if job.production_end:
            logs.append({
                "action": "Production Completed",
                "description": f"Production finished on {job.production_end.strftime('%Y-%m-%d')}",
            })
    
    # 5. Delivery and installation
    if job.delivery_date:
        logs.append({
            "action": "Delivery Scheduled",
            "description": f"Delivery scheduled for {job.delivery_date.strftime('%Y-%m-%d')}",
        })
    
    if job.installation_date:
        logs.append({
            "action": "Installation Scheduled",
            "description": f"Installation appointment set for {job.installation_date.strftime('%Y-%m-%d')}",
        })
        
        if job.status.value in ["installed", "completed"]:
            logs.append({
                "action": "Installation Started",
                "description": "Installation team arrived on-site and commenced work",
            })
            
            logs.append({
                "action": "Installation Completed",
                "description": "Installation completed successfully. Customer walk-through conducted.",
            })
    
    # 6. Quality checks and customer feedback
    if job.status.value in ["installed", "completed"]:
        logs.append({
            "action": "Quality Inspection",
            "description": random.choice([
                "Final quality inspection passed",
                "Customer satisfaction confirmed",
                "All items verified against specifications",
            ]),
        })
    
    # 7. Completion
    if job.completion_date:
        logs.append({
            "action": "Job Completed",
            "description": f"Job marked as completed on {job.completion_date.strftime('%Y-%m-%d')}. All deliverables met.",
        })
        
        logs.append({
            "action": "Documentation",
            "description": "Warranty documents and completion certificate issued to customer",
        })
    
    # 8. Add occasional communication logs
    if random.random() < 0.3:  # 30% chance
        logs.insert(
            random.randint(1, len(logs)),
            {
                "action": "Customer Communication",
                "description": random.choice([
                    "Customer called for status update - provided timeline",
                    "Email sent with production progress photos",
                    "WhatsApp update sent to customer",
                    "Customer visited showroom for color confirmation",
                ]),
            }
        )
    
    # 9. Add occasional issue logs (10% chance)
    if random.random() < 0.1 and len(logs) > 2:
        logs.insert(
            random.randint(1, len(logs) - 1),
            {
                "action": "Issue Resolved",
                "description": random.choice([
                    "Minor measurement adjustment made after customer feedback",
                    "Color mismatch resolved - new samples approved",
                    "Delivery rescheduled due to customer availability",
                    "Installation delay resolved - new appointment set",
                ]),
            }
        )
    
    return logs


async def clear_activity_logs(session: AsyncSession) -> None:
    """Clear all activity logs (for testing purposes)."""
    result = await session.execute(select(ActivityLog))
    logs = result.scalars().all()
    
    for log in logs:
        await session.delete(log)
    
    await session.commit()
    logger.info(f"Cleared {len(logs)} activity logs")
