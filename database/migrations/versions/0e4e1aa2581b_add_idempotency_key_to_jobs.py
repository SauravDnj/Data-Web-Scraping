"""add idempotency key to jobs

Revision ID: 0e4e1aa2581b
Revises: bafe7b89931a
Create Date: 2026-08-20 01:05:53.891439

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e4e1aa2581b'
down_revision: Union[str, Sequence[str], None] = 'bafe7b89931a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    Uses batch mode (required for SQLite, which cannot ALTER a
    constraint directly — it needs the copy-and-move strategy batch
    mode provides; on MySQL this still emits plain ALTER statements,
    no behavior change there). Verified locally against SQLite:
    upgrade -> downgrade -> upgrade round-trips cleanly.
    """
    with op.batch_alter_table("jobs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("idempotency_key", sa.String(length=255), nullable=True))
        batch_op.create_unique_constraint(
            op.f("uq_jobs_idempotency_key"), ["idempotency_key"]
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("jobs", schema=None) as batch_op:
        batch_op.drop_constraint(op.f("uq_jobs_idempotency_key"), type_="unique")
        batch_op.drop_column("idempotency_key")
