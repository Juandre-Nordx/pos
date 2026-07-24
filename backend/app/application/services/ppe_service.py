from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.inventory import WarehouseStock
from app.infrastructure.database.models.ppe import PPECategory, PPEEmployeeIssue, PPEItem
from app.schemas.ppe import PPECategoryResponse, PPEComplianceSummary, PPEIssueResponse, PPEItemResponse


class PPEService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_categories(self) -> list[PPECategoryResponse]:
        result = await self.session.execute(
            select(PPECategory).where(PPECategory.is_deleted.is_(False)).order_by(PPECategory.name)
        )
        categories = []
        for category in result.scalars().all():
            count_result = await self.session.execute(
                select(func.count()).select_from(PPEItem).where(
                    PPEItem.category_id == category.id, PPEItem.is_deleted.is_(False)
                )
            )
            categories.append(
                PPECategoryResponse(
                    uuid=category.uuid,
                    created_at=category.created_at,
                    updated_at=category.updated_at,
                    name=category.name,
                    slug=category.slug,
                    description=category.description,
                    item_count=count_result.scalar_one(),
                )
            )
        return categories

    async def list_items(self) -> list[PPEItemResponse]:
        result = await self.session.execute(
            select(PPEItem)
            .options(selectinload(PPEItem.category), selectinload(PPEItem.product))
            .where(PPEItem.is_deleted.is_(False))
            .order_by(PPEItem.name)
        )
        items = []
        for item in result.scalars().all():
            stock = 0
            if item.product_id:
                stock_result = await self.session.execute(
                    select(func.coalesce(func.sum(WarehouseStock.quantity), 0)).where(
                        WarehouseStock.product_id == item.product_id
                    )
                )
                stock = stock_result.scalar_one()
            items.append(
                PPEItemResponse(
                    uuid=item.uuid,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                    name=item.name,
                    category_name=item.category.name,
                    size=item.size,
                    standard=item.standard,
                    replacement_interval_days=item.replacement_interval_days,
                    current_stock=stock,
                    status=item.status,
                )
            )
        return items

    async def list_issues(self) -> list[PPEIssueResponse]:
        today = datetime.now(UTC).date()
        result = await self.session.execute(
            select(PPEEmployeeIssue)
            .options(
                selectinload(PPEEmployeeIssue.employee),
                selectinload(PPEEmployeeIssue.ppe_item).selectinload(PPEItem.category),
            )
            .where(PPEEmployeeIssue.is_deleted.is_(False))
            .order_by(PPEEmployeeIssue.issued_date.desc())
        )
        issues = []
        for issue in result.scalars().all():
            is_overdue = issue.replacement_due_date is not None and issue.replacement_due_date < today
            issues.append(
                PPEIssueResponse(
                    uuid=issue.uuid,
                    created_at=issue.created_at,
                    updated_at=issue.updated_at,
                    employee_name=issue.employee.full_name,
                    employee_number=issue.employee.employee_number,
                    ppe_item_name=issue.ppe_item.name,
                    ppe_category=issue.ppe_item.category.name,
                    issued_date=issue.issued_date,
                    replacement_due_date=issue.replacement_due_date,
                    quantity=issue.quantity,
                    condition=issue.condition,
                    status=issue.status,
                    is_overdue=is_overdue,
                )
            )
        return issues

    async def compliance_summary(self) -> PPEComplianceSummary:
        today = datetime.now(UTC).date()
        total_result = await self.session.execute(
            select(func.count()).select_from(PPEEmployeeIssue).where(PPEEmployeeIssue.is_deleted.is_(False))
        )
        total = total_result.scalar_one()
        overdue_result = await self.session.execute(
            select(func.count())
            .select_from(PPEEmployeeIssue)
            .where(
                PPEEmployeeIssue.is_deleted.is_(False),
                PPEEmployeeIssue.replacement_due_date.is_not(None),
                PPEEmployeeIssue.replacement_due_date < today,
            )
        )
        overdue = overdue_result.scalar_one()
        due_month_result = await self.session.execute(
            select(func.count())
            .select_from(PPEEmployeeIssue)
            .where(
                PPEEmployeeIssue.is_deleted.is_(False),
                PPEEmployeeIssue.replacement_due_date.is_not(None),
                func.extract("month", PPEEmployeeIssue.replacement_due_date) == today.month,
                func.extract("year", PPEEmployeeIssue.replacement_due_date) == today.year,
            )
        )
        due_month = due_month_result.scalar_one()
        compliance_rate = round(((total - overdue) / total * 100) if total else 100.0, 1)
        return PPEComplianceSummary(
            total_issued=total,
            overdue_replacements=overdue,
            due_this_month=due_month,
            compliance_rate=compliance_rate,
        )
