"""
Measurement application service — on-site measurement tracking.

A Job can have multiple Measurement visits (tracked via measurement_number).
Each Measurement contains MeasurementItems that link to QuotationItems.
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BusinessRuleViolation,
    EntityNotFoundError,
    ValidationError,
)
from app.core.query import Pagination, Sorting
from app.models.activity_log import ActivityLog
from app.models.measurement import Measurement
from app.models.measurement_item import MeasurementItem
from app.repositories.job import JobRepository
from app.repositories.measurement import MeasurementFilters, MeasurementRepository
from app.repositories.measurement_item import MeasurementItemRepository
from app.repositories.quotation_item import QuotationItemRepository
from app.services.base import BaseService


class MeasurementService(BaseService[Measurement]):
    """Measurement workflow and item management."""

    def __init__(
        self,
        session: AsyncSession,
        repository: MeasurementRepository,
        item_repository: MeasurementItemRepository | None = None,
        job_repository: JobRepository | None = None,
        quotation_item_repository: QuotationItemRepository | None = None,
    ) -> None:
        super().__init__(session, repository, entity_name="Measurement")
        self._measurements = repository
        self._items = item_repository or MeasurementItemRepository(session)
        self._jobs = job_repository or JobRepository(session)
        self._quotation_items = quotation_item_repository or QuotationItemRepository(session)

    # ------------------------------------------------------------------
    # Measurement CRUD
    # ------------------------------------------------------------------

    async def get_measurement(
        self,
        measurement_id: uuid.UUID,
        *,
        load_items: bool = False,
    ) -> Measurement:
        """Get a single measurement by ID."""
        measurement = await self._measurements.get_by_id(
            measurement_id,
            load_items=load_items,
        )
        if measurement is None:
            raise EntityNotFoundError("Measurement", measurement_id)
        return measurement

    async def list_measurements(
        self,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        filters: MeasurementFilters | None = None,
    ) -> tuple[list[Measurement], int]:
        """List measurements with optional filtering, sorting, and pagination."""
        return await self._measurements.search(
            pagination=pagination,
            sorting=sorting,
            filters=filters,
        )

    async def list_job_measurements(
        self,
        job_id: uuid.UUID,
        *,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
    ) -> tuple[list[Measurement], int]:
        """List all measurements for a job."""
        # Verify job exists
        job = await self._jobs.get_by_id(job_id)
        if job is None:
            raise EntityNotFoundError("Job", job_id)

        return await self._measurements.list_by_job(
            job_id,
            pagination=pagination,
            sorting=sorting,
        )

    async def create_measurement(
        self,
        job_id: uuid.UUID,
        data: dict[str, Any],
    ) -> Measurement:
        """
        Create a new measurement for a job.

        Business rules:
        - Job must exist
        - measurement_number auto-increments from 1
        """
        # Verify job exists
        job = await self._jobs.get_by_id(job_id)
        if job is None:
            raise EntityNotFoundError("Job", job_id)

        # Get next measurement number
        measurement_number = await self._measurements.get_next_measurement_number(job_id)

        # Create measurement
        measurement_data = {
            "job_id": job_id,
            "measurement_number": measurement_number,
            "visit_date": data.get("visit_date"),
            "measured_by": self._trim_optional(data.get("measured_by")),
            "notes": self._trim_optional(data.get("notes")),
        }

        measurement = Measurement(**measurement_data)
        self._session.add(measurement)
        await self._session.flush()
        await self._session.refresh(measurement)

        # Log activity
        await self._log_activity(
            job_id=job_id,
            action="measurement_created",
            description=f"Measurement #{measurement_number} created",
        )

        return measurement

    async def update_measurement(
        self,
        measurement_id: uuid.UUID,
        data: dict[str, Any],
    ) -> Measurement:
        """Update measurement details."""
        measurement = await self.get_measurement(measurement_id)

        # Update allowed fields
        if "visit_date" in data:
            measurement.visit_date = data["visit_date"]

        if "measured_by" in data:
            measurement.measured_by = self._trim_optional(data["measured_by"])

        if "notes" in data:
            measurement.notes = self._trim_optional(data["notes"])

        await self._session.flush()
        await self._session.refresh(measurement)

        # Log activity
        await self._log_activity(
            job_id=measurement.job_id,
            action="measurement_updated",
            description=f"Measurement #{measurement.measurement_number} updated",
        )

        return measurement

    # ------------------------------------------------------------------
    # Measurement Items
    # ------------------------------------------------------------------

    async def list_items(self, measurement_id: uuid.UUID) -> list[MeasurementItem]:
        """List all items for a measurement."""
        # Verify measurement exists
        await self.get_measurement(measurement_id)
        return await self._items.list_by_measurement(measurement_id)

    async def add_item(
        self,
        measurement_id: uuid.UUID,
        data: dict[str, Any],
    ) -> MeasurementItem:
        """
        Add an item to a measurement.

        Business rules:
        - Measurement must exist
        - QuotationItem must exist
        - QuotationItem must belong to same quotation as Job
        """
        measurement = await self.get_measurement(measurement_id)

        # Get job and quotation
        job = await self._jobs.get_by_id(measurement.job_id)
        if job is None:
            raise EntityNotFoundError("Job", measurement.job_id)

        # Validate quotation item
        quotation_item_id = data.get("quotation_item_id")
        if not quotation_item_id:
            raise ValidationError("quotation_item_id is required")

        quotation_item = await self._quotation_items.get_by_id(quotation_item_id)
        if quotation_item is None:
            raise EntityNotFoundError("QuotationItem", quotation_item_id)

        # Validate quotation item belongs to job's quotation
        if quotation_item.quotation_id != job.quotation_id:
            raise BusinessRuleViolation(
                "QuotationItem must belong to the same quotation as the Job"
            )

        # Validate dimensions
        width = self._validate_dimension(data.get("width"), field="width")
        height = self._validate_dimension(data.get("height"), field="height")

        # Validate quantity
        quantity = int(data.get("quantity", 1))
        if quantity <= 0:
            raise ValidationError("quantity must be greater than 0", field="quantity")

        # Create item
        item_data = {
            "measurement_id": measurement_id,
            "quotation_item_id": quotation_item_id,
            "room_name": self._trim_optional(data.get("room_name")),
            "piece_number": self._trim_optional(data.get("piece_number")),
            "width": width,
            "height": height,
            "quantity": quantity,
            "notes": self._trim_optional(data.get("notes")),
        }

        item = MeasurementItem(**item_data)
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)

        # Log activity
        await self._log_activity(
            job_id=measurement.job_id,
            action="measurement_item_added",
            description=f"Item added to measurement #{measurement.measurement_number}",
        )

        return item

    async def update_item(
        self,
        item_id: uuid.UUID,
        data: dict[str, Any],
    ) -> MeasurementItem:
        """
        Update measurement item.

        Business rules:
        - Item must exist
        - If changing quotation_item_id, must validate same quotation
        """
        item = await self._items.get_by_id(item_id)
        if item is None:
            raise EntityNotFoundError("MeasurementItem", item_id)

        # Get measurement and job
        measurement = await self.get_measurement(item.measurement_id)
        job = await self._jobs.get_by_id(measurement.job_id)
        if job is None:
            raise EntityNotFoundError("Job", measurement.job_id)

        # Handle quotation_item_id change
        if "quotation_item_id" in data and data["quotation_item_id"] is not None:
            quotation_item_id = data["quotation_item_id"]
            quotation_item = await self._quotation_items.get_by_id(quotation_item_id)
            if quotation_item is None:
                raise EntityNotFoundError("QuotationItem", quotation_item_id)

            # Validate same quotation
            if quotation_item.quotation_id != job.quotation_id:
                raise BusinessRuleViolation(
                    "QuotationItem must belong to the same quotation as the Job"
                )

            item.quotation_item_id = quotation_item_id

        # Update other fields
        if "room_name" in data:
            item.room_name = self._trim_optional(data["room_name"])

        if "piece_number" in data:
            item.piece_number = self._trim_optional(data["piece_number"])

        if "width" in data:
            item.width = self._validate_dimension(data["width"], field="width")

        if "height" in data:
            item.height = self._validate_dimension(data["height"], field="height")

        if "quantity" in data and data["quantity"] is not None:
            quantity = int(data["quantity"])
            if quantity <= 0:
                raise ValidationError("quantity must be greater than 0", field="quantity")
            item.quantity = quantity

        if "notes" in data:
            item.notes = self._trim_optional(data["notes"])

        await self._session.flush()
        await self._session.refresh(item)

        # Log activity
        await self._log_activity(
            job_id=measurement.job_id,
            action="measurement_item_edited",
            description=f"Item in measurement #{measurement.measurement_number} edited",
        )

        return item

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _validate_dimension(
        self,
        value: Any,
        *,
        field: str,
    ) -> Decimal | None:
        """Validate and convert a dimension value."""
        if value is None:
            return None

        try:
            dimension = Decimal(str(value))
        except Exception as exc:
            raise ValidationError(
                f"Invalid dimension value for {field}",
                field=field,
            ) from exc

        if dimension < 0:
            raise ValidationError(
                f"{field} cannot be negative",
                field=field,
            )

        return dimension.quantize(Decimal("0.01"))

    @staticmethod
    def _trim_optional(value: Any) -> str | None:
        """Trim optional string value."""
        if value is None:
            return None
        trimmed = str(value).strip()
        return trimmed if trimmed else None

    async def _log_activity(
        self,
        *,
        job_id: uuid.UUID,
        action: str,
        description: str,
    ) -> None:
        """Create an activity log entry for the job."""
        activity = ActivityLog(
            job_id=job_id,
            action=action,
            description=description,
        )
        self._session.add(activity)
        await self._session.flush()

