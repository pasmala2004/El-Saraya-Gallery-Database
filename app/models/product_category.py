"""ProductCategory model."""
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity

if TYPE_CHECKING:
    from app.models.product import Product


class ProductCategory(BaseEntity):
    """
    Product category entity.

    Used to group products into logical categories (e.g., Windows, Doors, Locks).
    """

    __tablename__ = "product_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Relationships
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ProductCategory(id={self.id}, name='{self.name}')>"
