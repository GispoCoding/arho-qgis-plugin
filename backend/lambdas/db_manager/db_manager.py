import enum
import json
import logging
from pathlib import Path
from typing import Optional, TypedDict

import psycopg2
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.util.exc import CommandError
from db_helper import DatabaseHelper, Db, User
from psycopg2.sql import SQL, Identifier

"""
Hame-ryhti database manager, adapted from Tarmo db_manager.
"""

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


class Action(enum.Enum):
    CREATE_DB = "create_db"
    CHANGE_PWS = "change_pws"
    MIGRATE_DB = "migrate_db"


class Response(TypedDict):
    statusCode: int  # noqa N815
    body: str


class Event(TypedDict):
    action: str  # EventType
    version: Optional[str]  # Ansible version id


def create_db(conn: psycopg2.extensions.connection, db_name: str) -> str:
    """Creates empty db."""
    with conn.cursor() as cur:
        cur.execute(
            SQL("CREATE DATABASE {db_name};").format(db_name=Identifier(db_name))
        )
    msg = "Created empty database."
    LOGGER.info(msg)
    return msg


def configure_schemas_and_users(
    conn: psycopg2.extensions.connection, users: dict[User, dict]
) -> str:
    """
    Configures given database with hame schemas and users.
    """
    with conn.cursor() as cur:
        cur.execute(SQL("CREATE SCHEMA codes; CREATE SCHEMA hame;"))
        cur.execute(SQL("CREATE EXTENSION postgis WITH SCHEMA public;"))
        for key, user in users.items():
            if key == User.SU:
                # superuser exists already
                pass
            elif key == User.ADMIN:
                # To get the quotes right, username will have to be injected
                # using format, while password must be in vars.
                cur.execute(
                    SQL(
                        "CREATE ROLE {username} WITH CREATEROLE LOGIN ENCRYPTED PASSWORD %(password)s;"  # noqa
                    ).format(username=Identifier(user["username"])),
                    vars={"password": user["password"]},
                )
            else:
                # To get the quotes right, username will have to be injected
                # using format, while password must be in vars.
                cur.execute(
                    SQL(
                        "CREATE ROLE {username} WITH LOGIN ENCRYPTED PASSWORD %(password)s;"  # noqa
                    ).format(username=Identifier(user["username"])),
                    vars={"password": user["password"]},
                )
    msg = "Added hame schemas and users."
    return msg


def configure_permissions(
    conn: psycopg2.extensions.connection, users: dict[User, dict]
) -> str:
    """
    Configures user permissions.

    Can also be run on an existing database to fix user permissions to be up to date.
    """
    with conn.cursor() as cur:
        for key, user in users.items():
            if key == User.SU:
                # superuser already has the right permissions
                pass
            if key == User.ADMIN:
                # admin user should be able to edit all tables
                # (hame and code tables etc.)
                cur.execute(
                    SQL(
                        "ALTER DEFAULT PRIVILEGES FOR USER {SU_user} GRANT ALL PRIVILEGES ON TABLES TO {username};"  # noqa
                    ).format(
                        SU_user=Identifier(users[User.SU]["username"]),
                        username=Identifier(user["username"]),
                    )
                )
            elif key == User.READ_WRITE:
                # read and write user should be able to edit hame tables and
                # read code tables
                cur.execute(
                    SQL(
                        "ALTER DEFAULT PRIVILEGES FOR USER {SU_user} IN SCHEMA hame GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {username};"  # noqa
                    ).format(
                        SU_user=Identifier(users[User.SU]["username"]),
                        username=Identifier(user["username"]),
                    )
                )
                cur.execute(
                    SQL(
                        "ALTER DEFAULT PRIVILEGES FOR USER {SU_user} IN SCHEMA codes GRANT SELECT ON TABLES TO {username};"  # noqa
                    ).format(
                        SU_user=Identifier(users[User.SU]["username"]),
                        username=Identifier(user["username"]),
                    )
                )
            else:
                # default user should be able to read hame tables and code tables
                cur.execute(
                    SQL(
                        "ALTER DEFAULT PRIVILEGES FOR USER {SU_user} IN SCHEMA hame, codes GRANT SELECT ON TABLES TO {username};"  # noqa
                    ).format(
                        SU_user=Identifier(users[User.SU]["username"]),
                        username=Identifier(user["username"]),
                    )
                )
            # Finally, all users must have schema usage permissions
            cur.execute(
                SQL("GRANT USAGE ON SCHEMA hame to {username}").format(
                    username=Identifier(user["username"])
                )
            )
            cur.execute(
                SQL("GRANT USAGE ON SCHEMA codes to {username}").format(
                    username=Identifier(user["username"])
                )
            )
    msg = "Configured user permissions."
    return msg


