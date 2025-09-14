from __future__ import annotations

import os
import sys
import time
import timeit
import uuid
from collections.abc import Callable, Generator, Mapping
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar
from zoneinfo import ZoneInfo

import psycopg
import pytest
import sqlalchemy
from alembic import command
from alembic.config import Config
from alembic.operations import ops
from alembic.script import Script, ScriptDirectory
from geoalchemy2.shape import from_shape
from shapely.geometry import MultiLineString, MultiPoint, shape
from sqlalchemy.orm import Session, sessionmaker

from database import codes, enums, models
from database.base import PROJECT_SRID
from database.db_helper import ConnectionParameters, DatabaseHelper, User
from database.enums import AttributeValueDataType
from lambdas.db_manager import db_manager

if TYPE_CHECKING:
    from pytest_docker.plugin import Services

# A little hack to make sure the ryhti_client package can be found during tests
sys.path.append("lambdas/ryhti_client")

hame_count: int = 19  # adjust me when adding tables
codes_count: int = 22  # adjust me when adding tables
matview_count: int = 0  # adjust me when adding views

USE_DOCKER = (
    "1"  # Use "" if you don't want pytest-docker to start and destroy the containers
)

LOCAL_TZ = ZoneInfo("Europe/Helsinki")


def pytest_addoption(parser, pluginmanager) -> None:
    parser.addoption(
        "--no-docker-mounts",
        action="store_true",
        default=False,
        help="Run tests without mounting dev files to containers.",
    )


@pytest.fixture(scope="session")
def root_db_params() -> ConnectionParameters:
    return {
        "dbname": os.environ.get("DB_MAINTENANCE_NAME", ""),
        "user": os.environ.get("SU_USER", ""),
        "host": os.environ.get("DB_INSTANCE_ADDRESS", ""),
        "password": os.environ.get("SU_USER_PW", ""),
        "port": os.environ.get("DB_INSTANCE_PORT", ""),
    }


@pytest.fixture(scope="session")
def main_db_params() -> ConnectionParameters:
    return {
        "dbname": os.environ.get("DB_MAIN_NAME", ""),
        "user": os.environ.get("RW_USER", ""),
        "host": os.environ.get("DB_INSTANCE_ADDRESS", ""),
        "password": os.environ.get("RW_USER_PW", ""),
        "port": os.environ.get("DB_INSTANCE_PORT", ""),
    }


@pytest.fixture(scope="session")
def main_db_params_with_root_user() -> ConnectionParameters:
    return {
        "dbname": os.environ.get("DB_MAIN_NAME", ""),
        "user": os.environ.get("SU_USER", ""),
        "host": os.environ.get("DB_INSTANCE_ADDRESS", ""),
        "password": os.environ.get("SU_USER_PW", ""),
        "port": os.environ.get("DB_INSTANCE_PORT", ""),
    }


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig: pytest.Config):
    compose_files = [Path(__file__).parent.parent / "docker-compose.dev.yml"]

    if pytestconfig.getoption("no_docker_mounts"):
        compose_files.append(
            Path(__file__).parent.parent / "docker-compose.clear-mounts.yml"
        )

    return [str(f) for f in compose_files]


if os.environ.get("MANAGE_DOCKER", USE_DOCKER):

    @pytest.fixture(scope="session", autouse=True)
    def wait_for_services(
        docker_services: Services,
        main_db_params: ConnectionParameters,
        root_db_params: ConnectionParameters,
    ) -> None:
        def is_responsive(params) -> bool:
            succeeds = False
            try:
                with psycopg.connect(**root_db_params):
                    succeeds = True
            except psycopg.OperationalError:
                pass
            return succeeds

        wait_until_responsive(
            timeout=20, pause=0.5, check=lambda: is_responsive(root_db_params)
        )
        drop_hame_db(main_db_params, root_db_params)

else:

    @pytest.fixture(scope="session", autouse=True)
    def wait_for_services(
        main_db_params: ConnectionParameters, root_db_params: ConnectionParameters
    ) -> None:
        wait_until_responsive(
            timeout=20, pause=0.5, check=lambda: is_responsive(root_db_params)
        )
        drop_hame_db(main_db_params, root_db_params)


@pytest.fixture(scope="session")
def alembic_cfg() -> Config:
    return Config(Path(__file__).parent.parent / "alembic.ini")


@pytest.fixture(scope="session")
def current_head_version_id(alembic_cfg: Config) -> str | None:
    script_dir = ScriptDirectory.from_config(alembic_cfg)
    return script_dir.get_current_head()


@pytest.fixture(scope="module")
def hame_database_created(
    root_db_params: ConnectionParameters,
    main_db_params: ConnectionParameters,
    current_head_version_id: str | None,
) -> Generator[str | None]:
    event: db_manager.Event = {"action": "create_db"}
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    yield current_head_version_id

    drop_hame_db(main_db_params, root_db_params)


@pytest.fixture
def hame_database_migrated(
    root_db_params: ConnectionParameters,
    main_db_params: ConnectionParameters,
    current_head_version_id: str | None,
):
    event: db_manager.Event = {"action": "migrate_db"}
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    yield current_head_version_id

    drop_hame_db(main_db_params, root_db_params)


@pytest.fixture
def hame_database_migrated_down(hame_database_migrated: str | None) -> str:
    event: db_manager.Event = {"action": "migrate_db", "version": "base"}
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    return "base"


def process_revision_directives_remove_empty(context, revision, directives) -> None:
    # remove migration if it is empty
    script = directives[0]
    if script.upgrade_ops.is_empty():
        directives[:] = []


def process_revision_directives_add_table(context, revision, directives) -> None:
    # try adding a new table
    directives[0] = ops.MigrationScript(
        "abcdef12345",
        ops.UpgradeOps(
            ops=[
                ops.CreateTableOp(
                    "test_table",
                    [
                        sqlalchemy.Column("id", sqlalchemy.Integer(), primary_key=True),
                        sqlalchemy.Column(
                            "name", sqlalchemy.String(50), nullable=False
                        ),
                    ],
                    schema="hame",
                )
            ]
        ),
        ops.DowngradeOps(ops=[ops.DropTableOp("test_table", schema="hame")]),
    )


@pytest.fixture
def autogenerated_migration(
    alembic_cfg: Config,
    hame_database_migrated: str | None,
    current_head_version_id: str | None,
):
    if current_head_version_id is None:
        raise Exception("Current head version id is None")

    revision = command.revision(
        alembic_cfg,
        message="Test migration",
        head=current_head_version_id,
        autogenerate=True,
        process_revision_directives=process_revision_directives_remove_empty,
    )

    if revision:
        assert isinstance(revision, Script), "Alembic created more than one revision"
        path = Path(revision.path)
    else:
        path = None
    yield path
    if path:
        path.unlink()


@pytest.fixture
def new_migration(
    alembic_cfg: Config,
    hame_database_migrated: str | None,
    current_head_version_id: str | None,
):
    if current_head_version_id is None:
        raise Exception("Current head version id is None")

    revision = command.revision(
        alembic_cfg,
        message="Test migration",
        head=current_head_version_id,
        autogenerate=True,
        process_revision_directives=process_revision_directives_add_table,
    )
    assert isinstance(revision, Script), "Alembic created no or more than one revision"
    path = Path(revision.path)
    assert path.is_file()
    new_head_version_id = revision.revision
    yield new_head_version_id
    path.unlink()


@pytest.fixture
def hame_database_upgraded(new_migration: str):
    event: db_manager.Event = {"action": "migrate_db"}
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    return new_migration


@pytest.fixture
def hame_database_downgraded(
    hame_database_upgraded: str, current_head_version_id: str | None
):
    event: db_manager.Event = {
        "action": "migrate_db",
        "version": current_head_version_id,
    }
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    return current_head_version_id


def drop_hame_db(main_db_params, root_db_params) -> None:
    conn = psycopg.connect(**root_db_params)
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                f"DROP DATABASE IF EXISTS {main_db_params['dbname']} WITH (FORCE)"
            )
            for user in os.environ.get("DB_USERS", "").split(","):
                cur.execute(f"DROP ROLE IF EXISTS {user}")
    finally:
        conn.close()


def wait_until_responsive(check, timeout, pause, clock=timeit.default_timer) -> None:
    """Wait until a service is responsive.
    Taken from docker_services.wait_until_responsive
    """
    ref = clock()
    now = ref
    while (now - ref) < timeout:
        if check():
            return
        time.sleep(pause)
        now = clock()

    raise Exception("Timeout reached while waiting on service!")


def is_responsive(params):
    succeeds = False
    try:
        with psycopg.connect(**params):
            succeeds = True
    except psycopg.OperationalError:
        pass
    return succeeds


