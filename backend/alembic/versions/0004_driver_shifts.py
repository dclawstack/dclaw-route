"""add driver_shifts table

Revision ID: 0004_driver_shifts
Revises: 0003_delivery_proof
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "0004_driver_shifts"
down_revision = "0003_delivery_proof"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "driver_shifts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "driver_id",
            UUID(as_uuid=True),
            sa.ForeignKey("drivers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_at", sa.DateTime, nullable=False),
        sa.Column("end_at", sa.DateTime, nullable=True),
        sa.Column("hours_worked", sa.Float, nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_driver_shifts_driver_id", "driver_shifts", ["driver_id"])


def downgrade() -> None:
    op.drop_index("ix_driver_shifts_driver_id", table_name="driver_shifts")
    op.drop_table("driver_shifts")
