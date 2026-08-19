"""add cancel requested fields to jobs

Revision ID: ee8f2297969d
Revises: 9e753afdce70
Create Date: 2026-08-20 04:50:01.857667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee8f2297969d'
down_revision: Union[str, Sequence[str], None] = '9e753afdce70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # server_default backfills existing rows to "not requested" (same
    # reasoning as 9e753afdce70's failed_login_attempts column) — the
    # ORM model's Python-side default=False only applies to new rows
    # created after this migration runs.
    op.add_column(
        "jobs",
        sa.Column(
            "cancel_requested", sa.Boolean(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "jobs", sa.Column("cancel_requested_at", sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("jobs", "cancel_requested_at")
    op.drop_column("jobs", "cancel_requested")