def assert_database_is_alright(
    cur: psycopg.Cursor,
    expected_hame_count: int = hame_count,
    expected_codes_count: int = codes_count,
    expected_matview_count: int = matview_count,
) -> None:
    """Checks that the database has the right amount of tables with the right
    permissions.
    """
    # Check schemas
    cur.execute(
        "SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('hame', 'codes') ORDER BY schema_name DESC"
    )
    assert cur.fetchall() == [("hame",), ("codes",)]

    # Check users
    hame_users = os.environ.get("DB_USERS", "").split(",")
    cur.execute("SELECT rolname FROM pg_roles")
    assert set(hame_users).issubset({row[0] for row in cur.fetchall()})

    # Check schema permissions
    for user in hame_users:
        cur.execute(f"SELECT has_schema_privilege('{user}', 'hame', 'usage')")
        assert cur.fetchall() == [(True,)]
        cur.execute(f"SELECT has_schema_privilege('{user}', 'codes', 'usage')")
        assert cur.fetchall() == [(True,)]

    # Check hame tables
    cur.execute("SELECT tablename, tableowner FROM pg_tables WHERE schemaname='hame';")
    hame_tables = cur.fetchall()
    assert len(hame_tables) == expected_hame_count

    for table in hame_tables:
        table_name = table[0]
        owner = table[1]

        # Check table owner and read permissions
        assert owner == os.environ.get("SU_USER", "")
        cur.execute(
            f"SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_schema = 'hame' AND table_name='{table_name}';"
        )
        grants = cur.fetchall()
        assert (os.environ.get("R_USER"), "SELECT") in grants
        assert (os.environ.get("R_USER"), "INSERT") not in grants
        assert (os.environ.get("R_USER"), "UPDATE") not in grants
        assert (os.environ.get("R_USER"), "DELETE") not in grants
        assert (os.environ.get("RW_USER"), "SELECT") in grants
        assert (os.environ.get("RW_USER"), "INSERT") in grants
        assert (os.environ.get("RW_USER"), "UPDATE") in grants
        assert (os.environ.get("RW_USER"), "DELETE") in grants
        assert (os.environ.get("ADMIN_USER"), "SELECT") in grants
        assert (os.environ.get("ADMIN_USER"), "INSERT") in grants
        assert (os.environ.get("ADMIN_USER"), "UPDATE") in grants
        assert (os.environ.get("ADMIN_USER"), "DELETE") in grants

        # Check indexes
        cur.execute(
            f"SELECT indexdef FROM pg_indexes WHERE schemaname = 'hame' AND tablename = '{table_name}';"
        )
        index_defs = [index_def for (index_def,) in cur]

        cur.execute(
            f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'hame' AND table_name = '{table_name}';"
        )
        columns = [column for (column,) in cur]

        if "id" in columns:
            assert (
                f"CREATE UNIQUE INDEX {table_name}_pkey ON hame.{table_name} USING btree (id)"
                in index_defs
            )
        if "geom" in columns:
            assert (
                f"CREATE INDEX idx_{table_name}_geom ON hame.{table_name} USING gist (geom)"
                in index_defs
            )

        # Check ordering index, all ordering columns should have an index
        if "ordering" in columns:
            if table_name == "plan_regulation_group":
                assert (
                    "CREATE INDEX ix_plan_regulation_group_plan_id_ordering "
                    "ON hame.plan_regulation_group USING btree (plan_id, ordering)"
                ) in index_defs
            elif table_name in ("plan_regulation", "plan_proposition"):
                assert (
                    f"CREATE UNIQUE INDEX ix_{table_name}_plan_regulation_group_id_ordering "
                    f"ON hame.{table_name} USING btree (plan_regulation_group_id, ordering)"
                ) in index_defs
            elif table_name in (
                "land_use_area",
                "other_area",
                "line",
                "land_use_point",
                "other_point",
            ):
                assert (
                    f"CREATE UNIQUE INDEX ix_{table_name}_plan_id_ordering "
                    f"ON hame.{table_name} USING btree (plan_id, ordering)"
                ) in index_defs

    # Check code tables
    cur.execute("SELECT tablename, tableowner FROM pg_tables WHERE schemaname='codes';")
    code_tables = cur.fetchall()
    assert len(code_tables) == expected_codes_count

    for table in code_tables:
        table_name = table[0]
        owner = table[1]

        # Check table owner and read permissions
        assert owner == os.environ.get("SU_USER", "")
        cur.execute(
            f"SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_schema = 'codes' AND table_name='{table_name}';"
        )
        grants = cur.fetchall()
        assert (os.environ.get("R_USER"), "SELECT") in grants
        assert (os.environ.get("R_USER"), "INSERT") not in grants
        assert (os.environ.get("R_USER"), "UPDATE") not in grants
        assert (os.environ.get("R_USER"), "DELETE") not in grants
        assert (os.environ.get("RW_USER"), "SELECT") in grants
        assert (os.environ.get("RW_USER"), "INSERT") not in grants
        assert (os.environ.get("RW_USER"), "UPDATE") not in grants
        assert (os.environ.get("RW_USER"), "DELETE") not in grants
        assert (os.environ.get("ADMIN_USER"), "SELECT") in grants
        assert (os.environ.get("ADMIN_USER"), "INSERT") in grants
        assert (os.environ.get("ADMIN_USER"), "UPDATE") in grants
        assert (os.environ.get("ADMIN_USER"), "DELETE") in grants

        # Check code indexes
        cur.execute(
            f"SELECT * FROM pg_indexes WHERE schemaname = 'codes' AND tablename = '{table_name}';"
        )
        indexes = cur.fetchall()
        cur.execute(
            f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'codes' AND table_name = '{table_name}';"
        )
        columns = [column for (column,) in cur]
        assert (
            "codes",
            table_name,
            f"{table_name}_pkey",
            None,
            f"CREATE UNIQUE INDEX {table_name}_pkey ON codes.{table_name} USING btree (id)",
        ) in indexes
        if "level" in columns:
            assert (
                "codes",
                table_name,
                f"ix_codes_{table_name}_level",
                None,
                f"CREATE INDEX ix_codes_{table_name}_level ON codes.{table_name} USING btree (level)",
            ) in indexes
        if "parent" in columns:
            assert (
                "codes",
                table_name,
                f"ix_codes_{table_name}_parent_id",
                None,
                f"CREATE INDEX ix_codes_{table_name}_parent_id ON codes.{table_name} USING btree (parent_id)",
            ) in indexes
        if "short_name" in columns:
            assert (
                "codes",
                table_name,
                f"ix_codes_{table_name}_short_name",
                None,
                f"CREATE INDEX ix_codes_{table_name}_short_name ON codes.{table_name} USING btree (short_name)",
            ) in indexes
        if "value" in columns:
            assert (
                "codes",
                table_name,
                f"ix_codes_{table_name}_value",
                None,
                f"CREATE UNIQUE INDEX ix_codes_{table_name}_value ON codes.{table_name} USING btree (value)",
            ) in indexes

    # TODO: Check materialized views once we have any
    # cur.execute(
    #     "SELECT matviewname, matviewowner FROM pg_matviews WHERE schemaname='kooste';"
    # )
    # materialized_views = cur.fetchall()
    # assert len(materialized_views) == expected_matview_count

    # for view in materialized_views:
    #     view_name = view[0]
    #     owner = view[1]

    #     # Check view owner and read permissions
    #     # Materialized views must be owned by the read_write user so they can be
    #     updated automatically!
    #     assert owner == os.environ.get("RW_USER", "")
    #     # Materialized views permissions are only stored in psql specific tables
    #     cur.execute(f"SELECT relacl FROM pg_class WHERE relname='{view_name}';")
    #     permission_string = cur.fetchall()[0][0]
    #     assert f"{os.environ.get('R_USER')}=r/" in permission_string
    #     assert f"{os.environ.get('RW_USER')}=arwdDxt/" in permission_string
    #     assert f"{os.environ.get('ADMIN_USER')}=arwdDxt/" in permission_string


@pytest.fixture(scope="module")
def admin_connection_string(hame_database_created: str | None) -> str:
    return DatabaseHelper(user=User.ADMIN).get_connection_string()


@pytest.fixture(scope="module")
def rw_connection_string(hame_database_created: str | None) -> str:
    return DatabaseHelper(user=User.READ_WRITE).get_connection_string()


@pytest.fixture(scope="module")
def session(admin_connection_string: str):
    engine = sqlalchemy.create_engine(admin_connection_string)
    session = sessionmaker(bind=engine)
    return session()


@pytest.fixture
def rollback_after(session: Session):
    yield
    session.rollback()


@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parent / "test_data"


@pytest.fixture
def get_test_json(test_data_dir: Path) -> Callable[[str], str]:
    def _get_test_json(file_name: str) -> str:
        return (test_data_dir / file_name).read_text(encoding="utf-8")

    return _get_test_json


@pytest.fixture
def complete_plan_json(
    get_test_json: Callable[[str], str], remove_plan: Callable[[str], None]
) -> Generator[str]:
    yield get_test_json("complete_plan.json")

    remove_plan("09c62caa-c56f-474d-9c0a-1ba4c4188cb2")


@pytest.fixture
def invalid_plan_json(
    get_test_json: Callable[[str], str], remove_plan: Callable[[str], None]
) -> Generator[str]:
    yield get_test_json("invalid_plan.json")

    remove_plan("5e928c8f-1a4d-4912-853b-c92c844ae8ec")


@pytest.fixture
def simple_plan_json(
    get_test_json: Callable[[str], str], remove_plan: Callable[[str], None]
) -> Generator[str]:
    yield get_test_json("simple_plan.json")

    remove_plan("7f522b2f-8b45-4a17-b433-5f47271b579e")


@pytest.fixture
def delete_plan_after_test(session: Session) -> Generator[Callable[[str], None]]:
    plan_id = None

    def _set_plan_id(id: str) -> None:
        nonlocal plan_id
        plan_id = id

    yield _set_plan_id

    if plan_id and (plan := session.get(models.Plan, plan_id)):
        session.delete(plan)
        print(f"Removed plan {plan_id} after test")


@pytest.fixture
def remove_plan(session: Session) -> Callable[[str], None]:
    def _remove_plan(plan_id: str) -> None:
        if plan := session.get(models.Plan, plan_id):
            session.delete(plan)
            session.commit()

    return _remove_plan


T = TypeVar("T")
type ReturnSame[T] = Callable[[T], T]


@pytest.fixture
def temp_session_feature(session: Session) -> Generator[ReturnSame]:
    created_instances = []

    def add_instance(instance: T) -> T:
        session.add(instance)
        session.commit()
        created_instances.append(instance)
        return instance

    yield add_instance

    for instance in reversed(created_instances):
        if instance not in session:
            # Already deleted
            continue
        # Refresh to update collections changed by cascade deletes done by db.
        # Without this, sqlalchemy tries to delete things already deleted and gives warnings.
        session.refresh(instance)
        session.delete(instance)
        session.flush()  # flush to delete in right order
    session.commit()


# Code fixtures


