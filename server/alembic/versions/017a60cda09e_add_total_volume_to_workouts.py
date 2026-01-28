"""Add total_volume to workouts

Revision ID: 017a60cda09e
Revises: 6fa58041c7e7
Create Date: 2026-01-28 15:44:49.877184
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "017a60cda09e"
down_revision = "6fa58041c7e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workout_session", sa.Column("total_volume", sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("workout_session", "total_volume")
