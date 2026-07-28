from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.inventory_service import InventoryService
from app.core.database import get_db_session
from app.core.dependencies import require_permission
from app.infrastructure.database.models.user import User
from app.schemas.common import ResponseEnvelope
from app.schemas.inventory import (
    ProductDetailResponse,
    ProductListItem,
    StockAdditionRequest,
    StockAdditionResponse,
)

router = APIRouter(prefix="/inventory/products", tags=["Inventory"])


@router.get("", response_model=ResponseEnvelope[list[ProductListItem]])
async def list_products(
    _: Annotated[User, Depends(require_permission("inventory:read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=25, ge=1, le=100),
    search: str | None = Query(default=None),
    low_stock_only: bool = Query(default=False),
) -> ResponseEnvelope[list[ProductListItem]]:
    service = InventoryService(session)
    products, meta = await service.list_products(
        page=page, per_page=per_page, search=search, low_stock_only=low_stock_only
    )
    return ResponseEnvelope(data=products, meta=meta.model_dump())


@router.get("/{product_uuid}", response_model=ResponseEnvelope[ProductDetailResponse])
async def get_product(
    product_uuid: UUID,
    _: Annotated[User, Depends(require_permission("inventory:read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[ProductDetailResponse]:
    service = InventoryService(session)
    product = await service.get_product(str(product_uuid))
    return ResponseEnvelope(data=product)


@router.post("/{product_uuid}/stock", response_model=ResponseEnvelope[StockAdditionResponse])
async def add_stock(
    product_uuid: UUID,
    payload: StockAdditionRequest,
    user: Annotated[User, Depends(require_permission("inventory:write"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[StockAdditionResponse]:
    service = InventoryService(session)
    movement = await service.add_stock(str(product_uuid), payload, user.id)
    return ResponseEnvelope(data=movement)