@pytest.fixture
def code_instance(temp_session_feature: ReturnSame) -> codes.LifeCycleStatus:
    instance = codes.LifeCycleStatus(value="test", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def another_code_instance(temp_session_feature: ReturnSame) -> codes.LifeCycleStatus:
    instance = codes.LifeCycleStatus(value="test2", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def pending_status_instance(temp_session_feature: ReturnSame) -> codes.LifeCycleStatus:
    instance = codes.LifeCycleStatus(value="02", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def preparation_status_instance(
    temp_session_feature: ReturnSame,
) -> codes.LifeCycleStatus:
    instance = codes.LifeCycleStatus(value="03", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def plan_proposal_status_instance(
    temp_session_feature: ReturnSame,
) -> codes.LifeCycleStatus:
    instance = codes.LifeCycleStatus(value="04", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def approved_status_instance(temp_session_feature: ReturnSame) -> codes.LifeCycleStatus:
    instance = codes.LifeCycleStatus(value="06", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def valid_status_instance(temp_session_feature: ReturnSame) -> codes.LifeCycleStatus:
    instance = codes.LifeCycleStatus(value="13", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def plan_type_instance(temp_session_feature: ReturnSame) -> codes.PlanType:
    # Let's use real code to allow testing API endpoints that require this
    # code value as parameter
    # https://koodistot.suomi.fi/codescheme;registryCode=rytj;schemeCode=RY_Kaavalaji
    # 11: Kokonaismaakuntakaava
    instance = codes.PlanType(value="11", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_underground_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfUnderground:
    instance = codes.TypeOfUnderground(value="01", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_plan_regulation_group_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulationGroup:
    instance = codes.TypeOfPlanRegulationGroup(value="test", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_general_plan_regulation_group_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulationGroup:
    instance = codes.TypeOfPlanRegulationGroup(
        value="generalRegulations", status="LOCAL"
    )
    return temp_session_feature(instance)


@pytest.fixture
def type_of_land_use_plan_regulation_group_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulationGroup:
    instance = codes.TypeOfPlanRegulationGroup(
        value="landUseRegulations", status="LOCAL"
    )
    return temp_session_feature(instance)


@pytest.fixture
def type_of_other_area_plan_regulation_group_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulationGroup:
    instance = codes.TypeOfPlanRegulationGroup(
        value="otherAreaRegulations", status="LOCAL"
    )
    return temp_session_feature(instance)


@pytest.fixture
def type_of_line_plan_regulation_group_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulationGroup:
    instance = codes.TypeOfPlanRegulationGroup(value="lineRegulations", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_point_plan_regulation_group_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulationGroup:
    instance = codes.TypeOfPlanRegulationGroup(
        value="otherPointRegulations", status="LOCAL"
    )
    return temp_session_feature(instance)


@pytest.fixture
def type_of_plan_regulation_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulation:
    instance = codes.TypeOfPlanRegulation(value="asumisenAlue", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_plan_regulation_allowed_area_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulation:
    instance = codes.TypeOfPlanRegulation(value="sallittuKerrosala", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_plan_regulation_number_of_stories_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulation:
    instance = codes.TypeOfPlanRegulation(
        value="maanpaallinenKerroslukuArvovali", status="LOCAL"
    )
    return temp_session_feature(instance)


@pytest.fixture
def type_of_plan_regulation_ground_elevation_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulation:
    instance = codes.TypeOfPlanRegulation(
        value="maanpinnanKorkeusasema", status="LOCAL"
    )
    return temp_session_feature(instance)


@pytest.fixture
def type_of_plan_regulation_verbal_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulation:
    instance = codes.TypeOfPlanRegulation(value="sanallinenMaarays", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_plan_regulation_street_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulation:
    instance = codes.TypeOfPlanRegulation(value="katu", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_plan_regulation_construction_area_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfPlanRegulation:
    instance = codes.TypeOfPlanRegulation(value="rakennusala", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_verbal_plan_regulation_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfVerbalPlanRegulation:
    instance = codes.TypeOfVerbalPlanRegulation(value="perustaminen", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_main_use_additional_information_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfAdditionalInformation:
    instance = codes.TypeOfAdditionalInformation(
        value="paakayttotarkoitus", status="LOCAL"
    )
    return temp_session_feature(instance)


@pytest.fixture
def type_of_proportion_of_intended_use_additional_information_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfAdditionalInformation:
    instance = codes.TypeOfAdditionalInformation(
        value="kayttotarkoituksenOsuusKerrosalastaK-m2", status="LOCAL"
    )
    return temp_session_feature(instance)


@pytest.fixture
def type_of_sub_area_additional_information_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfAdditionalInformation:
    instance = codes.TypeOfAdditionalInformation(value="osaAlue", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_intended_use_allocation_additional_information_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfAdditionalInformation:
    instance = codes.TypeOfAdditionalInformation(
        value="kayttotarkoituskohdistus", status="LOCAL"
    )
    return temp_session_feature(instance)


@pytest.fixture
def type_of_source_data_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfSourceData:
    instance = codes.TypeOfSourceData(value="test", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_document_plan_map_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfDocument:
    instance = codes.TypeOfDocument(value="03", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_document_oas_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfDocument:
    instance = codes.TypeOfDocument(value="14", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_document_plan_description_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfDocument:
    instance = codes.TypeOfDocument(value="06", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def type_of_document_other_instance(
    temp_session_feature: ReturnSame,
) -> codes.TypeOfDocument:
    instance = codes.TypeOfDocument(value="99", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def category_of_publicity_public_instance(
    temp_session_feature: ReturnSame,
) -> codes.CategoryOfPublicity:
    instance = codes.CategoryOfPublicity(value="1", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def personal_data_content_no_personal_data_instance(
    temp_session_feature: ReturnSame,
) -> codes.PersonalDataContent:
    instance = codes.PersonalDataContent(value="1", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def retention_time_permanent_instance(
    temp_session_feature: ReturnSame,
) -> codes.RetentionTime:
    instance = codes.RetentionTime(value="01", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def language_finnish_instance(temp_session_feature: ReturnSame) -> codes.Language:
    instance = codes.Language(value="fi", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def legal_effects_of_master_plan_without_legal_effects_instance(
    temp_session_feature: ReturnSame,
) -> codes.LegalEffectsOfMasterPlan:
    instance = codes.LegalEffectsOfMasterPlan(value="2", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def municipality_instance(temp_session_feature: ReturnSame) -> codes.Municipality:
    instance = codes.Municipality(value="577", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def administrative_region_instance(
    temp_session_feature: ReturnSame,
) -> codes.AdministrativeRegion:
    instance = codes.AdministrativeRegion(value="01", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def another_administrative_region_instance(
    temp_session_feature: ReturnSame,
) -> codes.AdministrativeRegion:
    instance = codes.AdministrativeRegion(value="02", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def plan_theme_instance(temp_session_feature: ReturnSame) -> codes.PlanTheme:
    instance = codes.PlanTheme(value="01", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def codes_loaded(
    code_instance: codes.LifeCycleStatus,
    another_code_instance: codes.LifeCycleStatus,
    pending_status_instance: codes.LifeCycleStatus,
    preparation_status_instance: codes.LifeCycleStatus,
    plan_proposal_status_instance: codes.LifeCycleStatus,
    approved_status_instance: codes.LifeCycleStatus,
    valid_status_instance: codes.LifeCycleStatus,
    plan_type_instance: codes.PlanType,
    type_of_underground_instance: codes.TypeOfUnderground,
    type_of_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
    type_of_general_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
    type_of_land_use_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
    type_of_other_area_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
    type_of_line_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
    type_of_point_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
    type_of_plan_regulation_instance: codes.TypeOfPlanRegulation,
    type_of_plan_regulation_allowed_area_instance: codes.TypeOfPlanRegulation,
    type_of_plan_regulation_number_of_stories_instance: codes.TypeOfPlanRegulation,
    type_of_plan_regulation_ground_elevation_instance: codes.TypeOfPlanRegulation,
    type_of_plan_regulation_verbal_instance: codes.TypeOfPlanRegulation,
    type_of_plan_regulation_street_instance: codes.TypeOfPlanRegulation,
    type_of_plan_regulation_construction_area_instance: codes.TypeOfPlanRegulation,
    type_of_verbal_plan_regulation_instance: codes.TypeOfVerbalPlanRegulation,
    type_of_main_use_additional_information_instance: codes.TypeOfAdditionalInformation,
    type_of_proportion_of_intended_use_additional_information_instance: codes.TypeOfAdditionalInformation,
    type_of_sub_area_additional_information_instance: codes.TypeOfAdditionalInformation,
    type_of_intended_use_allocation_additional_information_instance: codes.TypeOfAdditionalInformation,
    type_of_source_data_instance: codes.TypeOfSourceData,
    type_of_document_plan_map_instance: codes.TypeOfDocument,
    type_of_document_oas_instance: codes.TypeOfDocument,
    type_of_document_plan_description_instance: codes.TypeOfDocument,
    type_of_document_other_instance: codes.TypeOfDocument,
    category_of_publicity_public_instance: codes.CategoryOfPublicity,
    personal_data_content_no_personal_data_instance: codes.PersonalDataContent,
    retention_time_permanent_instance: codes.RetentionTime,
    language_finnish_instance: codes.Language,
    legal_effects_of_master_plan_without_legal_effects_instance: codes.LegalEffectsOfMasterPlan,
    municipality_instance: codes.Municipality,
    administrative_region_instance: codes.AdministrativeRegion,
    another_administrative_region_instance: codes.AdministrativeRegion,
    plan_theme_instance: codes.PlanTheme,
    participation_plan_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
    plan_material_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
    draft_plan_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
    plan_proposal_sending_out_for_opinions_decision: codes.NameOfPlanCaseDecision,
    plan_proposal_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
    participation_plan_presenting_for_public_event: codes.TypeOfProcessingEvent,
    plan_material_presenting_for_public_event: codes.TypeOfProcessingEvent,
    plan_proposal_presenting_for_public_event: codes.TypeOfProcessingEvent,
    plan_proposal_requesting_for_opinions_event: codes.TypeOfProcessingEvent,
    presentation_to_the_public_interaction: codes.TypeOfInteractionEvent,
    decisionmaker_type: codes.TypeOfDecisionMaker,
) -> None:
    """Fixture that ensures all codes are loaded to the database.

    Used on import tests to ensure codes are there before import.
    """
    return


# Plan fixtures


@pytest.fixture
def plan_instance(
    temp_session_feature: ReturnSame,
    code_instance: codes.LifeCycleStatus,
    another_code_instance: codes.LifeCycleStatus,
    preparation_status_instance: codes.LifeCycleStatus,
    plan_proposal_status_instance: codes.LifeCycleStatus,
    organisation_instance: codes.Organisation,
    another_organisation_instance: codes.Organisation,
    plan_type_instance: codes.PlanType,
) -> models.Plan:
    # Any status and organisation instances that may be added to the plan later
    # have to be included above. If they are only created later, they will be torn
    # down too early and teardown will fail, because plan cannot have empty
    # status or organisation.
    instance = models.Plan(
        id=uuid.uuid4(),
        name={"fin": "Test Plan 1"},
        geom=from_shape(
            shape(
                {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [381849.834412134019658, 6677967.973336197435856],
                                [381849.834412134019658, 6680613.389312859624624],
                                [386378.427863708813675, 6680613.389312859624624],
                                [386378.427863708813675, 6677967.973336197435856],
                                [381849.834412134019658, 6677967.973336197435856],
                            ]
                        ]
                    ],
                }
            ),
            srid=PROJECT_SRID,
            extended=True,
        ),
        scale=1,
        description={"fin": "test_plan"},
        lifecycle_status=preparation_status_instance,
        organisation=organisation_instance,
        plan_type=plan_type_instance,
    )
    return temp_session_feature(instance)


@pytest.fixture
def another_plan_instance(
    temp_session_feature: ReturnSame,
    code_instance: codes.LifeCycleStatus,
    another_code_instance: codes.LifeCycleStatus,
    preparation_status_instance: codes.LifeCycleStatus,
    plan_proposal_status_instance: codes.LifeCycleStatus,
    organisation_instance: codes.Organisation,
    another_organisation_instance: codes.Organisation,
    plan_type_instance: codes.PlanType,
) -> models.Plan:
    # Any status and organisation instances that may be added to the plan later
    # have to be included above. If they are only created later, they will be torn
    # down too early and teardown will fail, because plan cannot have empty
    # status or organisation.
    instance = models.Plan(
        name={"fin": "Test Plan 2"},
        geom=from_shape(
            shape(
                {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [381849.834412134019658, 6677967.973336197435856],
                                [381849.834412134019658, 6680613.389312859624624],
                                [386378.427863708813675, 6680613.389312859624624],
                                [386378.427863708813675, 6677967.973336197435856],
                                [381849.834412134019658, 6677967.973336197435856],
                            ]
                        ]
                    ],
                }
            ),
            srid=PROJECT_SRID,
            extended=True,
        ),
        scale=1,
        description={"fin": "another_test_plan"},
        lifecycle_status=preparation_status_instance,
        organisation=organisation_instance,
        plan_type=plan_type_instance,
    )
    return temp_session_feature(instance)


# Organisation fixtures


@pytest.fixture
def organisation_instance(
    temp_session_feature: ReturnSame,
    administrative_region_instance: codes.AdministrativeRegion,
) -> models.Organisation:
    instance = models.Organisation(
        business_id="test", administrative_region=administrative_region_instance
    )
    return temp_session_feature(instance)


@pytest.fixture
def another_organisation_instance(
    temp_session_feature: ReturnSame,
    another_administrative_region_instance: codes.AdministrativeRegion,
) -> models.Organisation:
    instance = models.Organisation(
        business_id="other-test",
        administrative_region=another_administrative_region_instance,
    )
    return temp_session_feature(instance)


# Plan object fixtures


@pytest.fixture
def land_use_area_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: codes.Plan,
    plan_regulation_group_instance: codes.PlanRegulationGroup,
    numeric_plan_regulation_group_instance: codes.PlanRegulationGroup,
    decimal_plan_regulation_group_instance: codes.PlanRegulationGroup,
) -> models.LandUseArea:
    instance = models.LandUseArea(
        geom=from_shape(
            shape(
                {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [381849.834412134019658, 6677967.973336197435856],
                                [381849.834412134019658, 6680000.0],
                                [386378.427863708813675, 6680000.0],
                                [386378.427863708813675, 6677967.973336197435856],
                                [381849.834412134019658, 6677967.973336197435856],
                            ]
                        ]
                    ],
                }
            ),
            srid=PROJECT_SRID,
            extended=True,
        ),
        name={"fin": "test_land_use_area"},
        description={"fin": "test_land_use_area"},
        height_min=0.0,
        height_max=1.0,
        height_unit="m",
        ordering=1,
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
        plan_regulation_groups=[
            plan_regulation_group_instance,
            numeric_plan_regulation_group_instance,
            decimal_plan_regulation_group_instance,
        ],
    )
    return temp_session_feature(instance)


# This land use area is used to test land use regulations with additional information with
# code values, i.e. käyttötarkoituskohdistus.
@pytest.fixture
def pedestrian_street_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: codes.Plan,
    pedestrian_plan_regulation_group_instance: codes.PlanRegulationGroup,
):
    instance = models.LandUseArea(
        geom=from_shape(
            shape(
                {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [381849.834412134019658, 6680000.0],
                                [381849.834412134019658, 6680613.389312859624624],
                                [386378.427863708813675, 6680613.389312859624624],
                                [386378.427863708813675, 6680000.0],
                                [381849.834412134019658, 6680000.0],
                            ]
                        ]
                    ],
                }
            ),
            srid=PROJECT_SRID,
            extended=True,
        ),
        name={"fin": "test_pedestrian_street"},
        description={"fin": "test_pedestrian_street"},
        height_min=0.0,
        height_max=1.0,
        height_unit="m",
        ordering=2,
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
        plan_regulation_groups=[pedestrian_plan_regulation_group_instance],
    )
    return temp_session_feature(instance)


@pytest.fixture
def other_area_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: codes.Plan,
    construction_area_plan_regulation_group_instance: codes.PlanRegulationGroup,
):
    instance = models.OtherArea(
        geom=from_shape(
            shape(
                {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [
                            [
                                [382953, 6678582],
                                [382953, 6679385],
                                [383825, 6679385],
                                [383825, 6678582],
                                [382953, 6678582],
                            ]
                        ]
                    ],
                }
            ),
            srid=PROJECT_SRID,
            extended=True,
        ),
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
        plan_regulation_groups=[construction_area_plan_regulation_group_instance],
    )
    return temp_session_feature(instance)


@pytest.fixture
def line_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: codes.Plan,
    plan_regulation_group_instance: codes.PlanRegulationGroup,
):
    instance = models.Line(
        geom=from_shape(MultiLineString([[[382000, 6678000], [383000, 6678000]]])),
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    return temp_session_feature(instance)


@pytest.fixture
def land_use_point_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: codes.Plan,
    point_plan_regulation_group_instance: codes.PlanRegulationGroup,
):
    instance = models.LandUsePoint(
        geom=from_shape(MultiPoint([[382000, 6678000]])),
        name={"fin": "test_land_use_point"},
        description={"fin": "test_land_use_point"},
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
        plan_regulation_groups=[point_plan_regulation_group_instance],
    )
    return temp_session_feature(instance)


@pytest.fixture
def other_point_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: codes.Plan,
    point_plan_regulation_group_instance: codes.PlanRegulationGroup,
) -> models.OtherPoint:
    instance = models.OtherPoint(
        geom=from_shape(MultiPoint([[382000, 6678000], [383000, 6678000]])),
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
        plan_regulation_groups=[point_plan_regulation_group_instance],
    )
    return temp_session_feature(instance)


# Plan regulation fixtures


@pytest.fixture
def plan_regulation_group_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    type_of_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
) -> models.PlanRegulationGroup:
    instance = models.PlanRegulationGroup(
        short_name="K",
        plan=plan_instance,
        ordering=2,
        type_of_plan_regulation_group=type_of_plan_regulation_group_instance,
        name={"fin": "test_plan_regulation_group"},
    )
    return temp_session_feature(instance)


# Construction area must have its own plan regulation group
@pytest.fixture
def construction_area_plan_regulation_group_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    type_of_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
) -> models.PlanRegulationGroup:
    instance = models.PlanRegulationGroup(
        short_name="R",
        plan=plan_instance,
        ordering=6,
        type_of_plan_regulation_group=type_of_plan_regulation_group_instance,
        name={"fin": "test_construction_area_plan_regulation_group"},
    )
    return temp_session_feature(instance)


# Multiple numerical/decimal regulations cannot be in the same plan regulation group.
# Therefore, these plan regulations require their own groups.
@pytest.fixture
def numeric_plan_regulation_group_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    type_of_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
) -> models.PlanRegulationGroup:
    instance = models.PlanRegulationGroup(
        short_name="N",
        plan=plan_instance,
        ordering=3,
        type_of_plan_regulation_group=type_of_plan_regulation_group_instance,
        name={"fin": "test_numeric_plan_regulation_group"},
    )
    return temp_session_feature(instance)


@pytest.fixture
def decimal_plan_regulation_group_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    type_of_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
) -> models.PlanRegulationGroup:
    instance = models.PlanRegulationGroup(
        short_name="D",
        plan=plan_instance,
        ordering=4,
        type_of_plan_regulation_group=type_of_plan_regulation_group_instance,
        name={"fin": "test_decimal_plan_regulation_group"},
    )
    return temp_session_feature(instance)


@pytest.fixture
def pedestrian_plan_regulation_group_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    type_of_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
) -> models.PlanRegulationGroup:
    instance = models.PlanRegulationGroup(
        short_name="jk/pp",
        plan=plan_instance,
        ordering=5,
        type_of_plan_regulation_group=type_of_plan_regulation_group_instance,
        name={"fin": "test_pedestrian_plan_regulation_group"},
    )
    return temp_session_feature(instance)


@pytest.fixture
def point_plan_regulation_group_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    type_of_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
) -> models.PlanRegulationGroup:
    instance = models.PlanRegulationGroup(
        short_name="L",
        plan=plan_instance,
        ordering=1,
        type_of_plan_regulation_group=type_of_plan_regulation_group_instance,
        name={"fin": "test_point_plan_regulation_group"},
    )
    return temp_session_feature(instance)


@pytest.fixture
def general_regulation_group_instance(
    session: Session,
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    type_of_general_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
) -> models.PlanRegulationGroup:
    instance = models.PlanRegulationGroup(
        short_name="Y",
        plan=plan_instance,
        ordering=6,
        type_of_plan_regulation_group=type_of_general_plan_regulation_group_instance,
        name={"fin": "test_general_regulation_group"},
    )
    instance = temp_session_feature(instance)

    plan_instance.general_plan_regulation_groups.append(instance)

    return instance


@pytest.fixture
def empty_value_plan_regulation_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_plan_regulation_instance: codes.TypeOfPlanRegulation,
    plan_regulation_group_instance: codes.PlanRegulationGroup,
) -> models.PlanRegulation:
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_instance,
        plan_regulation_group=plan_regulation_group_instance,
        ordering=1,
    )
    return temp_session_feature(instance)


@pytest.fixture
def construction_area_plan_regulation_instance(
    session: Session,
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    construction_area_plan_regulation_group_instance: codes.PlanRegulationGroup,
    type_of_plan_regulation_construction_area_instance: codes.TypeOfPlanRegulation,
    make_additional_information_instance_of_type: Callable[
        [codes.TypeOfAdditionalInformation], models.AdditionalInformation
    ],
    type_of_sub_area_additional_information_instance: codes.TypeOfAdditionalInformation,
) -> models.PlanRegulation:
    sub_area_additional_information = make_additional_information_instance_of_type(
        type_of_sub_area_additional_information_instance
    )
    instance = models.PlanRegulation(
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_construction_area_instance,
        plan_regulation_group=construction_area_plan_regulation_group_instance,
        additional_information=[sub_area_additional_information],
        ordering=1,
    )
    instance = temp_session_feature(instance)
    return instance


@pytest.fixture
def numeric_plan_regulation_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_plan_regulation_allowed_area_instance: codes.TypeOfPlanRegulation,
    numeric_plan_regulation_group_instance: codes.PlanRegulationGroup,
) -> models.PlanRegulation:
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        value_data_type=AttributeValueDataType.POSITIVE_NUMERIC,
        numeric_value=1,
        unit="k-m2",
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_allowed_area_instance,
        plan_regulation_group=numeric_plan_regulation_group_instance,
        ordering=1,
    )
    return temp_session_feature(instance)


@pytest.fixture
def decimal_plan_regulation_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_plan_regulation_ground_elevation_instance: codes.TypeOfPlanRegulation,
    decimal_plan_regulation_group_instance: codes.PlanRegulationGroup,
) -> models.PlanRegulation:
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        value_data_type=AttributeValueDataType.DECIMAL,
        numeric_value=1.0,
        unit="m",
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_ground_elevation_instance,
        plan_regulation_group=decimal_plan_regulation_group_instance,
        ordering=1,
    )
    return temp_session_feature(instance)


@pytest.fixture
def numeric_range_plan_regulation_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_plan_regulation_number_of_stories_instance: codes.TypeOfPlanRegulation,
    plan_regulation_group_instance: codes.PlanRegulationGroup,
) -> models.PlanRegulation:
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        value_data_type=AttributeValueDataType.POSITIVE_NUMERIC_RANGE,
        numeric_range_min=2,
        numeric_range_max=3,
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_number_of_stories_instance,
        plan_regulation_group=plan_regulation_group_instance,
        ordering=3,
    )
    return temp_session_feature(instance)


