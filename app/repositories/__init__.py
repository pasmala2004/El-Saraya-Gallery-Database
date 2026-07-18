"""
Data-access layer.

Repositories encapsulate SQLAlchemy queries. They never commit, never
encode business rules, and are always used through a Service.
"""

from app.repositories.base import GenericRepository, RepositoryProtocol
from app.repositories.customer import CustomerRepository
from app.repositories.product import ProductRepository
from app.repositories.product_category import ProductCategoryRepository
from app.repositories.quotation import QuotationRepository
from app.repositories.quotation_item import QuotationItemRepository

__all__ = [
    "GenericRepository",
    "RepositoryProtocol",
    "CustomerRepository",
    "ProductRepository",
    "ProductCategoryRepository",
    "QuotationRepository",
    "QuotationItemRepository",
]
