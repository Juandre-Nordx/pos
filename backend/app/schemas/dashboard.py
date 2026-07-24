from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.common import BaseSchema


class DashboardMetric(BaseSchema):
    label: str
    value: Decimal | int | str
    change_percent: float | None = None
    trend: str | None = None


class DashboardChartPoint(BaseSchema):
    month: str
    revenue: Decimal
    expenses: Decimal
    profit: Decimal


class DashboardActivityItem(BaseSchema):
    uuid: str
    action: str
    entity_type: str
    description: str
    user_name: str | None = None
    created_at: datetime


class DashboardResponse(BaseSchema):
    metrics: list[DashboardMetric]
    charts: list[DashboardChartPoint]
    activity: list[DashboardActivityItem]
    quick_actions: list[str] = Field(default_factory=list)