@pytest.fixture
def text_plan_regulation_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_plan_regulation_instance: codes.TypeOfPlanRegulation,
    plan_regulation_group_instance: codes.PlanRegulationGroup,
) -> models.PlanRegulation:
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        value_data_type=AttributeValueDataType.LOCALIZED_TEXT,
        text_value={"fin": "test_value"},
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_instance,
        plan_regulation_group=plan_regulation_group_instance,
        additional_information=[],
        ordering=4,
    )
    return temp_session_feature(instance)


@pytest.fixture
def pedestrian_street_plan_regulation_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_plan_regulation_street_instance: codes.TypeOfPlanRegulation,
    pedestrian_plan_regulation_group_instance: codes.PlanRegulationGroup,
) -> models.PlanRegulation:
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_street_instance,
        plan_regulation_group=pedestrian_plan_regulation_group_instance,
        ordering=1,
    )
    return temp_session_feature(instance)


@pytest.fixture
def point_text_plan_regulation_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_plan_regulation_instance: codes.TypeOfPlanRegulation,
    point_plan_regulation_group_instance: codes.PlanRegulationGroup,
) -> models.PlanRegulation:
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        value_data_type=AttributeValueDataType.LOCALIZED_TEXT,
        text_value={"fin": "test_value"},
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_instance,
        plan_regulation_group=point_plan_regulation_group_instance,
        ordering=1,
    )
    return temp_session_feature(instance)


@pytest.fixture
def verbal_plan_regulation_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_plan_regulation_verbal_instance: codes.TypeOfPlanRegulation,
    type_of_verbal_plan_regulation_instance: codes.TypeOfVerbalPlanRegulation,
    plan_regulation_group_instance: codes.PlanRegulationGroup,
) -> models.PlanRegulation:
    """Looks like verbal plan regulations have to be serialized differently, type of
    verbal plan regulation is not allowed in other plan regulations. No idea how
    they differ from text regulations otherwise, though.
    """
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        value_data_type=AttributeValueDataType.LOCALIZED_TEXT,
        text_value={"fin": "test_value"},
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_verbal_instance,
        types_of_verbal_plan_regulations=[type_of_verbal_plan_regulation_instance],
        plan_regulation_group=plan_regulation_group_instance,
        ordering=5,
    )
    return temp_session_feature(instance)


@pytest.fixture
def general_plan_regulation_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_plan_regulation_instance: codes.TypeOfPlanRegulation,
    general_regulation_group_instance: codes.PlanRegulationGroup,
) -> models.PlanRegulation:
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        value_data_type=AttributeValueDataType.LOCALIZED_TEXT,
        text_value={"fin": "test_value"},
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_instance,
        plan_regulation_group=general_regulation_group_instance,
        ordering=1,
    )
    return temp_session_feature(instance)


@pytest.fixture
def plan_proposition_instance(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    plan_regulation_group_instance: codes.PlanRegulationGroup,
) -> models.PlanProposition:
    instance = models.PlanProposition(
        lifecycle_status=preparation_status_instance,
        plan_regulation_group=plan_regulation_group_instance,
        text_value={"fin": "test_recommendation"},
    )
    return temp_session_feature(instance)


