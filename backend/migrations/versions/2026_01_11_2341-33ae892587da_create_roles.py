"""create roles

Revision ID: 33ae892587da
Revises: f73abbd8c732
Create Date: 2026-01-11 23:41:59.461894

"""

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "33ae892587da"
down_revision: str | None = "f73abbd8c732"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    current_database = op.get_bind().engine.url.database

    op.execute("CREATE ROLE arho_read_write")
    op.execute(f'GRANT CONNECT ON DATABASE "{current_database}" TO arho_read_write')
    op.execute(f"GRANT USAGE ON SCHEMA hame, codes TO arho_read_write")

    op.execute("CREATE ROLE arho_read_only")
    op.execute(f'GRANT CONNECT ON DATABASE "{current_database}" TO arho_read_only')
    op.execute(f"GRANT USAGE ON SCHEMA hame, codes TO arho_read_only")

    op.execute("CREATE ROLE arho_admin WITH CREATEROLE")
    op.execute(f'GRANT CONNECT ON DATABASE "{current_database}" TO arho_admin')
    op.execute(f"GRANT arho_read_write TO arho_admin WITH ADMIN OPTION")
    op.execute(f"GRANT arho_read_only TO arho_admin WITH ADMIN OPTION")

def downgrade() -> None:
    for role in ("arho_admin", "arho_read_only", "arho_read_write"):
        op.execute(f"REASSIGN OWNED BY {role} TO arho_dba") # Reassign objects owned by the role
        op.execute(f"DROP OWNED BY {role}") # Remove privileges granted to the role which is needed before dropping the role
        op.execute(f"DROP ROLE {role}")

