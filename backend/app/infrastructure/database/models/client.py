from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.inventory import Product


class Client(Base, AuditMixin):
    __tablename__ = "clients"

    client_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    trading_name: Mapped[str | None] = mapped_column(String(255))
    vat_number: Mapped[str | None] = mapped_column(String(50))
    registration_number: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    payment_terms_days: Mapped[int] = mapped_column(default=30)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    notes_summary: Mapped[str | None] = mapped_column(Text)

    contacts: Mapped[list["ClientContact"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    addresses: Mapped[list["ClientAddress"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class ClientContact(Base, AuditMixin):
    __tablename__ = "client_contacts"

    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    mobile: Mapped[str | None] = mapped_column(String(50))
    position: Mapped[str | None] = mapped_column(String(100))
    is_primary: Mapped[bool] = mapped_column(default=False)
    is_billing_contact: Mapped[bool] = mapped_column(default=False)

    client: Mapped["Client"] = relationship(back_populates="contacts")


class ClientAddress(Base, AuditMixin):
    __tablename__ = "client_addresses"

    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    address_type: Mapped[str] = mapped_column(String(20), default="physical")
    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str | None] = mapped_column(String(100))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(2), default="ZA")
    is_default: Mapped[bool] = mapped_column(default=True)

    client: Mapped["Client"] = relationship(back_populates="addresses")
