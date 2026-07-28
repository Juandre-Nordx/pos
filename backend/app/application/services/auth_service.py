from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import Settings
from app.core.exceptions import UnauthorizedException
from app.core.permissions import SYSTEM_PERMISSIONS, SYSTEM_ROLES, permission_key
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.infrastructure.database.models.user import (
    AuditLog,
    CompanySettings,
    LoginHistory,
    Permission,
    RefreshToken,
    Role,
    User,
)

logger = structlog.get_logger()


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    async def login(
        self,
        email: str,
        password: str,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, str, str]:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.email == email.lower(), User.is_deleted.is_(False))
        )
        user = result.scalar_one_or_none()

        if user is None or not verify_password(password, user.password_hash):
            logger.warning(
                "login_failed",
                email=email.lower(),
                ip_address=ip_address,
                reason="invalid_credentials",
            )
            self.session.add(
                LoginHistory(
                    email=email.lower(),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    failure_reason="Invalid credentials",
                )
            )
            await self.session.flush()
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            logger.warning(
                "login_failed",
                user_uuid=str(user.uuid),
                email=user.email,
                ip_address=ip_address,
                reason="account_inactive",
            )
            raise UnauthorizedException("Account is inactive")

        user.last_login_at = datetime.now(UTC)
        access_token = create_access_token(str(user.uuid), self.settings)
        refresh_token = create_refresh_token(str(user.uuid), self.settings)

        self.session.add(
            RefreshToken(
                user_id=user.id,
                token_hash=hash_token(refresh_token),
                expires_at=datetime.now(UTC) + timedelta(days=self.settings.jwt_refresh_token_expire_days),
                ip_address=ip_address,
                device_info=user_agent,
                created_by=user.id,
            )
        )
        self.session.add(
            LoginHistory(
                user_id=user.id,
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
                created_by=user.id,
            )
        )
        await self.session.flush()
        logger.info("user_login", user_uuid=str(user.uuid), email=user.email)
        return user, access_token, refresh_token

    async def get_current_user_profile(self, user: User) -> User:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user.id)
        )
        return result.scalar_one()


