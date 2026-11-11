"""add jobs table

Revision ID: 83fe73894789
Revises: 5d2c9b7e4a11
Create Date: 2026-10-12 11:51:41.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "83fe73894789"
down_revision: str | None = "5d2c9b7e4a11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Alembic does not create schemas. The QGIS roles get no grants on the
    # schema or the table: only the ryhti_client lambda uses them.
    op.execute("CREATE SCHEMA IF NOT EXISTS jobs")
    op.create_table(
        "job",
        sa.Column(
            "id",
            sa.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("plan_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column(
            "request", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column(
            "status",
            sa.Enum(
                "queued", "running", "done", "failed", name="jobstatus", schema="jobs"
            ),
            nullable=False,
        ),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("finished_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="jobs",
    )


def downgrade() -> None:
    op.drop_table("job", schema="jobs")
    op.execute("DROP TYPE jobs.jobstatus")
    op.execute("DROP SCHEMA IF EXISTS jobs")
