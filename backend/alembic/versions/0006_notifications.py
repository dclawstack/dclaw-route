"""add notification templates + events; customer contact on stops

Revision ID: 0006_notifications
Revises: 0005_vehicles
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "0006_notifications"
down_revision = "0005_vehicles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("stops", sa.Column("customer_email", sa.String(200), nullable=True))
    op.add_column("stops", sa.Column("customer_phone", sa.String(50), nullable=True))

    op.create_table(
        "notification_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("kind", sa.String(50), nullable=False, unique=True),
        sa.Column("subject", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "notification_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "delivery_id",
            UUID(as_uuid=True),
            sa.ForeignKey("deliveries.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("kind", sa.String(50), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("recipient", sa.String(200), nullable=False),
        sa.Column("subject", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("sent_at", sa.DateTime, nullable=False),
    )
    op.create_index(
        "ix_notification_events_delivery_id", "notification_events", ["delivery_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notification_events_delivery_id", table_name="notification_events"
    )
    op.drop_table("notification_events")
    op.drop_table("notification_templates")
    op.drop_column("stops", "customer_phone")
    op.drop_column("stops", "customer_email")
