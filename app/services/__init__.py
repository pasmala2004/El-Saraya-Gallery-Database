"""
Application service layer.

Services own business rules and transaction boundaries. They depend on
repositories via constructor injection and are provided to routes through
``app.api.deps.get_service``.
"""

from app.services.base import BaseService, ServiceProtocol
from app.services.customer import CustomerService
from app.services.product import ProductService
from app.services.product_category import ProductCategoryService
from app.services.quotation import QuotationService

__all__ = [
    "BaseService",
    "ServiceProtocol",
    "CustomerService",
    "ProductService",
    "ProductCategoryService",
    "QuotationService",
]
