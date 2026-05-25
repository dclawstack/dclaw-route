"""add gig_drivers table

Revision ID: 0010_gig_drivers
Revises: 0009_route_dock
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "0010_gig_drivers"
down_revision = "0009_route_dock"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gig_drivers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("rating", sa.Float, nullable=False),
        sa.Column("vehicle_type", sa.String(50), nullable=False),
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
    op.drop_table("gig_drivers")
