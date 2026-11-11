"""grant table privileges

Revision ID: 437ffa34d4d2
Revises: 33ae892587da
Create Date: 2026-01-12 00:04:08.539750

"""

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "437ffa34d4d2"
down_revision: str | None = "33ae892587da"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

tables = [
  "additional_information",
  "document",
  "event_date",
  "land_use_area",
  "land_use_area_v",
  "legal_effects_association",
  "lifecycle_date",
  "line",
  "line_v",
  "organisation",
  "other_area",
  "other_area_v",
  "plan",
  "plan_matter",
  "plan_proposition",
  "plan_regulation",
  "plan_regulation_group",
  "plan_theme_association",
  "point",
  "point_v",
  "regulation_group_association",
  "source_data",
  "type_of_verbal_regulation_association",
]

arho_tables_need_admin_delete = {
  "plan", "plan_matter"
}

code_tables = [
  "administrative_region",
  "allowed_events",
  "category_of_publicity",
  "language",
  "legal_effects_of_master_plan",
  "lifecycle_status",
  "municipality",
  "name_of_plan_case_decision",
  "personal_data_content",
  "plan_theme",
  "plan_type",
  "retention_time",
  "type_of_additional_information",
  "type_of_decision_maker",
  "type_of_document",
  "type_of_interaction_event",
  "type_of_plan_regulation",
  "type_of_plan_regulation_group",
  "type_of_processing_event",
  "type_of_source_data",
  "type_of_underground",
  "type_of_verbal_plan_regulation",
]

def upgrade() -> None:
    for table in tables:
        op.execute(f"GRANT SELECT ON hame.{table} TO arho_read_only;")
        op.execute(f"GRANT SELECT, INSERT, UPDATE ON hame.{table} TO arho_read_write;")
        if table in arho_tables_need_admin_delete:
            op.execute(f"GRANT DELETE ON hame.{table} TO arho_admin;")
        else:
            op.execute(f"GRANT DELETE ON hame.{table} TO arho_read_write;")

    for table in code_tables:
        op.execute(f"GRANT SELECT ON codes.{table} TO arho_read_only, arho_read_write;")

def downgrade() -> None:
    for table in tables:
        op.execute(f"REVOKE SELECT ON hame.{table} FROM arho_read_only;")
        op.execute(f"REVOKE SELECT, INSERT, UPDATE ON hame.{table} FROM arho_read_write;")
        if table in arho_tables_need_admin_delete:
            op.execute(f"REVOKE DELETE ON hame.{table} FROM arho_admin;")
        else:
          op.execute(f"REVOKE DELETE ON hame.{table} FROM arho_read_write;")

    for table in code_tables:
        op.execute(f"REVOKE SELECT ON codes.{table} FROM arho_read_only, arho_read_write;")
