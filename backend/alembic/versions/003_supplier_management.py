"""Expand supplier records and add supplier contacts.

Revision ID: 003
Revises: 002
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = [
        sa.Column("code", sa.String(50)), sa.Column("contact_person", sa.String(255)),
        sa.Column("alternative_phone", sa.String(50)), sa.Column("website", sa.String(500)),
        sa.Column("physical_address", sa.Text()), sa.Column("billing_address", sa.Text()),
        sa.Column("city", sa.String(100)), sa.Column("province", sa.String(100)),
        sa.Column("postal_code", sa.String(20)), sa.Column("country", sa.String(100)),
        sa.Column("registration_number", sa.String(100)),
        sa.Column("credit_limit", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("account_balance", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("bank_details", postgresql.JSONB()),
        sa.Column("lead_time_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("minimum_order_amount", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("delivery_terms", sa.Text()),
        sa.Column("product_categories", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("notes", sa.Text()),
    ]
    for column in columns:
        op.add_column("suppliers", column)
    # Preserve existing suppliers while assigning stable, unique codes before
    # enforcing the new business constraint.
    op.execute("UPDATE suppliers SET code = 'SUP-' || id::text WHERE code IS NULL")
    op.alter_column("suppliers", "code", nullable=False)
    op.create_unique_constraint("uq_suppliers_code", "suppliers", ["code"])
    op.create_index("ix_suppliers_code", "suppliers", ["code"])
    op.create_index("ix_suppliers_name", "suppliers", ["name"])

    op.create_table(
        "supplier_contacts",
        sa.Column("supplier_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("job_title", sa.String(150)), sa.Column("department", sa.String(150)),
        sa.Column("email", sa.String(255)), sa.Column("phone", sa.String(50)),
        sa.Column("alternative_phone", sa.String(50)),
        sa.Column("preferred_contact_method", sa.String(20), nullable=False, server_default="email"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("notes", sa.Text()), sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.BigInteger()), sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="CASCADE"),
    )
    for column in ("supplier_id", "full_name", "email", "phone", "uuid", "is_deleted"):
        op.create_index(f"ix_supplier_contacts_{column}", "supplier_contacts", [column])
    op.create_index("uq_supplier_primary_contact", "supplier_contacts", ["supplier_id"],
                    unique=True, postgresql_where=sa.text("is_primary AND NOT is_deleted"))
    op.execute("""
        INSERT INTO permissions (module, action, description, uuid, is_deleted)
        SELECT 'suppliers', action, description,
               md5('suppliers:' || action)::uuid, false
        FROM (VALUES
            ('read', 'View suppliers'), ('create', 'Create suppliers'),
            ('update', 'Edit and deactivate suppliers'),
            ('financial', 'View supplier financial information')
        ) AS requested(action, description)
        ON CONFLICT (module, action) DO NOTHING
    """)
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT roles.id, permissions.id
        FROM roles CROSS JOIN permissions
        WHERE roles.slug IN ('director', 'manager')
          AND permissions.module = 'suppliers'
        ON CONFLICT DO NOTHING
    """)
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT roles.id, permissions.id
        FROM roles CROSS JOIN permissions
        WHERE roles.slug = 'store' AND permissions.module = 'suppliers'
          AND permissions.action = 'read'
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM role_permissions WHERE permission_id IN
        (SELECT id FROM permissions WHERE module = 'suppliers')
    """)
    op.execute("DELETE FROM permissions WHERE module = 'suppliers'")
    op.drop_table("supplier_contacts")
    op.drop_constraint("uq_suppliers_code", "suppliers", type_="unique")
    for name in ["code", "contact_person", "alternative_phone", "website", "physical_address",
                 "billing_address", "city", "province", "postal_code", "country",
                 "registration_number", "credit_limit", "account_balance", "bank_details",
                 "lead_time_days", "minimum_order_amount", "delivery_terms", "product_categories", "notes"]:
        op.drop_column("suppliers", name)