class SeedService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    async def seed_if_empty(self) -> bool:
        result = await self.session.execute(select(func.count()).select_from(User))
        if result.scalar_one() > 0:
            return False
        await self._seed_all()
        return True

    async def _seed_all(self) -> None:
        await self._seed_permissions_and_roles()
        await self._seed_company()
        await self._seed_admin_user()
        await self._seed_departments_employees()
        await self._seed_clients()
        await self._seed_inventory()
        await self._seed_ppe()
        await self._seed_audit_activity()
        await self.session.flush()
        logger.info("demo_data_seeded")

    async def _seed_permissions_and_roles(self) -> None:
        permission_map: dict[str, Permission] = {}
        for module, action, description in SYSTEM_PERMISSIONS:
            perm = Permission(module=module, action=action, description=description)
            self.session.add(perm)
            await self.session.flush()
            permission_map[permission_key(module, action)] = perm

        for role_slug, perms in SYSTEM_ROLES.items():
            role = Role(
                name=role_slug.replace("_", " ").title(),
                slug=role_slug,
                description=f"System role: {role_slug}",
                is_system=True,
            )
            if perms != ["*"]:
                role.permissions = [permission_map[p] for p in perms if p in permission_map]
            else:
                role.permissions = list(permission_map.values())
            self.session.add(role)
        await self.session.flush()

    async def _seed_company(self) -> None:
        self.session.add(
            CompanySettings(
                company_name="Nordx Industrial Supplies (Pty) Ltd",
                trading_name="NordxPOS Demo",
                registration_number="2021/123456/07",
                vat_number="4123456789",
                email="info@demo.nordxpos.co.za",
                phone="+27 11 555 0100",
                website="https://demo.nordxpos.co.za",
                address={
                    "line1": "42 Industrial Boulevard",
                    "city": "Johannesburg",
                    "province": "Gauteng",
                    "postal_code": "2001",
                    "country": "ZA",
                },
                currency="ZAR",
                locale="en-ZA",
                timezone="Africa/Johannesburg",
            )
        )

    async def _seed_admin_user(self) -> None:
        result = await self.session.execute(select(Role).where(Role.slug == "super_admin"))
        super_admin = result.scalar_one()
        user = User(
            email=self.settings.demo_admin_email.lower(),
            password_hash=hash_password(self.settings.demo_admin_password),
            first_name="Demo",
            last_name="Administrator",
            phone="+27 82 555 0100",
            is_active=True,
            is_verified=True,
            roles=[super_admin],
        )
        self.session.add(user)
        await self.session.flush()

    async def _seed_departments_employees(self) -> None:
        from app.infrastructure.database.models.employee import Department, Employee

        departments = [
            Department(name="Operations", description="Field operations and logistics"),
            Department(name="Warehouse", description="Inventory and stock management"),
            Department(name="Sales", description="Client relations and sales"),
            Department(name="Finance", description="Accounts and finance"),
        ]
        self.session.add_all(departments)
        await self.session.flush()

        employees_data = [
            ("EMP-001", "Thabo", "Mokoena", "Operations Manager", departments[0].id),
            ("EMP-002", "Sarah", "Van Wyk", "Warehouse Supervisor", departments[1].id),
            ("EMP-003", "James", "Ndlovu", "Sales Representative", departments[2].id),
            ("EMP-004", "Priya", "Pillay", "Finance Clerk", departments[3].id),
            ("EMP-005", "Michael", "Botha", "Field Technician", departments[0].id),
        ]
        for number, first, last, title, dept_id in employees_data:
            self.session.add(
                Employee(
                    employee_number=number,
                    first_name=first,
                    last_name=last,
                    job_title=title,
                    department_id=dept_id,
                    email=f"{first.lower()}.{last.lower()}@demo.nordxpos.co.za",
                    status="active",
                )
            )
        await self.session.flush()

    async def _seed_clients(self) -> None:
        from app.infrastructure.database.models.client import Client, ClientAddress, ClientContact

        clients_data = [
            {
                "number": "CLT-0001",
                "company": "Platinum Mining Solutions",
                "trading": "Platinum Mining",
                "vat": "4987654321",
                "reg": "2015/987654/07",
                "email": "accounts@platinummining.co.za",
                "phone": "+27 11 234 5678",
                "city": "Rustenburg",
            },
            {
                "number": "CLT-0002",
                "company": "Coastal Construction Group",
                "trading": "Coastal Construction",
                "vat": "4876543210",
                "reg": "2018/456789/07",
                "email": "procurement@coastalbuild.co.za",
                "phone": "+27 21 345 6789",
                "city": "Cape Town",
            },
            {
                "number": "CLT-0003",
                "company": "Eastern Logistics SA",
                "trading": "Eastern Logistics",
                "vat": "4765432109",
                "reg": "2019/321654/07",
                "email": "finance@easternlogistics.co.za",
                "phone": "+27 31 456 7890",
                "city": "Durban",
            },
            {
                "number": "CLT-0004",
                "company": "Highveld Engineering Works",
                "trading": "Highveld Engineering",
                "vat": "4654321098",
                "reg": "2017/654321/07",
                "email": "admin@highveldeng.co.za",
                "phone": "+27 12 567 8901",
                "city": "Pretoria",
            },
        ]

        for data in clients_data:
            client = Client(
                client_number=data["number"],
                company_name=data["company"],
                trading_name=data["trading"],
                vat_number=data["vat"],
                registration_number=data["reg"],
                email=data["email"],
                phone=data["phone"],
                credit_limit=250000,
                payment_terms_days=30,
                status="active",
            )
            client.contacts = [
                ClientContact(
                    first_name="Accounts",
                    last_name="Department",
                    email=data["email"],
                    phone=data["phone"],
                    is_primary=True,
                    is_billing_contact=True,
                )
            ]
            client.addresses = [
                ClientAddress(
                    address_type="physical",
                    line1=f"12 {data['city']} Business Park",
                    city=data["city"],
                    province="Gauteng" if data["city"] != "Cape Town" else "Western Cape",
                    postal_code="2000",
                    country="ZA",
                    is_default=True,
                )
            ]
            self.session.add(client)
        await self.session.flush()

    async def _seed_inventory(self) -> None:
        from decimal import Decimal

        from app.infrastructure.database.models.inventory import (
            Product,
            ProductCategory,
            Supplier,
            Warehouse,
            WarehouseStock,
        )

        supplier = Supplier(
            name="SafetyFirst Distributors SA",
            contact_email="orders@safetyfirst.co.za",
            phone="+27 11 789 0123",
            vat_number="4012345678",
            payment_terms_days=30,
        )
        self.session.add(supplier)
        await self.session.flush()

        categories = {
            "ppe-boots": ProductCategory(name="Safety Boots", slug="ppe-boots"),
            "ppe-gloves": ProductCategory(name="Safety Gloves", slug="ppe-gloves"),
            "ppe-helmets": ProductCategory(name="Hard Hats", slug="ppe-helmets"),
            "ppe-hivis": ProductCategory(name="Hi-Vis Clothing", slug="ppe-hivis"),
            "general": ProductCategory(name="General Supplies", slug="general"),
        }
        self.session.add_all(categories.values())
        await self.session.flush()

        warehouse = Warehouse(name="Main Warehouse", code="WH-MAIN", is_default=True)
        self.session.add(warehouse)
        await self.session.flush()

        products_data = [
            ("SKU-BOOT-001", "Steel Toe Safety Boot - Size 8", "ppe-boots", 850, 1299, 10, 45),
            ("SKU-BOOT-002", "Steel Toe Safety Boot - Size 10", "ppe-boots", 850, 1299, 10, 38),
            ("SKU-GLOVE-001", "Cut-Resistant Gloves - Large", "ppe-gloves", 120, 249, 25, 8),
            ("SKU-GLOVE-002", "Chemical Resistant Gloves - Medium", "ppe-gloves", 95, 189, 20, 150),
            ("SKU-HAT-001", "SANS Hard Hat - White", "ppe-helmets", 180, 349, 15, 62),
            ("SKU-HAT-002", "SANS Hard Hat - Yellow", "ppe-helmets", 180, 349, 15, 55),
            ("SKU-VIS-001", "Hi-Vis Vest - Large", "ppe-hivis", 85, 159, 30, 5),
            ("SKU-VIS-002", "Hi-Vis Jacket - XL", "ppe-hivis", 220, 399, 20, 72),
            ("SKU-GEN-001", "Industrial Cable Ties (100pk)", "general", 45, 89, 50, 200),
        ]

        for sku, name, cat_slug, purchase, selling, min_stock, qty in products_data:
            product = Product(
                sku=sku,
                name=name,
                category_id=categories[cat_slug].id,
                supplier_id=supplier.id,
                purchase_price=Decimal(str(purchase)),
                selling_price=Decimal(str(selling)),
                min_stock_level=min_stock,
                is_active=True,
            )
            self.session.add(product)
            await self.session.flush()
            self.session.add(
                WarehouseStock(
                    warehouse_id=warehouse.id,
                    product_id=product.id,
                    quantity=qty,
                )
            )
        await self.session.flush()

    async def _seed_ppe(self) -> None:
        from datetime import date, timedelta

        from app.infrastructure.database.models.employee import Employee
        from app.infrastructure.database.models.inventory import Product
        from app.infrastructure.database.models.ppe import PPECategory, PPEEmployeeIssue, PPEItem

        ppe_categories = {
            "boots": PPECategory(name="Safety Boots", slug="boots", description="Steel toe and composite safety footwear"),
            "gloves": PPECategory(name="Safety Gloves", slug="gloves", description="Cut, chemical and heat resistant gloves"),
            "helmets": PPECategory(name="Hard Hats", slug="helmets", description="SANS compliant head protection"),
            "hivis": PPECategory(name="Hi-Vis", slug="hivis", description="High visibility clothing"),
        }
        self.session.add_all(ppe_categories.values())
        await self.session.flush()

        result = await self.session.execute(select(Product).where(Product.sku.like("SKU-%")))
        products = result.scalars().all()
        ppe_items = []
        for product in products:
            cat_slug = "general"
            if "BOOT" in product.sku:
                cat_slug = "boots"
            elif "GLOVE" in product.sku:
                cat_slug = "gloves"
            elif "HAT" in product.sku:
                cat_slug = "helmets"
            elif "VIS" in product.sku:
                cat_slug = "hivis"
            if cat_slug == "general":
                continue
            size = None
            if "Size 8" in product.name:
                size = "8"
            elif "Size 10" in product.name:
                size = "10"
            elif "Large" in product.name:
                size = "L"
            elif "Medium" in product.name:
                size = "M"
            elif "XL" in product.name:
                size = "XL"
            item = PPEItem(
                category_id=ppe_categories[cat_slug].id,
                product_id=product.id,
                name=product.name,
                size=size,
                standard="SANS 20345" if cat_slug == "boots" else "SANS 501" if cat_slug == "gloves" else "SANS 1397",
                replacement_interval_days=365 if cat_slug == "boots" else 180,
                status="active",
            )
            self.session.add(item)
            ppe_items.append(item)
        await self.session.flush()

        emp_result = await self.session.execute(select(Employee).limit(5))
        employees = emp_result.scalars().all()
        today = date.today()
        for i, employee in enumerate(employees):
            if i >= len(ppe_items):
                break
            item = ppe_items[i]
            issued = today - timedelta(days=120 + i * 30)
            due = issued + timedelta(days=item.replacement_interval_days)
            self.session.add(
                PPEEmployeeIssue(
                    employee_id=employee.id,
                    ppe_item_id=item.id,
                    issued_date=issued,
                    replacement_due_date=due,
                    quantity=1,
                    condition="good" if due >= today else "worn",
                    status="issued" if due >= today else "replacement_due",
                )
            )
        await self.session.flush()

    async def _seed_audit_activity(self) -> None:
        from uuid import uuid4

        activities = [
            ("create", "client", "New client Platinum Mining Solutions added"),
            ("update", "product", "Stock adjusted for Safety Boots Size 8"),
            ("create", "ppe_issue", "PPE issued to Thabo Mokoena"),
            ("update", "client", "Coastal Construction credit limit updated"),
            ("create", "product", "New product Hi-Vis Jacket added to catalog"),
        ]
        for action, entity_type, description in activities:
            self.session.add(
                AuditLog(
                    action=action,
                    entity_type=entity_type,
                    entity_uuid=uuid4(),
                    new_values={"description": description},
                )
            )
