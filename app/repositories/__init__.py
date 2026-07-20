"""
Data-access layer.

Repositories encapsulate SQLAlchemy queries. They never commit, never
encode business rules, and are always used through a Service.
"""

from app.repositories.base import GenericRepository, RepositoryProtocol
from app.repositories.customer import CustomerRepository
from app.repositories.job import JobRepository
from app.repositories.measurement import MeasurementRepository
from app.repositories.measurement_item import MeasurementItemRepository
from app.repositories.payment import PaymentRepository
from app.repositories.product import ProductRepository
from app.repositories.product_category import ProductCategoryRepository
from app.repositories.quotation import QuotationRepository
from app.repositories.quotation_item import QuotationItemRepository

__all__ = [
    "GenericRepository",
    "RepositoryProtocol",
    "CustomerRepository",
    "JobRepository",
    "MeasurementRepository",
    "MeasurementItemRepository",
    "PaymentRepository",
    "ProductRepository",
    "ProductCategoryRepository",
    "QuotationRepository",
    "QuotationItemRepository",
]
