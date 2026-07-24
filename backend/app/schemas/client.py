from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.common import BaseSchema, TimestampSchema, UUIDSchema


class ClientContactResponse(UUIDSchema, TimestampSchema):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    mobile: str | None = None
    position: str | None = None
    is_primary: bool
    is_billing_contact: bool


class ClientAddressResponse(UUIDSchema, TimestampSchema):
    address_type: str
    line1: str
    line2: str | None = None
    city: str
    province: str | None = None
    postal_code: str | None = None
    country: str
    is_default: bool


class ClientListItem(UUIDSchema, TimestampSchema):
    client_number: str
    company_name: str
    trading_name: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str
    credit_limit: Decimal


class ClientDetailResponse(ClientListItem):
    vat_number: str | None = None
    registration_number: str | None = None
    payment_terms_days: int
    notes_summary: str | None = None
    contacts: list[ClientContactResponse] = []
    addresses: list[ClientAddressResponse] = []


class ClientCreateRequest(BaseSchema):
    company_name: str = Field(min_length=1, max_length=255)
    trading_name: str | None = None
    vat_number: str | None = None
    registration_number: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    credit_limit: Decimal = Decimal("0.00")
    payment_terms_days: int = 30
    notes_summary: str | None = None
