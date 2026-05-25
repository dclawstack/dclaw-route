"""add autonomous_vehicles table

Revision ID: 0011_autonomous_vehicles
Revises: 0010_gig_drivers
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "0011_autonomous_vehicles"
down_revision = "0010_gig_drivers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "autonomous_vehicles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("vendor", sa.String(100), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("autopilot_level", sa.Integer, nullable=False),
        sa.Column("capacity_kg", sa.Float, nullable=False),
        sa.Column("current_lat", sa.Float, nullable=True),
        sa.Column("current_lng", sa.Float, nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "current_route_id",
            UUID(as_uuid=True),
            sa.ForeignKey("routes.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("autonomous_vehicles")
