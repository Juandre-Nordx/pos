import math
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictException, NotFoundException
from app.infrastructure.database.models.inventory import Supplier, SupplierContact
from app.infrastructure.database.models.user import AuditLog
from app.schemas.common import PaginationMeta
from app.schemas.supplier import SupplierContactInput, SupplierCreateRequest, SupplierUpdateRequest


class SupplierService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, page: int, per_page: int, search: str | None, active: bool | None):
        query = select(Supplier).options(selectinload(Supplier.contacts)).where(Supplier.is_deleted.is_(False))
        count_query = select(func.count(Supplier.id)).where(Supplier.is_deleted.is_(False))
        filters = []
        if active is not None:
            filters.append(Supplier.is_active.is_(active))
        if search:
            term = f"%{search.strip()}%"
            contact_match = select(SupplierContact.supplier_id).where(
                SupplierContact.is_deleted.is_(False),
                or_(SupplierContact.full_name.ilike(term), SupplierContact.email.ilike(term),
                    SupplierContact.phone.ilike(term)),
            )
            filters.append(or_(Supplier.name.ilike(term), Supplier.code.ilike(term),
                               Supplier.contact_email.ilike(term), Supplier.phone.ilike(term),
                               Supplier.id.in_(contact_match)))
        query = query.where(*filters)
        count_query = count_query.where(*filters)
        total = int((await self.session.execute(count_query)).scalar_one())
        result = await self.session.execute(query.order_by(Supplier.name).offset((page - 1) * per_page).limit(per_page))
        return list(result.scalars().unique()), PaginationMeta(
            page=page, per_page=per_page, total=total,
            total_pages=max(1, math.ceil(total / per_page)),
        )

    async def get(self, supplier_uuid: UUID) -> Supplier:
        result = await self.session.execute(select(Supplier).options(selectinload(Supplier.contacts)).where(
            Supplier.uuid == supplier_uuid, Supplier.is_deleted.is_(False)))
        supplier = result.scalar_one_or_none()
        if supplier is None:
            raise NotFoundException("Supplier not found")
        return supplier

    async def create(self, payload: SupplierCreateRequest, user_id: int, ip_address: str | None) -> Supplier:
        if await self._code_exists(payload.code):
            raise ConflictException("Supplier code already exists")
        values = payload.model_dump(exclude={"contacts"})
        supplier = Supplier(**values, created_by=user_id)
        supplier.contacts = [SupplierContact(**contact.model_dump(), created_by=user_id) for contact in payload.contacts]
        self.session.add(supplier)
        await self.session.flush()
        self._audit(user_id, "supplier.created", supplier, None, self._audit_values(supplier), ip_address)
        return supplier

    async def update(self, supplier_uuid: UUID, payload: SupplierUpdateRequest, user_id: int,
                     ip_address: str | None) -> Supplier:
        supplier = await self.get(supplier_uuid)
        if await self._code_exists(payload.code, supplier.id):
            raise ConflictException("Supplier code already exists")
        old = self._audit_values(supplier)
        for field, value in payload.model_dump().items():
            setattr(supplier, field, value)
        supplier.updated_by = user_id
        await self.session.flush()
        self._audit(user_id, "supplier.updated", supplier, old, self._audit_values(supplier), ip_address)
        return supplier

    async def deactivate(self, supplier_uuid: UUID, user_id: int, ip_address: str | None) -> Supplier:
        supplier = await self.get(supplier_uuid)
        old = {"is_active": supplier.is_active}
        supplier.is_active = False
        supplier.updated_by = user_id
        self._audit(user_id, "supplier.deactivated", supplier, old, {"is_active": False}, ip_address)
        return supplier

    async def add_contact(self, supplier_uuid: UUID, payload: SupplierContactInput, user_id: int) -> SupplierContact:
        supplier = await self.get(supplier_uuid)
        if payload.is_primary:
            for contact in supplier.contacts:
                contact.is_primary = False
                contact.updated_by = user_id
        contact = SupplierContact(supplier_id=supplier.id, **payload.model_dump(), created_by=user_id)
        self.session.add(contact)
        await self.session.flush()
        return contact

    async def _code_exists(self, code: str, excluding_id: int | None = None) -> bool:
        query = select(Supplier.id).where(func.lower(Supplier.code) == code.lower(), Supplier.is_deleted.is_(False))
        if excluding_id:
            query = query.where(Supplier.id != excluding_id)
        return (await self.session.execute(query)).scalar_one_or_none() is not None

    @staticmethod
    def _audit_values(supplier: Supplier) -> dict:
        return {"name": supplier.name, "code": supplier.code, "contact_email": supplier.contact_email,
                "phone": supplier.phone, "is_active": supplier.is_active}

    def _audit(self, user_id: int, action: str, supplier: Supplier, old: dict | None,
               new: dict, ip_address: str | None) -> None:
        self.session.add(AuditLog(user_id=user_id, action=action, entity_type="supplier",
                                  entity_uuid=supplier.uuid, old_values=old, new_values=new,
                                  ip_address=ip_address, created_by=user_id))
