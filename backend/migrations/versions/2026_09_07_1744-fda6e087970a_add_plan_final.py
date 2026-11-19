"""add_plan_final

Revision ID: fda6e087970a
Revises: 82c89028a4d4
Create Date: 2026-09-07 17:44:43.211925

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from alembic_utils.pg_view import PGView

# revision identifiers, used by Alembic.
revision: str = "fda6e087970a"
down_revision: str | None = "82c89028a4d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Only the where clause of plan_valid changes; the column list stays the same,
# so CREATE OR REPLACE VIEW works and the dependent valid views and their
# grants survive untouched.
NEW_PLAN_VALID_DEFINITION = "select\n    p.plan_matter_id,\n    p.name,\n    p.description,\n    p.scale,\n    p.official_use_only,\n    p.approval_date,\n    p.locked,\n    p.geom,\n    p.validated_at,\n    p.validation_errors,\n    p.exported_at,\n    p.id,\n    p.creator,\n    p.created_at,\n    p.modified_at,\n    p.modifier,\n    p.lifecycle_status_id,\n    p.period_of_validity_start,\n    p.period_of_validity_end\nfrom\n    hame.plan p\n    join codes.lifecycle_status ls on ls.id = p.lifecycle_status_id\nwhere\n    p.final\n    and ls.value = '13'\n    and current_date between coalesce(p.period_of_validity_start, '-infinity'::date) and coalesce(p.period_of_validity_end, 'infinity'::date)"

OLD_PLAN_VALID_DEFINITION = "select\n    p.plan_matter_id,\n    p.name,\n    p.description,\n    p.scale,\n    p.official_use_only,\n    p.approval_date,\n    p.locked,\n    p.geom,\n    p.validated_at,\n    p.validation_errors,\n    p.exported_at,\n    p.id,\n    p.creator,\n    p.created_at,\n    p.modified_at,\n    p.modifier,\n    p.lifecycle_status_id,\n    p.period_of_validity_start,\n    p.period_of_validity_end\nfrom\n    hame.plan p\n    join codes.lifecycle_status ls on ls.id = p.lifecycle_status_id\nwhere\n    ls.value = '13'\n    and current_date between coalesce(p.period_of_validity_start, '-infinity'::date) and coalesce(p.period_of_validity_end, 'infinity'::date)"


def upgrade() -> None:
    op.add_column(
        "plan",
        sa.Column("final", sa.Boolean(), server_default="0", nullable=False),
        schema="hame",
    )
    op.replace_entity(
        PGView(
            schema="hame",
            signature="plan_valid",
            definition=NEW_PLAN_VALID_DEFINITION,
        )
    )


def downgrade() -> None:
    op.replace_entity(
        PGView(
            schema="hame",
            signature="plan_valid",
            definition=OLD_PLAN_VALID_DEFINITION,
        )
    )
    op.drop_column("plan", "final", schema="hame")
