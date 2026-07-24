from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.ppe import PPEEmployeeIssue
    from app.infrastructure.database.models.user import User


class Department(Base, AuditMixin):
    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    employees: Mapped[list["Employee"]] = relationship(back_populates="department")


class Employee(Base, AuditMixin):
    __tablename__ = "employees"

    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True)
    department_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("departments.id"))
    employee_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    job_title: Mapped[str | None] = mapped_column(String(150))
    hire_date: Mapped[Date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)

    user: Mapped["User | None"] = relationship(back_populates="employee")
    department: Mapped["Department | None"] = relationship(back_populates="employees")
    ppe_issues: Mapped[list["PPEEmployeeIssue"]] = relationship(back_populates="employee")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
