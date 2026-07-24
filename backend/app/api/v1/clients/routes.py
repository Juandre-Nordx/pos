from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.client_service import ClientService
from app.core.database import get_db_session
from app.core.dependencies import require_permission
from app.infrastructure.database.models.user import User
from app.schemas.client import ClientDetailResponse, ClientListItem
from app.schemas.common import PaginationMeta, ResponseEnvelope

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("", response_model=ResponseEnvelope[list[ClientListItem]])
async def list_clients(
    _: Annotated[User, Depends(require_permission("clients:read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=25, ge=1, le=100),
    search: str | None = Query(default=None),
) -> ResponseEnvelope[list[ClientListItem]]:
    service = ClientService(session)
    clients, meta = await service.list_clients(page=page, per_page=per_page, search=search)
    return ResponseEnvelope(data=clients, meta=meta.model_dump())


@router.get("/{client_uuid}", response_model=ResponseEnvelope[ClientDetailResponse])
async def get_client(
    client_uuid: UUID,
    _: Annotated[User, Depends(require_permission("clients:read"))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseEnvelope[ClientDetailResponse]:
    service = ClientService(session)
    client = await service.get_client(str(client_uuid))
    return ResponseEnvelope(data=client)
