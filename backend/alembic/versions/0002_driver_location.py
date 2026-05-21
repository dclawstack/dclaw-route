"""add driver location columns

Revision ID: 0002_driver_location
Revises: 0001_initial
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_driver_location"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("drivers", sa.Column("current_lat", sa.Float, nullable=True))
    op.add_column("drivers", sa.Column("current_lng", sa.Float, nullable=True))
    op.add_column("drivers", sa.Column("location_updated_at", sa.DateTime, nullable=True))


def downgrade() -> None:
    op.drop_column("drivers", "location_updated_at")
    op.drop_column("drivers", "current_lng")
    op.drop_column("drivers", "current_lat")
