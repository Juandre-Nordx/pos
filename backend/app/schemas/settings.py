from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CompanyAddress(BaseModel):
    street: str = Field(default="", max_length=255)
    city: str = Field(default="", max_length=120)
    province: str = Field(default="", max_length=120)
    postal_code: str = Field(default="", max_length=20)
    country: str = Field(default="South Africa", max_length=120)


class CompanySettingsUpdate(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    trading_name: str | None = Field(default=None, max_length=255)
    registration_number: str | None = Field(default=None, max_length=100)
    vat_number: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    website: str | None = Field(default=None, max_length=255)
    address: CompanyAddress = Field(default_factory=CompanyAddress)
    logo_url: str | None = Field(default=None, max_length=500)


class CompanySettingsResponse(CompanySettingsUpdate):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
