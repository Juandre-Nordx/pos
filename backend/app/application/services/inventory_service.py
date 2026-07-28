import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.infrastructure.database.models.inventory import (
    Product,
    StockMovement,
    Warehouse,
    WarehouseStock,
)
from app.schemas.common import PaginationMeta
from app.schemas.inventory import (
    ProductDetailResponse,
    ProductListItem,
    StockAdditionRequest,
    StockAdditionResponse,
)


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
        self,
        *,
        page: int = 1,
        per_page: int = 25,
        search: str | None = None,
        low_stock_only: bool = False,
    ) -> tuple[list[ProductListItem], PaginationMeta]:
        query = select(Product).where(Product.is_deleted.is_(False)).order_by(Product.name)
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
        meta = PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page)),
        )
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

    async def add_stock(
        self, product_uuid: str, payload: StockAdditionRequest, user_id: int
    ) -> StockAdditionResponse:
        product_result = await self.session.execute(
            select(Product).where(Product.uuid == product_uuid, Product.is_deleted.is_(False))
        )
        product = product_result.scalar_one_or_none()
        if product is None:
            raise NotFoundException("Product not found")

        warehouse_result = await self.session.execute(
            select(Warehouse)
            .where(Warehouse.is_deleted.is_(False))
            .order_by(Warehouse.is_default.desc(), Warehouse.id)
            .limit(1)
        )
        warehouse = warehouse_result.scalar_one_or_none()
        if warehouse is None:
            raise NotFoundException("No inventory warehouse is configured")

        stock_result = await self.session.execute(
            select(WarehouseStock)
            .where(
                WarehouseStock.product_id == product.id,
                WarehouseStock.warehouse_id == warehouse.id,
                WarehouseStock.is_deleted.is_(False),
            )
            .with_for_update()
        )
        stock = stock_result.scalar_one_or_none()
        if stock is None:
            stock = WarehouseStock(
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity=0,
                reserved_quantity=0,
                created_by=user_id,
            )
            self.session.add(stock)

        quantity_before = stock.quantity
        stock.quantity += payload.quantity
        stock.updated_by = user_id
        self.session.add(
            StockMovement(
                product_id=product.id,
                warehouse_id=warehouse.id,
                movement_type="stock_receipt",
                quantity_before=quantity_before,
                quantity_changed=payload.quantity,
                quantity_after=stock.quantity,
                reason=payload.reason,
                reference=payload.reference,
                created_by=user_id,
            )
        )
        await self.session.flush()
        return StockAdditionResponse(
            product_uuid=str(product.uuid),
            warehouse_name=warehouse.name,
            quantity_before=quantity_before,
            quantity_added=payload.quantity,
            quantity_after=stock.quantity,
        )
