from datetime import date

from pydantic import Field

from app.schemas.common import BaseSchema, TimestampSchema, UUIDSchema


class PPECategoryResponse(UUIDSchema, TimestampSchema):
    name: str
    slug: str
    description: str | None = None
    item_count: int = 0


class PPEItemResponse(UUIDSchema, TimestampSchema):
    name: str
    category_name: str
    size: str | None = None
    standard: str | None = None
    replacement_interval_days: int
    current_stock: int = 0
    status: str


class PPEIssueResponse(UUIDSchema, TimestampSchema):
    employee_name: str
    employee_number: str
    ppe_item_name: str
    ppe_category: str
    issued_date: date
    replacement_due_date: date | None = None
    quantity: int
    condition: str
    status: str
    is_overdue: bool = False


class PPEComplianceSummary(BaseSchema):
    total_issued: int
    overdue_replacements: int
    due_this_month: int
    compliance_rate: float


class PPEIssueCreateRequest(BaseSchema):
    employee_uuid: str
    ppe_item_uuid: str
    issued_date: date
    quantity: int = Field(default=1, ge=1)
    notes: str | None = None
