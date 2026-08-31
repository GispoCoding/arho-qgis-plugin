from __future__ import annotations

import enum
import json
import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, NotRequired, TypedDict

import psycopg
from alembic import command
from alembic.config import Config
from alembic.util.exc import CommandError
from psycopg.sql import SQL, Identifier, Literal

from database.db_helper import DbUser, get_connection_parameters, get_user_credentials

if TYPE_CHECKING:
    from collections.abc import Generator

"""
Hame-ryhti database manager, adapted from Tarmo db_manager.
"""

LOGGER = logging.getLogger()


class Action(enum.Enum):
    CREATE_DB = "create_db"
    MIGRATE_DB = "migrate_db"


class Response(TypedDict):
    statusCode: int
    body: str


class Event(TypedDict):
    action: str  # EventType
    version: NotRequired[str | None]  # Alembic revision id


dba_user_credentials = get_user_credentials(DbUser.DBA)
su_user_credentials = get_user_credentials(DbUser.SU)


def database_exists(conn: psycopg.Connection, db_name: str) -> bool:
    return (
        conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
        ).fetchone()
        is not None
    )


def create_dba_user_if_not_exists(conn: psycopg.Connection) -> None:
    if (
        conn.execute(
            SQL("SELECT 1 FROM pg_roles WHERE rolname = {username}").format(
                username=Literal(dba_user_credentials["username"])
            )
        ).fetchone()
        is not None
    ):
        LOGGER.info("DBA user already exists.")
        return

    conn.execute(
        SQL(
            "CREATE ROLE {username} WITH CREATEROLE LOGIN ENCRYPTED PASSWORD {password}"
        ).format(
            username=Identifier(dba_user_credentials["username"]),
            password=Literal(dba_user_credentials["password"]),
        )
    )
    conn.commit()
    LOGGER.info("Created DBA user.")


def grant_dba_role_to_su_user(conn: psycopg.Connection) -> None:
    """Allow the SU user to SET ROLE to the DBA user.

    Since PostgreSQL 16, a CREATEROLE user that creates a role gets the role
    back with SET FALSE, and CREATE DATABASE ... OWNER requires being able to
    SET ROLE to the owner. The SU user holds ADMIN OPTION on the DBA user it
    created, so it may grant itself the SET option.

    This runs on every setup, both to cover databases where the DBA user was
    created without the SET option and because re-granting is a no-op.
    """
    conn.execute(
        SQL("GRANT {dba_user} TO CURRENT_USER WITH SET TRUE").format(
            dba_user=Identifier(dba_user_credentials["username"])
        )
    )
    conn.commit()
    LOGGER.info("Granted the DBA role to the SU user.")


@contextmanager
def as_dba_user(conn: psycopg.Connection) -> Generator[None]:
    """Run statements as the DBA user, which owns the main database.

    The SU user owns neither the main database nor its public schema, so it
    cannot grant or revoke privileges on them on its own. Note that a REVOKE
    by a non-owner only warns instead of failing, so without this the
    statements would silently do nothing.
    """
    conn.execute(
        SQL("SET ROLE {dba_user}").format(
            dba_user=Identifier(dba_user_credentials["username"])
        )
    )
    try:
        yield
    finally:
        conn.execute(SQL("RESET ROLE"))


def create_db_if_not_exists(conn: psycopg.Connection, db_name: str) -> None:
    """Creates empty db."""
    if database_exists(conn, db_name):
        msg = "Database already exists."
        LOGGER.info(msg)
        return

    conn.commit()  # Ensure no transaction is active
    original_autocommit = conn.autocommit
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(
            SQL("CREATE DATABASE {db_name} OWNER {dba_user}").format(
                db_name=Identifier(db_name),
                dba_user=Identifier(dba_user_credentials["username"]),
            )
        )
    conn.autocommit = original_autocommit
    LOGGER.info("Created empty database.")


