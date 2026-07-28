from decimal import Decimal
from typing import Literal

from pydantic import EmailStr, Field, field_validator

from app.schemas.common import BaseSchema, TimestampSchema, UUIDSchema


class SupplierContactInput(BaseSchema):
    full_name: str = Field(min_length=1, max_length=255)
    job_title: str | None = Field(default=None, max_length=150)
    department: str | None = Field(default=None, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    alternative_phone: str | None = Field(default=None, max_length=50)
    preferred_contact_method: Literal["email", "phone", "sms"] = "email"
    is_primary: bool = False
    notes: str | None = None


class SupplierContactResponse(SupplierContactInput, UUIDSchema, TimestampSchema):
    pass


class SupplierInput(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    contact_person: str | None = Field(default=None, max_length=255)
    contact_email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    alternative_phone: str | None = Field(default=None, max_length=50)
    website: str | None = Field(default=None, max_length=500)
    physical_address: str | None = None
    billing_address: str | None = None
    city: str | None = Field(default=None, max_length=100)
    province: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default=None, max_length=100)
    registration_number: str | None = Field(default=None, max_length=100)
    vat_number: str | None = Field(default=None, max_length=50)
    payment_terms_days: int = Field(default=30, ge=0, le=3650)
    credit_limit: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    bank_details: dict | None = None
    lead_time_days: int = Field(default=0, ge=0, le=3650)
    minimum_order_amount: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    delivery_terms: str | None = None
    product_categories: list[str] = []
    notes: str | None = None
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()


class SupplierCreateRequest(SupplierInput):
    contacts: list[SupplierContactInput] = []

    @field_validator("contacts")
    @classmethod
    def one_primary_contact(cls, contacts: list[SupplierContactInput]) -> list[SupplierContactInput]:
        if sum(contact.is_primary for contact in contacts) > 1:
            raise ValueError("Only one contact may be primary")
        return contacts


class SupplierUpdateRequest(SupplierInput):
    pass


class SupplierResponse(SupplierInput, UUIDSchema, TimestampSchema):
    account_balance: Decimal = Decimal("0.00")
    contacts: list[SupplierContactResponse] = []


class SupplierListItem(UUIDSchema, TimestampSchema):
    name: str
    code: str
    contact_person: str | None
    contact_email: EmailStr | None
    phone: str | None
    city: str | None
    country: str | None
    is_active: bool
    contact_count: int
