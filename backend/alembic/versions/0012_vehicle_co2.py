"""add vehicles.co2_g_per_km

Revision ID: 0012_vehicle_co2
Revises: 0011_autonomous_vehicles
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa


revision = "0012_vehicle_co2"
down_revision = "0011_autonomous_vehicles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "vehicles",
        sa.Column("co2_g_per_km", sa.Float, nullable=False, server_default="250.0"),
    )
    op.alter_column("vehicles", "co2_g_per_km", server_default=None)


def downgrade() -> None:
    op.drop_column("vehicles", "co2_g_per_km")