# Source data fixtures


@pytest.fixture
def source_data_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    type_of_source_data_instance: codes.TypeOfSourceData,
) -> models.SourceData:
    instance = models.SourceData(
        additional_information_uri="http://test.fi",
        detachment_date=datetime.now(tz=LOCAL_TZ),
        plan=plan_instance,
        type_of_source_data=type_of_source_data_instance,
    )
    return temp_session_feature(instance)


# Document fixtures


@pytest.fixture
def document_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    type_of_document_oas_instance: codes.TypeOfDocument,
    category_of_publicity_public_instance: codes.CategoryOfPublicity,
    personal_data_content_no_personal_data_instance: codes.PersonalDataContent,
    retention_time_permanent_instance: codes.RetentionTime,
    language_finnish_instance: codes.Language,
) -> models.Document:
    instance = models.Document(
        name={"fin": "Osallistumis- ja arviointisuunnitelma"},
        type_of_document=type_of_document_oas_instance,
        permanent_document_identifier="HEL 2024-016009",
        category_of_publicity=category_of_publicity_public_instance,
        personal_data_content=personal_data_content_no_personal_data_instance,
        retention_time=retention_time_permanent_instance,
        language=language_finnish_instance,
        document_date=datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
        plan=plan_instance,
        url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    )
    return temp_session_feature(instance)


@pytest.fixture
def plan_report_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    type_of_document_plan_description_instance: codes.TypeOfDocument,
    category_of_publicity_public_instance: codes.CategoryOfPublicity,
    personal_data_content_no_personal_data_instance: codes.PersonalDataContent,
    retention_time_permanent_instance: codes.RetentionTime,
    language_finnish_instance: codes.Language,
) -> models.Document:
    instance = models.Document(
        name={"fin": "Kaavaselostus"},
        type_of_document=type_of_document_plan_description_instance,
        permanent_document_identifier="HEL 2024-016009",
        category_of_publicity=category_of_publicity_public_instance,
        personal_data_content=personal_data_content_no_personal_data_instance,
        retention_time=retention_time_permanent_instance,
        language=language_finnish_instance,
        document_date=datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
        plan=plan_instance,
        url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    )
    return temp_session_feature(instance)


@pytest.fixture
def other_document_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    type_of_document_other_instance: codes.TypeOfDocument,
    category_of_publicity_public_instance: codes.CategoryOfPublicity,
    personal_data_content_no_personal_data_instance: codes.PersonalDataContent,
    retention_time_permanent_instance: codes.RetentionTime,
    language_finnish_instance: codes.Language,
) -> models.Document:
    instance = models.Document(
        name={"fin": "Muu asiakirja"},
        type_of_document=type_of_document_other_instance,
        category_of_publicity=category_of_publicity_public_instance,
        personal_data_content=personal_data_content_no_personal_data_instance,
        retention_time=retention_time_permanent_instance,
        language=language_finnish_instance,
        document_date=datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
        plan=plan_instance,
        url="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    )
    return temp_session_feature(instance)


@pytest.fixture
def plan_map_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    type_of_document_plan_map_instance: codes.TypeOfDocument,
    category_of_publicity_public_instance: codes.CategoryOfPublicity,
    personal_data_content_no_personal_data_instance: codes.PersonalDataContent,
    retention_time_permanent_instance: codes.RetentionTime,
    language_finnish_instance: codes.Language,
) -> models.Document:
    instance = models.Document(
        name={"fin": "Kaavakartta"},
        type_of_document=type_of_document_plan_map_instance,
        category_of_publicity=category_of_publicity_public_instance,
        personal_data_content=personal_data_content_no_personal_data_instance,
        retention_time=retention_time_permanent_instance,
        language=language_finnish_instance,
        document_date=datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
        plan=plan_instance,
        url="https://raw.githubusercontent.com/GeoTIFF/test-data/refs/heads/main/files/GeogToWGS84GeoKey5.tif",
    )
    return temp_session_feature(instance)


# Date fixtures


@pytest.fixture
def lifecycle_date_instance(
    temp_session_feature: ReturnSame, code_instance: codes.LifeCycleStatus
) -> models.LifeCycleDate:
    instance = models.LifeCycleDate(
        lifecycle_status=code_instance,
        starting_at=datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
        ending_at=datetime(2025, 1, 1, tzinfo=LOCAL_TZ),
    )
    return temp_session_feature(instance)


@pytest.fixture
def pending_date_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    pending_status_instance: codes.LifeCycleStatus,
) -> models.LifeCycleDate:
    instance = models.LifeCycleDate(
        plan=plan_instance,
        lifecycle_status=pending_status_instance,
        starting_at=datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
        ending_at=datetime(2024, 2, 1, tzinfo=LOCAL_TZ),
    )
    return temp_session_feature(instance)


@pytest.fixture
def preparation_date_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    preparation_status_instance: codes.LifeCycleStatus,
) -> models.LifeCycleDate:
    instance = models.LifeCycleDate(
        plan=plan_instance,
        lifecycle_status=preparation_status_instance,
        starting_at=datetime(2024, 2, 1, tzinfo=LOCAL_TZ),
        ending_at=datetime(2024, 3, 1, tzinfo=LOCAL_TZ),
    )
    return temp_session_feature(instance)


@pytest.fixture
def plan_proposal_date_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    plan_proposal_status_instance: codes.LifeCycleStatus,
) -> models.LifeCycleDate:
    instance = models.LifeCycleDate(
        plan=plan_instance,
        lifecycle_status=plan_proposal_status_instance,
        starting_at=datetime(2024, 4, 1, tzinfo=LOCAL_TZ),
        ending_at=datetime(2024, 5, 1, tzinfo=LOCAL_TZ),
    )
    return temp_session_feature(instance)


@pytest.fixture
def approved_date_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    approved_status_instance: codes.LifeCycleStatus,
) -> models.LifeCycleDate:
    instance = models.LifeCycleDate(
        plan=plan_instance,
        lifecycle_status=approved_status_instance,
        starting_at=datetime(2024, 4, 1, tzinfo=LOCAL_TZ),
        ending_at=datetime(2024, 5, 1, tzinfo=LOCAL_TZ),
    )
    return temp_session_feature(instance)


@pytest.fixture
def valid_date_instance(
    temp_session_feature: ReturnSame,
    plan_instance: codes.Plan,
    valid_status_instance: codes.LifeCycleStatus,
) -> models.LifeCycleDate:
    instance = models.LifeCycleDate(
        plan=plan_instance,
        lifecycle_status=valid_status_instance,
        starting_at=datetime(2024, 5, 1, tzinfo=LOCAL_TZ),
    )
    return temp_session_feature(instance)


@pytest.fixture
def decision_date_instance(
    temp_session_feature: ReturnSame,
    preparation_date_instance: models.LifeCycleDate,
    participation_plan_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
):
    instance = models.EventDate(
        lifecycle_date=preparation_date_instance,
        decision=participation_plan_presenting_for_public_decision,
        starting_at=datetime(2024, 2, 5, tzinfo=LOCAL_TZ),
    )
    return temp_session_feature(instance)


@pytest.fixture
def processing_event_date_instance(
    temp_session_feature: ReturnSame,
    preparation_date_instance: models.LifeCycleDate,
    participation_plan_presenting_for_public_event: codes.TypeOfProcessingEvent,
):
    instance = models.EventDate(
        lifecycle_date=preparation_date_instance,
        processing_event=participation_plan_presenting_for_public_event,
        starting_at=datetime(2024, 2, 15, tzinfo=LOCAL_TZ),
    )
    return temp_session_feature(instance)


@pytest.fixture
def interaction_event_date_instance(
    temp_session_feature: ReturnSame,
    preparation_date_instance: models.LifeCycleDate,
    presentation_to_the_public_interaction: codes.TypeOfInteractionEvent,
):
    instance = models.EventDate(
        lifecycle_date=preparation_date_instance,
        interaction_event=presentation_to_the_public_interaction,
        starting_at=datetime(2024, 2, 15, tzinfo=LOCAL_TZ),
        ending_at=datetime(2024, 2, 28, tzinfo=LOCAL_TZ),
    )
    return temp_session_feature(instance)


# Additional information fixtures


@pytest.fixture
def main_use_additional_information_instance(
    temp_session_feature: ReturnSame,
    type_of_main_use_additional_information_instance: codes.TypeOfAdditionalInformation,
    empty_value_plan_regulation_instance: codes.PlanRegulation,
):
    instance = models.AdditionalInformation(
        plan_regulation=empty_value_plan_regulation_instance,
        type_of_additional_information=type_of_main_use_additional_information_instance,
    )
    return temp_session_feature(instance)


@pytest.fixture
def proportion_of_intended_use_additional_information_instance(
    temp_session_feature: ReturnSame,
    type_of_proportion_of_intended_use_additional_information_instance: codes.TypeOfAdditionalInformation,
    empty_value_plan_regulation_instance: codes.PlanRegulation,
):
    instance = models.AdditionalInformation(
        plan_regulation=empty_value_plan_regulation_instance,
        type_of_additional_information=type_of_proportion_of_intended_use_additional_information_instance,
        value_data_type=enums.AttributeValueDataType.POSITIVE_NUMERIC,
        numeric_value=2500,
        unit="k-m2",
    )
    return temp_session_feature(instance)


@pytest.fixture
def make_additional_information_instance_of_type(
    session: Session,
) -> Generator[
    Callable[[codes.TypeOfAdditionalInformation], models.AdditionalInformation]
]:
    created_instances = []

    def _make_additional_information_instance_of_type(
        type_of_additional_information: codes.TypeOfAdditionalInformation,
    ) -> models.AdditionalInformation:
        instance = models.AdditionalInformation(
            type_of_additional_information=type_of_additional_information
        )
        created_instances.append(instance)
        return instance

    yield _make_additional_information_instance_of_type

    for instance in created_instances:
        if instance in session:
            session.delete(instance)
    session.commit()


# Complete fixtures


