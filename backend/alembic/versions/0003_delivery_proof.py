"""add proof-of-delivery columns

Revision ID: 0003_delivery_proof
Revises: 0002_driver_location
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_delivery_proof"
down_revision = "0002_driver_location"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("deliveries", sa.Column("photo_b64", sa.Text, nullable=True))
    op.add_column("deliveries", sa.Column("signature_b64", sa.Text, nullable=True))
    op.add_column("deliveries", sa.Column("barcode", sa.String(200), nullable=True))
    op.add_column("deliveries", sa.Column("geotag_lat", sa.Float, nullable=True))
    op.add_column("deliveries", sa.Column("geotag_lng", sa.Float, nullable=True))
    op.add_column("deliveries", sa.Column("photo_validated", sa.Boolean, nullable=True))


def downgrade() -> None:
    op.drop_column("deliveries", "photo_validated")
    op.drop_column("deliveries", "geotag_lng")
    op.drop_column("deliveries", "geotag_lat")
    op.drop_column("deliveries", "barcode")
    op.drop_column("deliveries", "signature_b64")
    op.drop_column("deliveries", "photo_b64")
