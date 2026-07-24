from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.client import Client
from app.infrastructure.database.models.inventory import Product, WarehouseStock
from app.infrastructure.database.models.ppe import PPEEmployeeIssue, PPEItem
from app.infrastructure.database.models.user import AuditLog
from app.schemas.dashboard import (
    DashboardActivityItem,
    DashboardChartPoint,
    DashboardMetric,
    DashboardResponse,
)


class DashboardService:
    MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_dashboard(self) -> DashboardResponse:
        client_count = await self._count_clients()
        product_count, stock_value, low_stock = await self._inventory_stats()
        ppe_overdue = await self._ppe_overdue_count()
        activity = await self._recent_activity()

        metrics = [
            DashboardMetric(label="Revenue (MTD)", value=Decimal("487250.00"), change_percent=12.4, trend="up"),
            DashboardMetric(label="Expenses (MTD)", value=Decimal("312890.00"), change_percent=-3.2, trend="down"),
            DashboardMetric(label="Profit (MTD)", value=Decimal("174360.00"), change_percent=18.7, trend="up"),
            DashboardMetric(label="Outstanding Invoices", value=Decimal("89340.00"), change_percent=5.1, trend="up"),
            DashboardMetric(label="Outstanding Quotes", value=Decimal("156200.00"), change_percent=-2.0, trend="down"),
            DashboardMetric(label="Clients", value=client_count, trend="up"),
            DashboardMetric(label="Stock Value", value=stock_value, trend="up"),
            DashboardMetric(label="Low Stock Items", value=low_stock, trend="down" if low_stock > 0 else "up"),
            DashboardMetric(label="PPE Replacements Due", value=ppe_overdue, trend="down" if ppe_overdue > 0 else "up"),
            DashboardMetric(label="Business Cases Waiting", value=3, trend="neutral"),
            DashboardMetric(label="Trip Requests Waiting", value=2, trend="neutral"),
        ]

        charts = [
            DashboardChartPoint(
                month=self.MONTHS[i],
                revenue=Decimal(str(320000 + i * 28000)),
                expenses=Decimal(str(210000 + i * 15000)),
                profit=Decimal(str(110000 + i * 13000)),
            )
            for i in range(7)
        ]

        return DashboardResponse(
            metrics=metrics,
            charts=charts,
            activity=activity,
            quick_actions=[
                "New Client",
                "Create Quote",
                "Issue PPE",
                "Stock Adjustment",
                "New Invoice",
            ],
        )

    async def _count_clients(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Client).where(Client.is_deleted.is_(False))
        )
        return result.scalar_one()

    async def _inventory_stats(self) -> tuple[int, Decimal, int]:
        products_result = await self.session.execute(
            select(Product).where(Product.is_deleted.is_(False), Product.is_active.is_(True))
        )
        products = products_result.scalars().all()
        stock_value = Decimal("0")
        low_stock = 0
        for product in products:
            stock_result = await self.session.execute(
                select(func.coalesce(func.sum(WarehouseStock.quantity), 0)).where(
                    WarehouseStock.product_id == product.id,
                    WarehouseStock.is_deleted.is_(False),
                )
            )
            qty = stock_result.scalar_one()
            stock_value += product.selling_price * qty
            if qty <= product.min_stock_level:
                low_stock += 1
        return len(products), stock_value, low_stock

    async def _ppe_overdue_count(self) -> int:
        today = datetime.now(UTC).date()
        result = await self.session.execute(
            select(func.count())
            .select_from(PPEEmployeeIssue)
            .where(
                PPEEmployeeIssue.is_deleted.is_(False),
                PPEEmployeeIssue.replacement_due_date.is_not(None),
                PPEEmployeeIssue.replacement_due_date < today,
                PPEEmployeeIssue.status == "issued",
            )
        )
        return result.scalar_one()

    async def _recent_activity(self) -> list[DashboardActivityItem]:
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.is_deleted.is_(False))
            .order_by(AuditLog.created_at.desc())
            .limit(8)
        )
        items = []
        for log in result.scalars().all():
            description = (log.new_values or {}).get("description", f"{log.action} {log.entity_type}")
            items.append(
                DashboardActivityItem(
                    uuid=str(log.uuid),
                    action=log.action,
                    entity_type=log.entity_type,
                    description=description,
                    created_at=log.created_at,
                )
            )
        return items
