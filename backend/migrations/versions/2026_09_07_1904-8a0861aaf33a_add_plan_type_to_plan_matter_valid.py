"""add_plan_type_to_plan_matter_valid

Revision ID: 8a0861aaf33a
Revises: fda6e087970a
Create Date: 2026-09-07 19:04:08.076591

"""

from collections.abc import Sequence

from alembic import op
from alembic_utils.pg_view import PGView

# revision identifiers, used by Alembic.
revision: str = "8a0861aaf33a"
down_revision: str | None = "fda6e087970a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The plan_type column is appended after the existing columns, so
# CREATE OR REPLACE VIEW works and the grants on the view survive.
NEW_PLAN_MATTER_VALID_DEFINITION = 'with recursive plan_type_root as (\n    select id, id root_id\n    from codes.plan_type\n    where level = 1\n  union all\n    select child.id, r.root_id\n    from plan_type_root r\n    join codes.plan_type child on child.parent_id = r.id\n)\nselect\n    m.name,\n    m.description,\n    m.permanent_plan_identifier,\n    m.producers_plan_identifier,\n    m.case_identifier,\n    m.record_number,\n    m.digital_origin_id,\n    m.plan_type_id,\n    m.organisation_id,\n    m.id,\n    m.creator,\n    m.created_at,\n    m.modified_at,\n    m.modifier,\n    root.value plan_type\nfrom\n    hame.plan_matter m\n    left join plan_type_root ptr on ptr.id = m.plan_type_id\n    left join codes.plan_type root on root.id = ptr.root_id\nwhere\n    exists (select 1 from hame.plan_valid p\n        where p.plan_matter_id = m.id)'

OLD_PLAN_MATTER_VALID_DEFINITION = 'select\n    m.name,\n    m.description,\n    m.permanent_plan_identifier,\n    m.producers_plan_identifier,\n    m.case_identifier,\n    m.record_number,\n    m.digital_origin_id,\n    m.plan_type_id,\n    m.organisation_id,\n    m.id,\n    m.creator,\n    m.created_at,\n    m.modified_at,\n    m.modifier\nfrom\n    hame.plan_matter m\nwhere\n    exists (select 1 from hame.plan_valid p\n        where p.plan_matter_id = m.id)'


def grant_select() -> None:
    """Re-grant select on the view.

    CREATE OR REPLACE VIEW keeps the grants, but alembic_utils falls back to
    DROP VIEW + CREATE VIEW whenever it fails, and dropping the view drops the
    grants with it. The downgrade removes a column, which CREATE OR REPLACE
    VIEW cannot do, so it always takes that fallback.
    """
    op.execute("GRANT SELECT ON hame.plan_matter_valid TO arho_read_only;")
    op.execute("GRANT SELECT ON hame.plan_matter_valid TO arho_read_write;")


def upgrade() -> None:
    op.replace_entity(
        PGView(
            schema="hame",
            signature="plan_matter_valid",
            definition=NEW_PLAN_MATTER_VALID_DEFINITION,
        )
    )
    grant_select()


def downgrade() -> None:
    op.replace_entity(
        PGView(
            schema="hame",
            signature="plan_matter_valid",
            definition=OLD_PLAN_MATTER_VALID_DEFINITION,
        )
    )
    grant_select()
