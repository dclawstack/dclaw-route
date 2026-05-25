"""add deliveries.kind for drop-off vs pickup (returns)

Revision ID: 0007_delivery_kind
Revises: 0006_notifications
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa


revision = "0007_delivery_kind"
down_revision = "0006_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "deliveries",
        sa.Column("kind", sa.String(20), nullable=False, server_default="drop_off"),
    )
    op.alter_column("deliveries", "kind", server_default=None)


def downgrade() -> None:
    op.drop_column("deliveries", "kind")