@pytest.fixture
def complete_test_plan(
    session: Session,
    document_instance: models.Document,
    plan_report_instance: models.Document,
    other_document_instance: models.Document,
    plan_map_instance: models.Document,
    plan_instance: models.Plan,
    land_use_area_instance: models.LandUseArea,
    pedestrian_street_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    land_use_point_instance: models.LandUsePoint,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    pedestrian_plan_regulation_group_instance: models.PlanRegulationGroup,
    construction_area_plan_regulation_group_instance: models.PlanRegulationGroup,
    numeric_plan_regulation_group_instance: models.PlanRegulationGroup,
    decimal_plan_regulation_group_instance: models.PlanRegulationGroup,
    point_plan_regulation_group_instance: models.PlanRegulationGroup,
    general_regulation_group_instance: models.PlanRegulationGroup,
    empty_value_plan_regulation_instance: models.PlanRegulation,
    text_plan_regulation_instance: models.PlanRegulation,
    pedestrian_street_plan_regulation_instance: models.PlanRegulation,
    construction_area_plan_regulation_instance: models.PlanRegulation,
    point_text_plan_regulation_instance: models.PlanRegulation,
    numeric_plan_regulation_instance: models.PlanRegulation,
    decimal_plan_regulation_instance: models.PlanRegulation,
    numeric_range_plan_regulation_instance: models.PlanRegulation,
    verbal_plan_regulation_instance: models.PlanRegulation,
    general_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    proportion_of_intended_use_additional_information_instance: models.AdditionalInformation,
    legal_effects_of_master_plan_without_legal_effects_instance: codes.LegalEffectsOfMasterPlan,
    plan_theme_instance: codes.PlanTheme,
    type_of_main_use_additional_information_instance: codes.TypeOfAdditionalInformation,
    type_of_proportion_of_intended_use_additional_information_instance: codes.TypeOfAdditionalInformation,
    type_of_intended_use_allocation_additional_information_instance: codes.TypeOfAdditionalInformation,
    make_additional_information_instance_of_type: Callable[
        [codes.TypeOfAdditionalInformation], models.AdditionalInformation
    ],
    participation_plan_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
    plan_material_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
    draft_plan_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
    plan_proposal_sending_out_for_opinions_decision: codes.NameOfPlanCaseDecision,
    plan_proposal_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
    participation_plan_presenting_for_public_event: codes.TypeOfProcessingEvent,
    plan_material_presenting_for_public_event: codes.TypeOfProcessingEvent,
    plan_proposal_presenting_for_public_event: codes.TypeOfProcessingEvent,
    plan_proposal_requesting_for_opinions_event: codes.TypeOfProcessingEvent,
    presentation_to_the_public_interaction: codes.TypeOfInteractionEvent,
    decisionmaker_type: codes.TypeOfDecisionMaker,
    pending_date_instance: models.LifeCycleDate,
    preparation_date_instance: models.LifeCycleDate,
    decision_date_instance: models.EventDate,
    processing_event_date_instance: models.EventDate,
    interaction_event_date_instance: models.EventDate,
) -> models.Plan:
    """Plan data that might be more or less complete, to be tested and validated with the
    Ryhti API.

    For the plan *matter* to be validated, we also need extra code objects (that are not
    linked to the plan in the database) to be committed to the database, and some
    dates for the plan lifecycle statuses to be set.
    """
    # In tests, we need known dates for the phases. Plan has a trigger-generated additional
    # date for the preparation phase that we must delete before testing.
    session.delete(plan_instance.lifecycle_dates[2])
    session.commit()

    # Add the optional (nullable) relationships. We don't want them to be present in
    # all fixtures.
    plan_instance.legal_effects_of_master_plan.append(
        legal_effects_of_master_plan_without_legal_effects_instance
    )

    empty_value_plan_regulation_instance.plan_themes.append(plan_theme_instance)
    # empty value plan regulation may have intended use
    empty_value_plan_regulation_instance.additional_information.append(
        make_additional_information_instance_of_type(
            type_of_main_use_additional_information_instance
        )
    )
    # empty value plan regulation may have proportion of intended use
    empty_value_plan_regulation_instance.additional_information.append(
        proportion_of_intended_use_additional_information_instance
    )

    numeric_plan_regulation_instance.plan_themes.append(plan_theme_instance)
    # allowed area numeric value cannot be used with intended use regulation type

    decimal_plan_regulation_instance.plan_themes.append(plan_theme_instance)
    # elevation decimal value cannot be used with intended use regulation type

    text_plan_regulation_instance.plan_themes.append(plan_theme_instance)
    # text value plan regulation may have intended use
    text_plan_regulation_instance.additional_information.append(
        make_additional_information_instance_of_type(
            type_of_main_use_additional_information_instance
        )
    )

    point_text_plan_regulation_instance.plan_themes.append(plan_theme_instance)
    # point cannot *currently* be used with intended use regulation type

    numeric_range_plan_regulation_instance.plan_themes.append(plan_theme_instance)
    # numeric range cannot be used with intended use regulation type

    verbal_plan_regulation_instance.plan_themes.append(plan_theme_instance)
    # verbal plan regulation cannot be used with intended use regulation type

    general_plan_regulation_instance.plan_themes.append(plan_theme_instance)
    # general plan regulation cannot be used with intended use regulation type

    pedestrian_street_plan_regulation_instance.plan_themes.append(plan_theme_instance)
    # pedestrian street must have intended use *and* two intended use allocations
    # (käyttötarkoituskohdistus):
    pedestrian_street_plan_regulation_instance.additional_information.append(
        make_additional_information_instance_of_type(
            type_of_main_use_additional_information_instance
        )
    )
    pedestrian_intended_use_allocation = make_additional_information_instance_of_type(
        type_of_intended_use_allocation_additional_information_instance
    )
    pedestrian_intended_use_allocation.value_data_type = AttributeValueDataType.CODE
    pedestrian_intended_use_allocation.code_list = (
        "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji"
    )
    pedestrian_intended_use_allocation.code_value = (
        "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/jalankulkualue"
    )
    pedestrian_intended_use_allocation.code_title = {
        "eng": "Pedestrian area",
        "fin": "Jalankulkualue",
        "swe": "Fotgångarområde",
    }
    pedestrian_street_plan_regulation_instance.additional_information.append(
        pedestrian_intended_use_allocation
    )
    cycling_intended_use_allocation = make_additional_information_instance_of_type(
        type_of_intended_use_allocation_additional_information_instance
    )
    cycling_intended_use_allocation.value_data_type = AttributeValueDataType.CODE
    cycling_intended_use_allocation.code_list = (
        "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji"
    )
    cycling_intended_use_allocation.code_value = (
        "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/pyorailyalue"
    )
    cycling_intended_use_allocation.code_title = {
        "eng": "Cycling area",
        "fin": "Pyöräilyalue",
        "swe": "Cykelområde",
    }
    pedestrian_street_plan_regulation_instance.additional_information.append(
        cycling_intended_use_allocation
    )

    plan_proposition_instance.plan_themes.append(plan_theme_instance)
    session.commit()
    return plan_instance


@pytest.fixture
def another_test_plan(
    session: Session, another_plan_instance: codes.Plan
) -> models.Plan:
    return another_plan_instance


@pytest.fixture
def participation_plan_presenting_for_public_decision(
    temp_session_feature: ReturnSame, preparation_status_instance: codes.LifeCycleStatus
) -> codes.NameOfPlanCaseDecision:
    instance = codes.NameOfPlanCaseDecision(
        value="04", status="LOCAL", allowed_statuses=[preparation_status_instance]
    )
    return temp_session_feature(instance)


@pytest.fixture
def plan_material_presenting_for_public_decision(
    temp_session_feature: ReturnSame, preparation_status_instance: codes.LifeCycleStatus
) -> codes.NameOfPlanCaseDecision:
    instance = codes.NameOfPlanCaseDecision(
        value="05", status="LOCAL", allowed_statuses=[preparation_status_instance]
    )
    return temp_session_feature(instance)


@pytest.fixture
def draft_plan_presenting_for_public_decision(
    temp_session_feature: ReturnSame, preparation_status_instance: codes.LifeCycleStatus
) -> codes.NameOfPlanCaseDecision:
    instance = codes.NameOfPlanCaseDecision(
        value="06", status="LOCAL", allowed_statuses=[preparation_status_instance]
    )
    return temp_session_feature(instance)


@pytest.fixture
def plan_proposal_sending_out_for_opinions_decision(
    temp_session_feature: ReturnSame,
    plan_proposal_status_instance: codes.LifeCycleStatus,
) -> codes.NameOfPlanCaseDecision:
    instance = codes.NameOfPlanCaseDecision(
        value="07", status="LOCAL", allowed_statuses=[plan_proposal_status_instance]
    )
    return temp_session_feature(instance)


@pytest.fixture
def plan_proposal_presenting_for_public_decision(
    temp_session_feature: ReturnSame,
    plan_proposal_status_instance: codes.LifeCycleStatus,
) -> codes.NameOfPlanCaseDecision:
    instance = codes.NameOfPlanCaseDecision(
        value="08", status="LOCAL", allowed_statuses=[plan_proposal_status_instance]
    )
    return temp_session_feature(instance)


@pytest.fixture
def participation_plan_presenting_for_public_event(
    temp_session_feature: ReturnSame, preparation_status_instance: codes.LifeCycleStatus
) -> codes.TypeOfProcessingEvent:
    instance = codes.TypeOfProcessingEvent(
        value="05", status="LOCAL", allowed_statuses=[preparation_status_instance]
    )
    return temp_session_feature(instance)


@pytest.fixture
def plan_material_presenting_for_public_event(
    temp_session_feature: ReturnSame, preparation_status_instance: codes.LifeCycleStatus
) -> codes.TypeOfProcessingEvent:
    instance = codes.TypeOfProcessingEvent(
        value="06", status="LOCAL", allowed_statuses=[preparation_status_instance]
    )
    return temp_session_feature(instance)


@pytest.fixture
def plan_proposal_presenting_for_public_event(
    temp_session_feature: ReturnSame,
    plan_proposal_status_instance: codes.LifeCycleStatus,
) -> codes.TypeOfProcessingEvent:
    instance = codes.TypeOfProcessingEvent(
        value="07", status="LOCAL", allowed_statuses=[plan_proposal_status_instance]
    )
    return temp_session_feature(instance)


@pytest.fixture
def plan_proposal_requesting_for_opinions_event(
    temp_session_feature: ReturnSame,
    plan_proposal_status_instance: codes.LifeCycleStatus,
) -> codes.TypeOfProcessingEvent:
    instance = codes.TypeOfProcessingEvent(
        value="08", status="LOCAL", allowed_statuses=[plan_proposal_status_instance]
    )
    return temp_session_feature(instance)


@pytest.fixture
def presentation_to_the_public_interaction(
    temp_session_feature: ReturnSame,
    preparation_status_instance: codes.LifeCycleStatus,
    plan_proposal_status_instance: codes.LifeCycleStatus,
) -> codes.TypeOfInteractionEvent:
    instance = codes.TypeOfInteractionEvent(
        value="01",
        status="LOCAL",
        allowed_statuses=[preparation_status_instance, plan_proposal_status_instance],
    )
    return temp_session_feature(instance)


@pytest.fixture
def decisionmaker_type(temp_session_feature: ReturnSame) -> codes.TypeOfDecisionMaker:
    instance = codes.TypeOfDecisionMaker(value="01", status="LOCAL")
    return temp_session_feature(instance)


