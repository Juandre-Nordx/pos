from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.employee import Employee
    from app.infrastructure.database.models.inventory import Product


class PPECategory(Base, AuditMixin):
    __tablename__ = "ppe_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    items: Mapped[list["PPEItem"]] = relationship(back_populates="category")


class PPEItem(Base, AuditMixin):
    __tablename__ = "ppe_items"

    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("ppe_categories.id"), index=True)
    product_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("products.id"), unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    size: Mapped[str | None] = mapped_column(String(50))
    standard: Mapped[str | None] = mapped_column(String(100))
    replacement_interval_days: Mapped[int] = mapped_column(Integer, default=365)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")

    category: Mapped["PPECategory"] = relationship(back_populates="items")
    product: Mapped["Product | None"] = relationship(back_populates="ppe_item")
    issues: Mapped[list["PPEEmployeeIssue"]] = relationship(back_populates="ppe_item")


class PPEEmployeeIssue(Base, AuditMixin):
    __tablename__ = "ppe_employee_issues"

    employee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), index=True)
    ppe_item_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("ppe_items.id", ondelete="CASCADE"), index=True)
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    replacement_due_date: Mapped[date | None] = mapped_column(Date)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    condition: Mapped[str] = mapped_column(String(20), default="good")
    status: Mapped[str] = mapped_column(String(20), default="issued", index=True)
    notes: Mapped[str | None] = mapped_column(Text)

    employee: Mapped["Employee"] = relationship(back_populates="ppe_issues")
    ppe_item: Mapped["PPEItem"] = relationship(back_populates="issues")
    inspections: Mapped[list["PPEInspection"]] = relationship(back_populates="issue")


class PPEInspection(Base, AuditMixin):
    __tablename__ = "ppe_inspections"

    issue_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ppe_employee_issues.id", ondelete="CASCADE"), index=True
    )
    inspection_date: Mapped[date] = mapped_column(Date, nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    inspector_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"))

    issue: Mapped["PPEEmployeeIssue"] = relationship(back_populates="inspections")
