import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.infrastructure.database.models.client import Client
from app.schemas.client import ClientDetailResponse, ClientListItem
from app.schemas.common import PaginationMeta


class ClientService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_clients(self, *, page: int = 1, per_page: int = 25, search: str | None = None) -> tuple[list[ClientListItem], PaginationMeta]:
        query = select(Client).where(Client.is_deleted.is_(False))
        if search:
            pattern = f"%{search}%"
            query = query.where(
                Client.company_name.ilike(pattern)
                | Client.client_number.ilike(pattern)
                | Client.email.ilike(pattern)
            )

        count_result = await self.session.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        result = await self.session.execute(
            query.order_by(Client.company_name).offset((page - 1) * per_page).limit(per_page)
        )
        clients = [
            ClientListItem(
                uuid=client.uuid,
                created_at=client.created_at,
                updated_at=client.updated_at,
                client_number=client.client_number,
                company_name=client.company_name,
                trading_name=client.trading_name,
                email=client.email,
                phone=client.phone,
                status=client.status,
                credit_limit=client.credit_limit,
            )
            for client in result.scalars().all()
        ]
        meta = PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page)),
        )
        return clients, meta

    async def get_client(self, client_uuid: str) -> ClientDetailResponse:
        result = await self.session.execute(
            select(Client)
            .options(selectinload(Client.contacts), selectinload(Client.addresses))
            .where(Client.uuid == client_uuid, Client.is_deleted.is_(False))
        )
        client = result.scalar_one_or_none()
        if client is None:
            raise NotFoundException("Client not found")
        return ClientDetailResponse.model_validate(client)
