"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "company_settings",
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("trading_name", sa.String(255)),
        sa.Column("registration_number", sa.String(100)),
        sa.Column("vat_number", sa.String(50)),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(50)),
        sa.Column("website", sa.String(255)),
        sa.Column("address", postgresql.JSONB()),
        sa.Column("logo_url", sa.String(500)),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("locale", sa.String(10), nullable=False),
        sa.Column("timezone", sa.String(50), nullable=False),
        sa.Column("settings", postgresql.JSONB()),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index("ix_company_settings_is_deleted", "company_settings", ["is_deleted"])
    op.create_index("ix_company_settings_uuid", "company_settings", ["uuid"])

    op.create_table(
        "roles",
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index("ix_roles_is_deleted", "roles", ["is_deleted"])
    op.create_index("ix_roles_slug", "roles", ["slug"])
    op.create_index("ix_roles_uuid", "roles", ["uuid"])

    op.create_table(
        "permissions",
        sa.Column("module", sa.String(50), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("description", sa.String(255)),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("module", "action", name="uq_permission_module_action"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.Column("permission_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    op.create_table(
        "users",
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(50)),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_is_deleted", "users", ["is_deleted"])
    op.create_index("ix_users_uuid", "users", ["uuid"])

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )

    for table_name, extra_cols in [
        ("refresh_tokens", [
            sa.Column("user_id", sa.BigInteger(), nullable=False),
            sa.Column("token_hash", sa.String(255), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked_at", sa.DateTime(timezone=True)),
            sa.Column("device_info", sa.String(500)),
            sa.Column("ip_address", sa.String(45)),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        ]),
        ("login_history", [
            sa.Column("user_id", sa.BigInteger()),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("ip_address", sa.String(45)),
            sa.Column("user_agent", sa.String(500)),
            sa.Column("success", sa.Boolean(), nullable=False),
            sa.Column("failure_reason", sa.String(255)),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        ]),
        ("audit_logs", [
            sa.Column("user_id", sa.BigInteger()),
            sa.Column("action", sa.String(100), nullable=False),
            sa.Column("entity_type", sa.String(100), nullable=False),
            sa.Column("entity_uuid", postgresql.UUID(as_uuid=True)),
            sa.Column("old_values", postgresql.JSONB()),
            sa.Column("new_values", postgresql.JSONB()),
            sa.Column("ip_address", sa.String(45)),
            sa.Column("user_agent", sa.String(500)),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        ]),
        ("departments", [
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("description", sa.Text()),
        ]),
        ("clients", [
            sa.Column("client_number", sa.String(50), nullable=False),
            sa.Column("company_name", sa.String(255), nullable=False),
            sa.Column("trading_name", sa.String(255)),
            sa.Column("vat_number", sa.String(50)),
            sa.Column("registration_number", sa.String(100)),
            sa.Column("email", sa.String(255)),
            sa.Column("phone", sa.String(50)),
            sa.Column("credit_limit", sa.Numeric(15, 2)),
            sa.Column("payment_terms_days", sa.Integer()),
            sa.Column("status", sa.String(20)),
            sa.Column("notes_summary", sa.Text()),
        ]),
        ("suppliers", [
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("contact_email", sa.String(255)),
            sa.Column("phone", sa.String(50)),
            sa.Column("vat_number", sa.String(50)),
            sa.Column("payment_terms_days", sa.Integer()),
            sa.Column("is_active", sa.Boolean()),
        ]),
        ("product_categories", [
            sa.Column("parent_id", sa.BigInteger()),
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("slug", sa.String(150), nullable=False),
            sa.Column("description", sa.Text()),
            sa.ForeignKeyConstraint(["parent_id"], ["product_categories.id"]),
        ]),
        ("warehouses", [
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("code", sa.String(20), nullable=False),
            sa.Column("is_default", sa.Boolean()),
        ]),
        ("ppe_categories", [
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("slug", sa.String(100), nullable=False),
            sa.Column("description", sa.Text()),
        ]),
    ]:
        cols = extra_cols + [
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("created_by", sa.BigInteger()),
            sa.Column("updated_by", sa.BigInteger()),
            sa.Column("is_deleted", sa.Boolean(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("uuid"),
        ]
        op.create_table(table_name, *cols)

    op.create_table(
        "employees",
        sa.Column("user_id", sa.BigInteger()),
        sa.Column("department_id", sa.BigInteger()),
        sa.Column("employee_number", sa.String(50), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(50)),
        sa.Column("job_title", sa.String(150)),
        sa.Column("hire_date", sa.Date()),
        sa.Column("status", sa.String(20)),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_number"),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_table(
        "client_contacts",
        sa.Column("client_id", sa.BigInteger(), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(50)),
        sa.Column("mobile", sa.String(50)),
        sa.Column("position", sa.String(100)),
        sa.Column("is_primary", sa.Boolean()),
        sa.Column("is_billing_contact", sa.Boolean()),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_table(
        "client_addresses",
        sa.Column("client_id", sa.BigInteger(), nullable=False),
        sa.Column("address_type", sa.String(20)),
        sa.Column("line1", sa.String(255), nullable=False),
        sa.Column("line2", sa.String(255)),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("province", sa.String(100)),
        sa.Column("postal_code", sa.String(20)),
        sa.Column("country", sa.String(2)),
        sa.Column("is_default", sa.Boolean()),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_table(
        "products",
        sa.Column("category_id", sa.BigInteger()),
        sa.Column("supplier_id", sa.BigInteger()),
        sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("barcode", sa.String(100)),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("purchase_price", sa.Numeric(15, 2)),
        sa.Column("selling_price", sa.Numeric(15, 2)),
        sa.Column("min_stock_level", sa.Integer()),
        sa.Column("unit_of_measure", sa.String(20)),
        sa.Column("is_active", sa.Boolean()),
        sa.Column("track_serial", sa.Boolean()),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["product_categories.id"]),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_table(
        "warehouse_stock",
        sa.Column("warehouse_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("quantity", sa.Integer()),
        sa.Column("reserved_quantity", sa.Integer()),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("warehouse_id", "product_id", name="uq_warehouse_product"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_table(
        "ppe_items",
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger()),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("size", sa.String(50)),
        sa.Column("standard", sa.String(100)),
        sa.Column("replacement_interval_days", sa.Integer()),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(20)),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["ppe_categories.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_table(
        "ppe_employee_issues",
        sa.Column("employee_id", sa.BigInteger(), nullable=False),
        sa.Column("ppe_item_id", sa.BigInteger(), nullable=False),
        sa.Column("issued_date", sa.Date(), nullable=False),
        sa.Column("replacement_due_date", sa.Date()),
        sa.Column("quantity", sa.Integer()),
        sa.Column("condition", sa.String(20)),
        sa.Column("status", sa.String(20)),
        sa.Column("notes", sa.Text()),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ppe_item_id"], ["ppe_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )

    op.create_table(
        "ppe_inspections",
        sa.Column("issue_id", sa.BigInteger(), nullable=False),
        sa.Column("inspection_date", sa.Date(), nullable=False),
        sa.Column("result", sa.String(20), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("inspector_id", sa.BigInteger()),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["inspector_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["issue_id"], ["ppe_employee_issues.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )


def downgrade() -> None:
    for table in [
        "ppe_inspections", "ppe_employee_issues", "ppe_items", "warehouse_stock",
        "products", "client_addresses", "client_contacts", "employees",
        "ppe_categories", "warehouses", "product_categories", "suppliers",
        "clients", "departments", "audit_logs", "login_history", "refresh_tokens",
        "user_roles", "users", "role_permissions", "permissions", "roles", "company_settings",
    ]:
        op.drop_table(table)
