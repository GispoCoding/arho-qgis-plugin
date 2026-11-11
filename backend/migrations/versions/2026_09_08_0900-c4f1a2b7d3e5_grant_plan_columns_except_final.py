"""grant plan columns except final

Revision ID: c4f1a2b7d3e5
Revises: 170cfb70d842
Create Date: 2026-09-08 09:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4f1a2b7d3e5"
down_revision: str | None = "170cfb70d842"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Every column of hame.plan apart from final. PostgreSQL cannot revoke a single
# column from a table wide update grant, so the grant is given column by column
# instead. A column added later has to be added here by its own migration; the
# test test_read_write_role_privileges_on_plan_columns in test/test_db.py fails
# until it is.
UPDATABLE_PLAN_COLUMNS = (
    "plan_matter_id",
    "name",
    "description",
    "scale",
    "official_use_only",
    "approval_date",
    "locked",
    "geom",
    "validated_at",
    "validation_errors",
    "exported_at",
    "id",
    "creator",
    "created_at",
    "modified_at",
    "modifier",
    "lifecycle_status_id",
    "period_of_validity_start",
    "period_of_validity_end",
)

COLUMN_LIST = ", ".join(UPDATABLE_PLAN_COLUMNS)


def upgrade() -> None:
    # The final column is set by the finalize_plan action of the ryhti_client
    # lambda, which connects as the owner of the table and is not bound by the
    # grants. Nobody else may publish a plan through the valid views.
    op.execute("REVOKE UPDATE ON hame.plan FROM arho_read_write;")
    op.execute(f"GRANT UPDATE ({COLUMN_LIST}) ON hame.plan TO arho_read_write;")


def downgrade() -> None:
    op.execute(f"REVOKE UPDATE ({COLUMN_LIST}) ON hame.plan FROM arho_read_write;")
    op.execute("GRANT UPDATE ON hame.plan TO arho_read_write;")
