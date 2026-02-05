"""Add PRs

Revision ID: 8157d6fa1693
Revises: 017a60cda09e
Create Date: 2026-01-29 17:34:25.830159

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "8157d6fa1693"
down_revision: Union[str, Sequence[str], None] = "017a60cda09e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add personal_record table and prtype enum."""

    # Create PRType enum
    prtype_enum = postgresql.ENUM(
        "MAX_VOLUME",
        "MAX_SINGLE_SET",
        "MAX_WEIGHT",
        "MAX_REPS",
        name="prtype",
        create_type=True,
    )
    prtype_enum.create(op.get_bind(), checkfirst=True)

    # Create personal_record table
    op.create_table(
        "personal_record",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("session_set_id", sa.Integer(), nullable=True),
        sa.Column(
            "pr_type",
            postgresql.ENUM(
                "MAX_VOLUME",
                "MAX_SINGLE_SET",
                "MAX_WEIGHT",
                "MAX_REPS",
                name="prtype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column(
            "achieved_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercise.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["session_id"], ["workout_session.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["session_set_id"], ["session_set.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for better query performance
    op.create_index(
        "idx_pr_user_exercise", "personal_record", ["user_id", "exercise_id"]
    )
    op.create_index(
        "idx_pr_user_exercise_type",
        "personal_record",
        ["user_id", "exercise_id", "pr_type"],
    )
    op.create_index("idx_pr_achieved_at", "personal_record", ["achieved_at"])


def downgrade() -> None:
    """Downgrade schema - remove personal_record table and prtype enum."""

    # Drop indexes
    op.drop_index("idx_pr_achieved_at", table_name="personal_record")
    op.drop_index("idx_pr_user_exercise_type", table_name="personal_record")
    op.drop_index("idx_pr_user_exercise", table_name="personal_record")

    # Drop table
    op.drop_table("personal_record")

    # Drop enum
    prtype_enum = postgresql.ENUM(name="prtype")
    prtype_enum.drop(op.get_bind(), checkfirst=True)
