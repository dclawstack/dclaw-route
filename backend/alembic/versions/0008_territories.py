"""add territories table + stops.territory_id

Revision ID: 0008_territories
Revises: 0007_delivery_kind
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "0008_territories"
down_revision = "0007_delivery_kind"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "territories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("color", sa.String(7), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.add_column(
        "stops",
        sa.Column(
            "territory_id",
            UUID(as_uuid=True),
            sa.ForeignKey("territories.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("stops", "territory_id")
    op.drop_table("territories")
