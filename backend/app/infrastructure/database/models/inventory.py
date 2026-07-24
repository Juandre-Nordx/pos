from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.ppe import PPEItem


class ProductCategory(Base, AuditMixin):
    __tablename__ = "product_categories"

    parent_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("product_categories.id"))
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Supplier(Base, AuditMixin):
    __tablename__ = "suppliers"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    contact_email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    vat_number: Mapped[str | None] = mapped_column(String(50))
    payment_terms_days: Mapped[int] = mapped_column(default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[list["Product"]] = relationship(back_populates="supplier")


class Warehouse(Base, AuditMixin):
    __tablename__ = "warehouses"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    stock_levels: Mapped[list["WarehouseStock"]] = relationship(back_populates="warehouse")


class Product(Base, AuditMixin):
    __tablename__ = "products"

    category_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("product_categories.id"))
    supplier_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("suppliers.id"))
    sku: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    barcode: Mapped[str | None] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    selling_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    min_stock_level: Mapped[int] = mapped_column(Integer, default=0)
    unit_of_measure: Mapped[str] = mapped_column(String(20), default="each")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    track_serial: Mapped[bool] = mapped_column(Boolean, default=False)

    category: Mapped["ProductCategory | None"] = relationship(back_populates="products")
    supplier: Mapped["Supplier | None"] = relationship(back_populates="products")
    stock_levels: Mapped[list["WarehouseStock"]] = relationship(back_populates="product")
    ppe_item: Mapped["PPEItem | None"] = relationship(back_populates="product", uselist=False)


class WarehouseStock(Base, AuditMixin):
    __tablename__ = "warehouse_stock"
    __table_args__ = (UniqueConstraint("warehouse_id", "product_id", name="uq_warehouse_product"),)

    warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("warehouses.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0)

    warehouse: Mapped["Warehouse"] = relationship(back_populates="stock_levels")
    product: Mapped["Product"] = relationship(back_populates="stock_levels")

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity
