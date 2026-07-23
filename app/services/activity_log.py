"""
ActivityLog service — centralized activity logging with rich metadata.

This service provides a unified interface for creating activity logs
across all business operations. It ensures consistent metadata capture
for audit trail and change tracking.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog


class ActivityLogService:
    """
    Centralized service for creating activity logs with rich metadata.
    
    Usage:
        log_service = ActivityLogService(session)
        await log_service.log(
            job_id=job.id,
            action="payment_updated",
            description="Payment amount changed",
            previous_value={"amount": "45000"},
            new_value={"amount": "50000"},
            user_name="Ahmed Hassan",
            entity_type="payment",
            entity_id=payment.id,
        )
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def log(
        self,
        *,
        job_id: uuid.UUID,
        action: str,
        description: str | None = None,
        previous_value: dict[str, Any] | str | None = None,
        new_value: dict[str, Any] | str | None = None,
        user_name: str | None = None,
        user_id: uuid.UUID | None = None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        event_metadata: dict[str, Any] | None = None,
    ) -> ActivityLog:
        """
        Create an activity log entry with rich metadata.
        
        Args:
            job_id: The job this activity belongs to
            action: Action identifier (e.g., "payment_updated", "status_changed")
            description: Human-readable description of the action
            previous_value: Previous value before change (dict or string)
            new_value: New value after change (dict or string)
            user_name: Name of user who performed the action
            user_id: UUID of user who performed the action
            entity_type: Type of related entity (payment, quotation, measurement, etc.)
            entity_id: UUID of related entity
            event_metadata: Additional structured data
            
        Returns:
            Created ActivityLog instance
        """
        # Convert dict values to JSON strings
        prev_str = self._serialize_value(previous_value)
        new_str = self._serialize_value(new_value)
        
        activity = ActivityLog(
            id=uuid.uuid4(),
            job_id=job_id,
            action=action,
            description=description,
            previous_value=prev_str,
            new_value=new_str,
            user_name=user_name,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            event_metadata=event_metadata,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        self._session.add(activity)
        await self._session.flush()
        
        return activity

    async def log_simple(
        self,
        *,
        job_id: uuid.UUID,
        action: str,
        description: str,
    ) -> ActivityLog:
        """
        Create a simple activity log entry (backward compatible).
        
        Use this for events that don't have change tracking.
        """
        return await self.log(
            job_id=job_id,
            action=action,
            description=description,
        )

    async def log_change(
        self,
        *,
        job_id: uuid.UUID,
        action: str,
        field_name: str,
        previous_value: Any,
        new_value: Any,
        user_name: str | None = None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
    ) -> ActivityLog:
        """
        Create an activity log for a single field change.
        
        Automatically generates description showing the change.
        """
        description = f"{field_name} changed from {previous_value} to {new_value}"
        
        return await self.log(
            job_id=job_id,
            action=action,
            description=description,
            previous_value={field_name: previous_value},
            new_value={field_name: new_value},
            user_name=user_name,
            entity_type=entity_type,
            entity_id=entity_id,
        )

    async def log_status_change(
        self,
        *,
        job_id: uuid.UUID,
        previous_status: str,
        new_status: str,
        user_name: str | None = None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
    ) -> ActivityLog:
        """
        Create an activity log for status changes.
        
        Convenience method for the common status change pattern.
        """
        return await self.log_change(
            job_id=job_id,
            action="status_changed",
            field_name="status",
            previous_value=previous_status,
            new_value=new_status,
            user_name=user_name,
            entity_type=entity_type,
            entity_id=entity_id,
        )

    async def log_entity_created(
        self,
        *,
        job_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        entity_description: str,
        user_name: str | None = None,
        event_metadata: dict[str, Any] | None = None,
    ) -> ActivityLog:
        """
        Create an activity log for entity creation.
        
        Example: Payment created, Measurement added, etc.
        """
        action = f"{entity_type}_created"
        description = f"{entity_type.title()} created: {entity_description}"
        
        return await self.log(
            job_id=job_id,
            action=action,
            description=description,
            user_name=user_name,
            entity_type=entity_type,
            entity_id=entity_id,
            event_metadata=event_metadata,
        )

    async def log_entity_updated(
        self,
        *,
        job_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        changes: dict[str, tuple[Any, Any]],
        user_name: str | None = None,
    ) -> ActivityLog:
        """
        Create an activity log for entity updates with multiple field changes.
        
        Args:
            changes: Dict mapping field names to (previous, new) tuples
            
        Example:
            changes = {
                "amount": (45000, 50000),
                "due_date": ("2024-01-01", "2024-01-15")
            }
        """
        action = f"{entity_type}_updated"
        
        # Build description listing all changes
        change_parts = []
        prev_dict = {}
        new_dict = {}
        
        for field, (prev, new) in changes.items():
            change_parts.append(f"{field}: {prev} → {new}")
            prev_dict[field] = prev
            new_dict[field] = new
        
        description = f"{entity_type.title()} updated: {', '.join(change_parts)}"
        
        return await self.log(
            job_id=job_id,
            action=action,
            description=description,
            previous_value=prev_dict,
            new_value=new_dict,
            user_name=user_name,
            entity_type=entity_type,
            entity_id=entity_id,
        )

    async def log_entity_deleted(
        self,
        *,
        job_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        entity_description: str,
        user_name: str | None = None,
    ) -> ActivityLog:
        """
        Create an activity log for entity deletion.
        """
        action = f"{entity_type}_deleted"
        description = f"{entity_type.title()} deleted: {entity_description}"
        
        return await self.log(
            job_id=job_id,
            action=action,
            description=description,
            user_name=user_name,
            entity_type=entity_type,
            entity_id=entity_id,
        )

    @staticmethod
    def _serialize_value(value: dict[str, Any] | str | None) -> str | None:
        """Convert value to JSON string if it's a dict."""
        if value is None:
            return None
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
