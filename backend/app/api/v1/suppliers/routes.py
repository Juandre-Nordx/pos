from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.supplier_service import SupplierService
from app.core.database import get_db_session
from app.core.dependencies import require_permission
from app.infrastructure.database.models.user import User
from app.schemas.common import ResponseEnvelope
from app.schemas.supplier import (
    SupplierContactInput, SupplierContactResponse, SupplierCreateRequest, SupplierListItem,
    SupplierResponse, SupplierUpdateRequest,
)

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


def supplier_response(supplier, show_financial: bool) -> SupplierResponse:
    response = SupplierResponse.model_validate(supplier)
    if not show_financial:
        response.bank_details = None
        response.credit_limit = 0
        response.account_balance = 0
    response.contacts = [contact for contact in response.contacts if not next(
        item.is_deleted for item in supplier.contacts if item.uuid == contact.uuid)]
    return response


@router.get("", response_model=ResponseEnvelope[list[SupplierListItem]])
async def list_suppliers(
    _: Annotated[User, Depends(require_permission("suppliers:read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    page: int = Query(1, ge=1), per_page: int = Query(25, ge=1, le=100),
    search: str | None = None, active: bool | None = None,
) -> ResponseEnvelope[list[SupplierListItem]]:
    suppliers, meta = await SupplierService(session).list(page, per_page, search, active)
    data = [SupplierListItem.model_validate({**supplier.__dict__,
            "contact_count": sum(not contact.is_deleted for contact in supplier.contacts)}) for supplier in suppliers]
    return ResponseEnvelope(data=data, meta=meta.model_dump())


@router.post("", response_model=ResponseEnvelope[SupplierResponse], status_code=status.HTTP_201_CREATED)
async def create_supplier(payload: SupplierCreateRequest, request: Request,
    user: Annotated[User, Depends(require_permission("suppliers:create"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[SupplierResponse]:
    supplier = await SupplierService(session).create(payload, user.id, request.client.host if request.client else None)
    return ResponseEnvelope(data=supplier_response(supplier, user.has_permission("suppliers:financial")))


@router.get("/{supplier_uuid}", response_model=ResponseEnvelope[SupplierResponse])
async def get_supplier(supplier_uuid: UUID,
    user: Annotated[User, Depends(require_permission("suppliers:read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[SupplierResponse]:
    supplier = await SupplierService(session).get(supplier_uuid)
    return ResponseEnvelope(data=supplier_response(supplier, user.has_permission("suppliers:financial")))


@router.put("/{supplier_uuid}", response_model=ResponseEnvelope[SupplierResponse])
async def update_supplier(supplier_uuid: UUID, payload: SupplierUpdateRequest, request: Request,
    user: Annotated[User, Depends(require_permission("suppliers:update"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[SupplierResponse]:
    supplier = await SupplierService(session).update(supplier_uuid, payload, user.id, request.client.host if request.client else None)
    return ResponseEnvelope(data=supplier_response(supplier, user.has_permission("suppliers:financial")))


@router.post("/{supplier_uuid}/deactivate", response_model=ResponseEnvelope[SupplierResponse])
async def deactivate_supplier(supplier_uuid: UUID, request: Request,
    user: Annotated[User, Depends(require_permission("suppliers:update"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[SupplierResponse]:
    supplier = await SupplierService(session).deactivate(supplier_uuid, user.id, request.client.host if request.client else None)
    return ResponseEnvelope(data=supplier_response(supplier, user.has_permission("suppliers:financial")))


@router.post("/{supplier_uuid}/contacts", response_model=ResponseEnvelope[SupplierContactResponse],
             status_code=status.HTTP_201_CREATED)
async def add_supplier_contact(supplier_uuid: UUID, payload: SupplierContactInput,
    user: Annotated[User, Depends(require_permission("suppliers:update"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[SupplierContactResponse]:
    contact = await SupplierService(session).add_contact(supplier_uuid, payload, user.id)
    return ResponseEnvelope(data=SupplierContactResponse.model_validate(contact))
