from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ResponseEnvelope(BaseModel, Generic[T]):
    data: T
    meta: dict | None = None
    errors: list[str] | None = None


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class UUIDSchema(BaseSchema):
    uuid: UUID


class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(UUIDSchema, TimestampSchema):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None = None
    avatar_url: str | None = None
    is_active: bool
    is_verified: bool
    roles: list[str] = []


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: datetime
