import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.infrastructure.database.models.inventory import Product, WarehouseStock
from app.schemas.common import PaginationMeta
from app.schemas.inventory import ProductDetailResponse, ProductListItem


class InventoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_stock(self, product_id: int) -> int:
        result = await self.session.execute(
            select(func.coalesce(func.sum(WarehouseStock.quantity), 0)).where(
                WarehouseStock.product_id == product_id,
                WarehouseStock.is_deleted.is_(False),
            )
        )
        return result.scalar_one()

    async def list_products(
        self, *, page: int = 1, per_page: int = 25, search: str | None = None, low_stock_only: bool = False
    ) -> tuple[list[ProductListItem], PaginationMeta]:
        query = (
            select(Product)
            .where(Product.is_deleted.is_(False))
            .order_by(Product.name)
        )
        if search:
            pattern = f"%{search}%"
            query = query.where(Product.name.ilike(pattern) | Product.sku.ilike(pattern))

        result = await self.session.execute(query)
        all_products = result.scalars().all()

        items: list[ProductListItem] = []
        for product in all_products:
            current_stock = await self._get_stock(product.id)
            is_low = current_stock <= product.min_stock_level
            if low_stock_only and not is_low:
                continue
            items.append(
                ProductListItem(
                    uuid=product.uuid,
                    created_at=product.created_at,
                    updated_at=product.updated_at,
                    sku=product.sku,
                    barcode=product.barcode,
                    name=product.name,
                    category_name=product.category.name if product.category else None,
                    purchase_price=product.purchase_price,
                    selling_price=product.selling_price,
                    min_stock_level=product.min_stock_level,
                    current_stock=current_stock,
                    is_low_stock=is_low,
                    is_active=product.is_active,
                    unit_of_measure=product.unit_of_measure,
                )
            )

        total = len(items)
        start = (page - 1) * per_page
        paginated = items[start : start + per_page]
        meta = PaginationMeta(page=page, per_page=per_page, total=total, total_pages=max(1, math.ceil(total / per_page)))
        return paginated, meta

    async def get_product(self, product_uuid: str) -> ProductDetailResponse:
        result = await self.session.execute(
            select(Product).where(Product.uuid == product_uuid, Product.is_deleted.is_(False))
        )
        product = result.scalar_one_or_none()
        if product is None:
            raise NotFoundException("Product not found")
        current_stock = await self._get_stock(product.id)
        return ProductDetailResponse(
            uuid=product.uuid,
            created_at=product.created_at,
            updated_at=product.updated_at,
            sku=product.sku,
            barcode=product.barcode,
            name=product.name,
            category_name=product.category.name if product.category else None,
            purchase_price=product.purchase_price,
            selling_price=product.selling_price,
            min_stock_level=product.min_stock_level,
            current_stock=current_stock,
            is_low_stock=current_stock <= product.min_stock_level,
            is_active=product.is_active,
            unit_of_measure=product.unit_of_measure,
            description=product.description,
            supplier_name=product.supplier.name if product.supplier else None,
            track_serial=product.track_serial,
        )
