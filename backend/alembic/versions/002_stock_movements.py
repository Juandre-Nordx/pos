"""Add immutable inventory movement history.

Revision ID: 002
Revises: 001
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stock_movements",
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("warehouse_id", sa.BigInteger(), nullable=False),
        sa.Column("movement_type", sa.String(30), nullable=False),
        sa.Column("quantity_before", sa.Integer(), nullable=False),
        sa.Column("quantity_changed", sa.Integer(), nullable=False),
        sa.Column("quantity_after", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("reference", sa.String(100)),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_by", sa.BigInteger()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index("ix_stock_movements_product_id", "stock_movements", ["product_id"])
    op.create_index("ix_stock_movements_warehouse_id", "stock_movements", ["warehouse_id"])
    op.create_index("ix_stock_movements_movement_type", "stock_movements", ["movement_type"])
    op.create_index("ix_stock_movements_uuid", "stock_movements", ["uuid"])
    op.create_index("ix_stock_movements_is_deleted", "stock_movements", ["is_deleted"])


def downgrade() -> None:
    op.drop_table("stock_movements")
