"""
ORM model registry.

Every model module must be imported here so that:
1. `Base.metadata` is fully populated when Alembic runs autogenerate.
2. SQLAlchemy's relationship resolution works across modules.
"""
from app.models.activity_log import ActivityLog
from app.models.customer import Customer
from app.models.job import Job
from app.models.measurement import Measurement
from app.models.measurement_item import MeasurementItem
from app.models.payment import Payment
from app.models.product import Product
from app.models.product_category import ProductCategory
from app.models.quotation import Quotation
from app.models.quotation_item import QuotationItem
from app.models.report import Report

__all__ = [
    "ActivityLog",
    "Customer",
    "ProductCategory",
    "Product",
    "Quotation",
    "QuotationItem",
    "Job",
    "Measurement",
    "MeasurementItem",
    "Payment",
    "Report",
]
