"""add vehicles table and routes.vehicle_id

Revision ID: 0005_vehicles
Revises: 0004_driver_shifts
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "0005_vehicles"
down_revision = "0004_driver_shifts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("plate", sa.String(20), nullable=False, unique=True),
        sa.Column("vehicle_type", sa.String(50), nullable=False),
        sa.Column("capacity_kg", sa.Float, nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("odometer_km", sa.Integer, nullable=False),
        sa.Column("last_service_odometer_km", sa.Integer, nullable=False),
        sa.Column("last_service_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.add_column(
        "routes",
        sa.Column(
            "vehicle_id",
            UUID(as_uuid=True),
            sa.ForeignKey("vehicles.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("routes", "vehicle_id")
    op.drop_table("vehicles")
