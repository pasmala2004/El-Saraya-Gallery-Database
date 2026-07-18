"""Product model."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, true
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity

if TYPE_CHECKING:
    from app.models.product_category import ProductCategory
    from app.models.quotation_item import QuotationItem


class Product(BaseEntity):
    """
    Product entity.

    Represents a sellable product such as Sliding Window, Casement Window,
    French Door, Kitchen, Smart Lock, etc.

    Pricing is not stored here — unit prices live on QuotationItem.
    """

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("category_id", "name", name="uq_products_category_id_name"),
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    # Relationships — lazy="select" by default; use selectinload/joinedload in queries
    category: Mapped["ProductCategory"] = relationship(
        "ProductCategory",
        back_populates="products",
        lazy="select",
    )
    quotation_items: Mapped[list["QuotationItem"]] = relationship(
        "QuotationItem",
        back_populates="product",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', active={self.active})>"
