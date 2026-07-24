from decimal import Decimal

from pydantic import Field

from app.schemas.common import BaseSchema, TimestampSchema, UUIDSchema


class ProductListItem(UUIDSchema, TimestampSchema):
    sku: str
    barcode: str | None = None
    name: str
    category_name: str | None = None
    purchase_price: Decimal
    selling_price: Decimal
    min_stock_level: int
    current_stock: int
    is_low_stock: bool
    is_active: bool
    unit_of_measure: str


class ProductDetailResponse(ProductListItem):
    description: str | None = None
    supplier_name: str | None = None
    track_serial: bool


class ProductCreateRequest(BaseSchema):
    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    barcode: str | None = None
    description: str | None = None
    purchase_price: Decimal = Decimal("0.00")
    selling_price: Decimal = Decimal("0.00")
    min_stock_level: int = 0
    unit_of_measure: str = "each"