@pytest.fixture
def desired_plan_dict(
    complete_test_plan: models.Plan,
    land_use_area_instance: models.LandUseArea,
    pedestrian_street_instance: models.LandUseArea,
    other_area_instance: models.OtherArea,
    land_use_point_instance: models.LandUsePoint,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    numeric_plan_regulation_group_instance: models.PlanRegulationGroup,
    decimal_plan_regulation_group_instance: models.PlanRegulationGroup,
    pedestrian_plan_regulation_group_instance: models.PlanRegulationGroup,
    construction_area_plan_regulation_group_instance: models.PlanRegulationGroup,
    point_plan_regulation_group_instance: models.PlanRegulationGroup,
    general_regulation_group_instance: models.PlanRegulationGroup,
    empty_value_plan_regulation_instance: models.PlanRegulation,
    text_plan_regulation_instance: models.PlanRegulation,
    pedestrian_street_plan_regulation_instance: models.PlanRegulation,
    construction_area_plan_regulation_instance: models.PlanRegulation,
    point_text_plan_regulation_instance: models.PlanRegulation,
    numeric_plan_regulation_instance: models.PlanRegulation,
    decimal_plan_regulation_instance: models.PlanRegulation,
    numeric_range_plan_regulation_instance: models.PlanRegulation,
    verbal_plan_regulation_instance: models.PlanRegulation,
    general_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
) -> dict:
    """Plan dict based on https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Avoin/ryhti-plan-public-validate-api.json

    Let's 1) write explicitly the complex fields, and 2) just check that the simple fields have
    the same values as the original plan fixture in the database.
    """
    return {
        "planKey": complete_test_plan.id,
        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
        "legalEffectOfLocalMasterPlans": [
            "http://uri.suomi.fi/codelist/rytj/oikeusvaik_YK/code/2"
        ],
        "scale": complete_test_plan.scale,
        "geographicalArea": {
            "srid": str(PROJECT_SRID),
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [381849.834412134019658, 6677967.973336197435856],
                        [381849.834412134019658, 6680613.389312859624624],
                        [386378.427863708813675, 6680613.389312859624624],
                        [386378.427863708813675, 6677967.973336197435856],
                        [381849.834412134019658, 6677967.973336197435856],
                    ]
                ],
            },
        },
        "planMaps": [],
        "planAnnexes": [],
        "otherPlanMaterials": [],
        "planReport": None,
        "periodOfValidity": None,
        "approvalDate": None,
        "generalRegulationGroups": [
            {
                "generalRegulationGroupKey": general_regulation_group_instance.id,
                "titleOfPlanRegulation": general_regulation_group_instance.name,
                "groupNumber": general_regulation_group_instance.ordering,
                "planRegulations": [
                    {
                        "planRegulationKey": general_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/asumisenAlue",
                        "value": {
                            "dataType": "LocalizedText",
                            "text": general_plan_regulation_instance.text_value,
                        },
                        "subjectIdentifiers": general_plan_regulation_instance.subject_identifiers,
                        "additionalInformations": [],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01"
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            general_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    }
                ],
                "planRecommendations": [],
            }
        ],
        "planDescription": (
            complete_test_plan.description["fin"]
            if complete_test_plan.description
            else None
        ),  # TODO: should this be a single language string? why?
        "planObjects": [
            {
                "planObjectKey": land_use_area_instance.id,
                "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                "undergroundStatus": "http://uri.suomi.fi/codelist/rytj/RY_MaanalaisuudenLaji/code/01",
                "geometry": {
                    "srid": str(PROJECT_SRID),
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [381849.834412134019658, 6677967.973336197435856],
                                [381849.834412134019658, 6680000.0],
                                [386378.427863708813675, 6680000.0],
                                [386378.427863708813675, 6677967.973336197435856],
                                [381849.834412134019658, 6677967.973336197435856],
                            ]
                        ],
                    },
                },
                "name": land_use_area_instance.name,
                "description": land_use_area_instance.description,
                "objectNumber": land_use_area_instance.ordering,
                "verticalLimit": {
                    "dataType": "DecimalRange",
                    "minimumValue": land_use_area_instance.height_min,
                    "maximumValue": land_use_area_instance.height_max,
                    "unitOfMeasure": land_use_area_instance.height_unit,
                },
                "periodOfValidity": None,
            },
            {
                "planObjectKey": pedestrian_street_instance.id,
                "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                "undergroundStatus": "http://uri.suomi.fi/codelist/rytj/RY_MaanalaisuudenLaji/code/01",
                "geometry": {
                    "srid": str(PROJECT_SRID),
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [381849.834412134019658, 6680000.0],
                                [381849.834412134019658, 6680613.389312859624624],
                                [386378.427863708813675, 6680613.389312859624624],
                                [386378.427863708813675, 6680000.0],
                                [381849.834412134019658, 6680000.0],
                            ]
                        ],
                    },
                },
                "name": pedestrian_street_instance.name,
                "description": pedestrian_street_instance.description,
                "objectNumber": pedestrian_street_instance.ordering,
                "verticalLimit": {
                    "dataType": "DecimalRange",
                    "minimumValue": pedestrian_street_instance.height_min,
                    "maximumValue": pedestrian_street_instance.height_max,
                    "unitOfMeasure": pedestrian_street_instance.height_unit,
                },
                "periodOfValidity": None,
            },
            {
                "planObjectKey": other_area_instance.id,
                "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                "undergroundStatus": "http://uri.suomi.fi/codelist/rytj/RY_MaanalaisuudenLaji/code/01",
                "geometry": {
                    "srid": str(PROJECT_SRID),
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [382953.0, 6678582.0],
                                [382953.0, 6679385.0],
                                [383825.0, 6679385.0],
                                [383825.0, 6678582.0],
                                [382953.0, 6678582.0],
                            ]
                        ],
                    },
                },
                "name": other_area_instance.name,
                "description": other_area_instance.description,
                "objectNumber": None,
                "relatedPlanObjectKeys": [land_use_area_instance.id],
                "periodOfValidity": None,
            },
            {
                "planObjectKey": land_use_point_instance.id,
                "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                "undergroundStatus": "http://uri.suomi.fi/codelist/rytj/RY_MaanalaisuudenLaji/code/01",
                "geometry": {
                    "srid": str(PROJECT_SRID),
                    "geometry": {"type": "Point", "coordinates": [382000.0, 6678000.0]},
                },
                "name": land_use_point_instance.name,
                "description": land_use_point_instance.description,
                "objectNumber": land_use_point_instance.ordering,
                "periodOfValidity": None,
            },
        ],
        # groups will not be in order by object, because we join all the group ids together to find
        # common groups across all objects:
        "planRegulationGroups": [
            {
                "planRegulationGroupKey": point_plan_regulation_group_instance.id,
                "titleOfPlanRegulation": point_plan_regulation_group_instance.name,
                "planRegulations": [
                    {
                        "planRegulationKey": point_text_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/asumisenAlue",
                        "value": {
                            "dataType": "LocalizedText",
                            "text": point_text_plan_regulation_instance.text_value,
                        },
                        "subjectIdentifiers": point_text_plan_regulation_instance.subject_identifiers,
                        "additionalInformations": [],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01"
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            point_text_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    }
                ],
                "planRecommendations": [],
                "letterIdentifier": point_plan_regulation_group_instance.short_name,
                "groupNumber": point_plan_regulation_group_instance.ordering,
                "colorNumber": "#FFFFFF",
            },
            {
                "planRegulationGroupKey": plan_regulation_group_instance.id,
                "titleOfPlanRegulation": plan_regulation_group_instance.name,
                "planRegulations": [
                    {
                        "planRegulationKey": empty_value_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/asumisenAlue",
                        "subjectIdentifiers": empty_value_plan_regulation_instance.subject_identifiers,
                        "additionalInformations": [
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/paakayttotarkoitus"
                            },
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/kayttotarkoituksenOsuusKerrosalastaK-m2",
                                "value": {
                                    "dataType": "PositiveNumeric",
                                    "number": 2500,
                                    "unitOfMeasure": "k-m2",
                                },
                            },
                        ],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01"
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            empty_value_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    },
                    {
                        "planRegulationKey": numeric_range_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/maanpaallinenKerroslukuArvovali",
                        "value": {
                            "dataType": "PositiveNumericRange",
                            "minimumValue": (
                                int(
                                    numeric_range_plan_regulation_instance.numeric_range_min
                                )
                                if numeric_range_plan_regulation_instance.numeric_range_min
                                else None
                            ),
                            "maximumValue": (
                                int(
                                    numeric_range_plan_regulation_instance.numeric_range_max
                                )
                                if numeric_range_plan_regulation_instance.numeric_range_max
                                else None
                            ),
                            # "unitOfMeasure": numeric_range_plan_regulation_instance.unit,  #  floor range does not have unit
                        },
                        "subjectIdentifiers": numeric_range_plan_regulation_instance.subject_identifiers,
                        "additionalInformations": [],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01"
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            numeric_range_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    },
                    {
                        "planRegulationKey": text_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/asumisenAlue",
                        "value": {
                            "dataType": "LocalizedText",
                            "text": text_plan_regulation_instance.text_value,
                        },
                        "subjectIdentifiers": text_plan_regulation_instance.subject_identifiers,
                        "additionalInformations": [
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/paakayttotarkoitus"
                            }
                        ],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01"
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(text_plan_regulation_instance.ordering),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    },
                    {
                        "planRegulationKey": verbal_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/sanallinenMaarays",
                        "value": {
                            "dataType": "LocalizedText",
                            "text": verbal_plan_regulation_instance.text_value,
                        },
                        "subjectIdentifiers": verbal_plan_regulation_instance.subject_identifiers,
                        "verbalRegulations": [
                            "http://uri.suomi.fi/codelist/rytj/RY_Sanallisen_Kaavamaarayksen_Laji/code/perustaminen"
                        ],
                        "additionalInformations": [],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01"
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            verbal_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    },
                ],
                "planRecommendations": [
                    {
                        "planRecommendationKey": plan_proposition_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "value": plan_proposition_instance.text_value,
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01"
                        ],
                        "recommendationNumber": plan_proposition_instance.ordering,
                        # TODO: plan recommendation documents to be added.
                        "periodOfValidity": None,
                    }
                ],
                "letterIdentifier": plan_regulation_group_instance.short_name,
                "groupNumber": plan_regulation_group_instance.ordering,
                "colorNumber": "#FFFFFF",
            },
            {
                "planRegulationGroupKey": numeric_plan_regulation_group_instance.id,
                "titleOfPlanRegulation": numeric_plan_regulation_group_instance.name,
                "planRegulations": [
                    {
                        "planRegulationKey": numeric_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/sallittuKerrosala",
                        "value": {
                            "dataType": "PositiveNumeric",
                            "number": (
                                int(numeric_plan_regulation_instance.numeric_value)
                                if numeric_plan_regulation_instance.numeric_value
                                else None
                            ),
                            "unitOfMeasure": numeric_plan_regulation_instance.unit,
                        },
                        "subjectIdentifiers": numeric_plan_regulation_instance.subject_identifiers,
                        "additionalInformations": [],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01"
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            numeric_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    }
                ],
                "planRecommendations": [],
                "letterIdentifier": numeric_plan_regulation_group_instance.short_name,
                "groupNumber": numeric_plan_regulation_group_instance.ordering,
                "colorNumber": "#FFFFFF",
            },
            {
                "planRegulationGroupKey": decimal_plan_regulation_group_instance.id,
                "titleOfPlanRegulation": decimal_plan_regulation_group_instance.name,
                "planRegulations": [
                    {
                        "planRegulationKey": decimal_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/maanpinnanKorkeusasema",
                        "value": {
                            "dataType": "Decimal",
                            "number": decimal_plan_regulation_instance.numeric_value,
                            "unitOfMeasure": decimal_plan_regulation_instance.unit,
                        },
                        "subjectIdentifiers": decimal_plan_regulation_instance.subject_identifiers,
                        "additionalInformations": [],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01"
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            decimal_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    }
                ],
                "planRecommendations": [],
                "letterIdentifier": decimal_plan_regulation_group_instance.short_name,
                "groupNumber": decimal_plan_regulation_group_instance.ordering,
                "colorNumber": "#FFFFFF",
            },
            {
                "planRegulationGroupKey": pedestrian_plan_regulation_group_instance.id,
                "titleOfPlanRegulation": pedestrian_plan_regulation_group_instance.name,
                "planRegulations": [
                    {
                        "planRegulationKey": pedestrian_street_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/katu",
                        "subjectIdentifiers": pedestrian_street_plan_regulation_instance.subject_identifiers,
                        "additionalInformations": [
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/paakayttotarkoitus"
                            },
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/kayttotarkoituskohdistus",
                                "value": {
                                    "dataType": "Code",
                                    "code": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/jalankulkualue",
                                    "codeList": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji",
                                    "title": {
                                        "eng": "Pedestrian area",
                                        "fin": "Jalankulkualue",
                                        "swe": "Fotgångarområde",
                                    },
                                },
                            },
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/kayttotarkoituskohdistus",
                                "value": {
                                    "dataType": "Code",
                                    "code": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/pyorailyalue",
                                    "codeList": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji",
                                    "title": {
                                        "eng": "Cycling area",
                                        "fin": "Pyöräilyalue",
                                        "swe": "Cykelområde",
                                    },
                                },
                            },
                        ],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01"
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            pedestrian_street_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    }
                ],
                "planRecommendations": [],
                "letterIdentifier": pedestrian_plan_regulation_group_instance.short_name,
                "groupNumber": pedestrian_plan_regulation_group_instance.ordering,
                "colorNumber": "#FFFFFF",
            },
            {
                "planRegulationGroupKey": construction_area_plan_regulation_group_instance.id,
                "titleOfPlanRegulation": construction_area_plan_regulation_group_instance.name,
                "planRegulations": [
                    {
                        "planRegulationKey": construction_area_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/rakennusala",
                        "subjectIdentifiers": construction_area_plan_regulation_instance.subject_identifiers,
                        "additionalInformations": [
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/osaAlue"
                            }
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            construction_area_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    }
                ],
                "planRecommendations": [],
                "letterIdentifier": construction_area_plan_regulation_group_instance.short_name,
                "groupNumber": construction_area_plan_regulation_group_instance.ordering,
                "colorNumber": "#FFFFFF",
            },
        ],
        "planRegulationGroupRelations": [
            {
                "planObjectKey": land_use_area_instance.id,
                "planRegulationGroupKey": numeric_plan_regulation_group_instance.id,
            },
            {
                "planObjectKey": land_use_area_instance.id,
                "planRegulationGroupKey": decimal_plan_regulation_group_instance.id,
            },
            {
                "planObjectKey": land_use_area_instance.id,
                "planRegulationGroupKey": plan_regulation_group_instance.id,
            },
            {
                "planObjectKey": other_area_instance.id,
                "planRegulationGroupKey": construction_area_plan_regulation_group_instance.id,
            },
            {
                "planObjectKey": pedestrian_street_instance.id,
                "planRegulationGroupKey": pedestrian_plan_regulation_group_instance.id,
            },
            {
                "planObjectKey": land_use_point_instance.id,
                "planRegulationGroupKey": point_plan_regulation_group_instance.id,
            },
        ],
    }