def database_exists(conn: psycopg2.extensions.connection, db_name: str) -> bool:
    query = SQL("SELECT count(*) FROM pg_database WHERE datname = %(db_name)s")
    with conn.cursor() as cur:
        cur.execute(query, vars={"db_name": db_name})
        return cur.fetchone()[0] == 1


def migrate_hame_db(db_helper: DatabaseHelper, version: str = "head") -> str:
    """Migrates an existing db to the latest scheme, or provided version. Also
    configures database permissions.

    Can also be used to create the database up to any version.
    """
    root_conn = psycopg2.connect(
        **db_helper.get_connection_parameters(User.SU, Db.MAINTENANCE)
    )
    try:
        users = db_helper.get_users()
        root_conn.autocommit = True
        main_conn_params = db_helper.get_connection_parameters(User.SU, Db.MAIN)
        msg = ""

        # 1) check and create database and users
        main_db_exists = database_exists(root_conn, db_helper.get_db_name(Db.MAIN))
        if not main_db_exists:
            msg += create_db(root_conn, db_helper.get_db_name(Db.MAIN))
        main_conn = psycopg2.connect(**main_conn_params)
        main_conn.autocommit = True
        if not main_db_exists:
            msg += configure_schemas_and_users(main_conn, users)

        # 2) check and create permissions
        msg += configure_permissions(main_conn, users)

        # 3) check and upgrade database to correct version
        if main_db_exists:
            with main_conn.cursor() as cur:
                version_query = SQL("SELECT version_num FROM alembic_version")
                cur.execute(version_query)
                old_version = cur.fetchone()[0]
        else:
            old_version = None
        main_conn.close()

        alembic_cfg = Config(Path("alembic.ini"))
        alembic_cfg.attributes["connection"] = main_conn_params
        script_dir = ScriptDirectory.from_config(alembic_cfg)
        current_head_version = script_dir.get_current_head()
        print(current_head_version)

        if version == "head":
            version = current_head_version
        if old_version != version:
            # Go figure. Alembic API has no way of checking if a version is up
            # or down from current version. We have to figure it out by trying
            try:
                command.downgrade(alembic_cfg, version)
            except CommandError:
                command.upgrade(alembic_cfg, version)
            msg += "\n" + (
                f"Database was in version {old_version}.\n"
                f"Migrated the database to {version}."
            )
        else:
            msg += "\n" + (
                "Requested version is the same as current database "
                f"version {old_version}.\nNo migrations were run."
            )
    finally:
        root_conn.close()
    LOGGER.info(msg)
    return msg


def change_password(
    user: User, db_helper: DatabaseHelper, conn: psycopg2.extensions.connection
) -> None:
    username, pw = db_helper.get_username_and_password(user)
    with conn.cursor() as cur:
        sql = SQL("ALTER USER {user} WITH PASSWORD %(password)s").format(
            user=Identifier(username)
        )
        cur.execute(sql, vars={"password": pw})
    conn.commit()


def change_passwords(db_helper: DatabaseHelper) -> str:
    conn = psycopg2.connect(
        **db_helper.get_connection_parameters(User.SU, Db.MAINTENANCE)
    )
    try:
        change_password(User.ADMIN, db_helper, conn)
        change_password(User.READ, db_helper, conn)
        change_password(User.READ_WRITE, db_helper, conn)
    finally:
        conn.close()
    msg = "Changed passwords"
    LOGGER.info(msg)
    return msg


def handler(event: Event, _) -> Response:
    """Handler which is called when accessing the endpoint."""
    # if the code fails before returning response, aws lambda will return http 500
    # with the exception stack trace, as desired.
    response = Response(statusCode=200, body=json.dumps(""))
    db_helper = DatabaseHelper()
    try:
        event_type = Action(event["action"])
    except KeyError:
        event_type = Action.CREATE_DB
    except ValueError:
        return Response(
            statusCode=400,
            body=f"Unknown action {event['action']}.",
        )

    if event_type is Action.CREATE_DB:
        msg = migrate_hame_db(db_helper)
    elif event_type is Action.CHANGE_PWS:
        msg = change_passwords(db_helper)
    elif event_type is Action.MIGRATE_DB:
        version = str(event.get("version", ""))
        if version:
            msg = migrate_hame_db(db_helper, version)
        else:
            msg = migrate_hame_db(db_helper)
    response["body"] = json.dumps(msg)
    return response
