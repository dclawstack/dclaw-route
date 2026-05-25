"""add routes.dock_number for WMS dock assignment

Revision ID: 0009_route_dock
Revises: 0008_territories
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa


revision = "0009_route_dock"
down_revision = "0008_territories"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("routes", sa.Column("dock_number", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("routes", "dock_number")