@pytest.fixture
def another_plan_dict(another_plan_instance: models.Plan) -> dict:
    """Minimal invalid plan dict with no related objects."""
    return {
        "planKey": another_plan_instance.id,
        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
        "legalEffectOfLocalMasterPlans": None,
        "scale": another_plan_instance.scale,
        "geographicalArea": {
            "srid": str(PROJECT_SRID),
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [381849.834412134019658, 6677967.973336197435856],
                        [381849.834412134019658, 6680613.389312859624624],
                        [386378.427863708813675, 6680613.389312859624624],
                        [386378.427863708813675, 6677967.973336197435856],
                        [381849.834412134019658, 6677967.973336197435856],
                    ]
                ],
            },
        },
        # TODO: plan documents to be added.
        "periodOfValidity": None,
        "approvalDate": None,
        "generalRegulationGroups": [],
        "planDescription": (
            another_plan_instance.description["fin"]
            if another_plan_instance.description
            else None
        ),  # TODO: should this be a single language string? why?
        "planObjects": [],
        "planRegulationGroups": [],
        "planRegulationGroupRelations": [],
        "planMaps": [],
        "planAnnexes": [],
        "otherPlanMaterials": [],
        "planReport": None,
    }


@pytest.fixture
def desired_plan_matter_dict(
    desired_plan_dict: dict, complete_test_plan: models.Plan
) -> dict:
    """Plan matter dict based on https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Palveluväylä/Kaavoitus%20OpenApi.json

    Constructing the plan matter requires certain additional codes to be present in the database and set in the plan instance.

    Let's 1) write explicitly the complex fields, and 2) just check that the simple fields have
    the same values as the original plan fixture in the database.
    """
    return {
        "permanentPlanIdentifier": "MK-123456",
        "planType": "http://uri.suomi.fi/codelist/rytj/RY_Kaavalaji/code/11",
        "name": complete_test_plan.name,
        "timeOfInitiation": "2024-01-01",
        "description": complete_test_plan.description,
        "producerPlanIdentifier": complete_test_plan.producers_plan_identifier,
        "caseIdentifiers": [],
        "recordNumbers": [],
        "administrativeAreaIdentifiers": ["01"],
        "digitalOrigin": "http://uri.suomi.fi/codelist/rytj/RY_DigitaalinenAlkupera/code/01",
        "planMatterPhases": [
            {
                "planMatterPhaseKey": "third_phase_test",
                "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                "geographicalArea": desired_plan_dict["geographicalArea"],
                "handlingEvent": {
                    "handlingEventKey": "whatever",
                    "handlingEventType": "http://uri.suomi.fi/codelist/rytj/kaavakastap/code/05",
                    "eventTime": "2024-02-15",
                    "cancelled": False,
                },
                "interactionEvents": [
                    {
                        "interactionEventKey": "whatever",
                        "interactionEventType": "http://uri.suomi.fi/codelist/rytj/RY_KaavanVuorovaikutustapahtumanLaji/code/01",
                        "eventTime": {
                            "begin": "2024-02-14T22:00:00Z",
                            "end": "2024-02-27T22:00:00Z",
                        },
                    }
                ],
                "planDecision": {
                    "planDecisionKey": "whatever",
                    "name": "http://uri.suomi.fi/codelist/rytj/kaavpaatnimi/code/04",
                    "decisionDate": "2024-02-05",
                    "dateOfDecision": "2024-02-05",
                    "typeOfDecisionMaker": "http://uri.suomi.fi/codelist/rytj/PaatoksenTekija/code/01",
                    "plans": [
                        {
                            # Documents must be added to the valid plan inside plan matter
                            **desired_plan_dict,
                            "planMaps": [
                                {
                                    "planMapKey": "whatever",
                                    "name": {"fin": "Kaavakartta"},
                                    "fileKey": "whatever else",
                                    "coordinateSystem": "http://uri.suomi.fi/codelist/rakrek/ETRS89/code/EPSG3067",
                                }
                            ],
                            "planAnnexes": [
                                {
                                    "attachmentDocumentKey": "whatever",
                                    "name": {
                                        "fin": "Osallistumis- ja arviointisuunnitelma"
                                    },
                                    "fileKey": "whatever else",
                                    "documentIdentifier": "HEL 2024-016009",
                                    "personalDataContent": "http://uri.suomi.fi/codelist/rytj/henkilotietosisalto/code/1",
                                    "categoryOfPublicity": "http://uri.suomi.fi/codelist/rytj/julkisuus/code/1",
                                    "retentionTime": "http://uri.suomi.fi/codelist/rytj/sailytysaika/code/01",
                                    "languages": [
                                        "http://uri.suomi.fi/codelist/rytj/ryhtikielet/code/fi"
                                    ],
                                    "accessibility": False,
                                    "documentDate": "2024-01-01",
                                    "typeOfAttachment": "http://uri.suomi.fi/codelist/rytj/RY_AsiakirjanLaji_YKAK/code/14",
                                }
                            ],
                            "planReport": {
                                "planReportKey": "whatever",
                                "attachmentDocuments": [
                                    {
                                        "attachmentDocumentKey": "whatever",
                                        "name": {"fin": "Kaavaselostus"},
                                        "fileKey": "whatever else",
                                        "documentIdentifier": "HEL 2024-016009",
                                        "personalDataContent": "http://uri.suomi.fi/codelist/rytj/henkilotietosisalto/code/1",
                                        "categoryOfPublicity": "http://uri.suomi.fi/codelist/rytj/julkisuus/code/1",
                                        "retentionTime": "http://uri.suomi.fi/codelist/rytj/sailytysaika/code/01",
                                        "languages": [
                                            "http://uri.suomi.fi/codelist/rytj/ryhtikielet/code/fi"
                                        ],
                                        "accessibility": False,
                                        "documentDate": "2024-01-01",
                                        "typeOfAttachment": "http://uri.suomi.fi/codelist/rytj/RY_AsiakirjanLaji_YKAK/code/06",
                                    }
                                ],
                            },
                            "otherPlanMaterials": [
                                {
                                    "otherPlanMaterialKey": "whatever",
                                    "name": {"fin": "Muu asiakirja"},
                                    "fileKey": "whatever else",
                                    "personalDataContent": "http://uri.suomi.fi/codelist/rytj/henkilotietosisalto/code/1",
                                    "categoryOfPublicity": "http://uri.suomi.fi/codelist/rytj/julkisuus/code/1",
                                }
                            ],
                        }
                    ],
                },
            }
        ],
        # TODO: source data etc. non-mandatory fields to be added
    }


def assert_lists_equal(
    list1: list,
    list2: list,
    ignore_keys: list | None = None,
    ignore_order_for_keys: list | None = None,
    ignore_list_order: bool | None = False,
    path: str = "",
) -> None:
    assert len(list1) == len(list2), f"Lists differ in length in path {path}"
    for i, item1 in enumerate(list1):
        current_path = f"{path}[{i}]" if path else f"[{i}]"
        items_to_compare = list2 if ignore_list_order else [list2[i]]
        deepest_error = AssertionError()
        error_depth = 0
        for item2 in items_to_compare:
            try:
                deepcompare(
                    item1,
                    item2,
                    ignore_keys=ignore_keys,
                    ignore_order_for_keys=ignore_order_for_keys,
                    path=current_path,
                )
            except AssertionError as error:
                # Now this is a hack if I ever saw one:
                depth = str(error).count(".") + str(error).count("[")
                if depth > error_depth:
                    deepest_error = error
                    error_depth = depth
                continue
            else:
                break
        else:
            raise deepest_error


def assert_dicts_equal(
    dict1: Mapping,
    dict2: Mapping,
    ignore_keys: list | None = None,
    ignore_order_for_keys: list | None = None,
    path: str = "",
) -> None:
    assert len(dict1) == len(dict2), (
        f"Dicts differ in length in {path}. Dict1 keys: {dict1.keys()}. Dict2 keys: {dict2.keys()}"
    )
    for key in dict2:
        if not ignore_keys or key not in ignore_keys:
            assert key in dict1, f"Key {key} missing in {path}"
    for key, value in dict1.items():
        current_path = f"{path}.{key}" if path else key
        if not ignore_keys or key not in ignore_keys:
            deepcompare(
                dict2[key],
                value,
                ignore_keys=ignore_keys,
                ignore_order_for_keys=ignore_order_for_keys,
                ignore_list_order=(
                    key in ignore_order_for_keys if ignore_order_for_keys else False
                ),
                path=current_path,
            )


def deepcompare(
    item1: object,
    item2: object,
    ignore_keys: list | None = None,
    ignore_order_for_keys: list | None = None,
    ignore_list_order: bool | None = False,
    path: str = "",
) -> None:
    """Recursively check that dicts and lists in two items have the same items (type and value)
    in the same order.

    Optionally, certain keys (e.g. random UUIDs set by the database, our script or
    the remote Ryhti API) can be ignored when comparing dicts in the lists, because
    they are not provided in the incoming data. Also, order of lists under certain keys
    in dicts may be ignored, or order of this list itself may be ignored.
    """
    assert type(item1) is type(item2), f"Item types differ at {path}"
    if isinstance(item1, dict) and isinstance(item2, dict):
        assert_dicts_equal(
            item1,
            item2,
            ignore_keys=ignore_keys,
            ignore_order_for_keys=ignore_order_for_keys,
            path=path,
        )
    elif isinstance(item1, list) and isinstance(item2, list):
        assert_lists_equal(
            item1,
            item2,
            ignore_keys=ignore_keys,
            ignore_order_for_keys=ignore_order_for_keys,
            ignore_list_order=ignore_list_order,
            path=path,
        )
    else:
        assert item1 == item2, f"Items differ at {path}"