def configure_db_permissions(conn: psycopg.Connection) -> None:
    """Revoke public access to the databases and hand the public schema to the DBA.

    The maintenance database is owned by the SU user, but the main database and
    its public schema are owned by the DBA user, so the two need different roles.
    """
    conn.execute(
        SQL("REVOKE ALL ON DATABASE {db_name} FROM PUBLIC").format(
            db_name=Identifier(os.environ["DB_MAINTENANCE_NAME"])
        )
    )
    with as_dba_user(conn):
        conn.execute(
            SQL("REVOKE ALL ON DATABASE {db_name} FROM PUBLIC").format(
                db_name=Identifier(os.environ["DB_MAIN_NAME"])
            )
        )
        conn.execute(SQL("REVOKE CREATE ON SCHEMA public FROM PUBLIC"))
        conn.execute(
            SQL("GRANT ALL ON SCHEMA public TO {dba_user}").format(
                dba_user=Identifier(dba_user_credentials["username"])
            )
        )
    conn.commit()
    LOGGER.info("Configured database permissions.")


def install_postgis_extension(conn: psycopg.Connection) -> None:
    """Install the PostGIS extension to the given database connection.

    PostGIS is not a trusted extension, so on RDS only the SU user, which is a
    member of rds_superuser, may create it. The SU user does not own the public
    schema, so it is given CREATE on it for the duration of the install only.
    """
    su_user = Identifier(su_user_credentials["username"])
    with as_dba_user(conn):
        conn.execute(
            SQL("GRANT CREATE ON SCHEMA public TO {su_user}").format(su_user=su_user)
        )
    conn.commit()
    try:
        conn.execute(SQL("CREATE EXTENSION IF NOT EXISTS postgis"))
        conn.commit()
    finally:
        conn.rollback()  # A failed install leaves the transaction aborted
        with as_dba_user(conn):
            conn.execute(
                SQL("REVOKE CREATE ON SCHEMA public FROM {su_user}").format(
                    su_user=su_user
                )
            )
        conn.commit()
    LOGGER.info("Installed PostGIS extension.")


def migrate_db(version: str = "head") -> str:
    connection_params = get_connection_parameters(
        dba_user_credentials, os.environ["DB_MAIN_NAME"]
    )
    alembic_cfg = Config(Path("alembic.ini"))
    alembic_cfg.attributes["connection_parameters"] = connection_params

    LOGGER.info("Migrating db to version '%s'", version)
    # Go figure. Alembic API has no way of checking if a version is up
    # or down from current version. We have to figure it out by trying
    try:
        command.downgrade(alembic_cfg, version)
        msg = f"Database downgraded to version {version}."
        LOGGER.info("Downgrade successful.")
    except CommandError:
        command.upgrade(alembic_cfg, version)
        msg = f"Database upgraded to or already at version {version}."
        LOGGER.info("Upgrade successful.")

    return msg


def setup_db() -> None:
    """Set up the database by creating the dba user and the database."""
    maintenance_db_name = os.environ["DB_MAINTENANCE_NAME"]
    main_db_name = os.environ["DB_MAIN_NAME"]

    # Connect to maintenance db to create DBA user and main db
    with psycopg.connect(
        **get_connection_parameters(su_user_credentials, maintenance_db_name)
    ) as su_connection_to_maintenance_db:
        create_dba_user_if_not_exists(su_connection_to_maintenance_db)
        grant_dba_role_to_su_user(su_connection_to_maintenance_db)
        create_db_if_not_exists(su_connection_to_maintenance_db, main_db_name)

    # Connect to main db to install PostGIS and configure permissions
    with psycopg.connect(
        **get_connection_parameters(su_user_credentials, main_db_name)
    ) as su_connection_to_main_db:
        install_postgis_extension(su_connection_to_main_db)
        configure_db_permissions(su_connection_to_main_db)


def handler(event: Event, _) -> Response:
    """Handler which is called when accessing the endpoint."""
    # if the code fails before returning response, aws lambda will return http 500
    # with the exception stack trace, as desired.
    response = Response(statusCode=200, body=json.dumps(""))
    LOGGER.info(f"Got an event {event}")
    try:
        event_type = Action(event["action"])
    except ValueError:
        return Response(statusCode=400, body=f"Unknown action {event['action']}.")
    except KeyError:
        return Response(statusCode=400, body="Action not defined.")

    msg = None
    if event_type is Action.CREATE_DB:
        setup_db()
        msg = "Database setup completed."
    elif event_type is Action.MIGRATE_DB:
        # Make sure DB is up to date
        setup_db()
        version = str(event.get("version", "head"))
        msg = migrate_db(version)
    response["body"] = msg or ""
    return response
