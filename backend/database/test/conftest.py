import os
import time
import timeit
from datetime import datetime
from pathlib import Path

import codes
import models
import psycopg2
import pytest
import sqlalchemy
from alembic import command
from alembic.config import Config
from alembic.operations import ops
from alembic.script import ScriptDirectory
from base import PROJECT_SRID
from db_helper import DatabaseHelper
from db_manager import db_manager
from dotenv import load_dotenv
from geoalchemy2.shape import from_shape
from shapely.geometry import MultiPolygon
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.orm import Session, sessionmaker

hame_count: int = 13  # adjust me when adding tables
codes_count: int = 11  # adjust me when adding tables
matview_count: int = 0  # adjust me when adding views

USE_DOCKER = (
    "1"  # Use "" if you don't want pytest-docker to start and destroy the containers
)
SCHEMA_FILES_PATH = Path(".")


@pytest.fixture(scope="session", autouse=True)
def set_env():
    dotenv_file = Path(__file__).parent.parent.parent / ".env"
    assert dotenv_file.exists()
    load_dotenv(str(dotenv_file))
    db_manager.SCHEMA_FILES_PATH = str(Path(__file__).parent.parent)


@pytest.fixture(scope="session")
def root_db_params():
    return {
        "dbname": os.environ.get("DB_MAINTENANCE_NAME", ""),
        "user": os.environ.get("SU_USER", ""),
        "host": os.environ.get("DB_INSTANCE_ADDRESS", ""),
        "password": os.environ.get("SU_USER_PW", ""),
        "port": os.environ.get("DB_INSTANCE_PORT", ""),
    }


@pytest.fixture(scope="session")
def main_db_params():
    return {
        "dbname": os.environ.get("DB_MAIN_NAME", ""),
        "user": os.environ.get("RW_USER", ""),
        "host": os.environ.get("DB_INSTANCE_ADDRESS", ""),
        "password": os.environ.get("RW_USER_PW", ""),
        "port": os.environ.get("DB_INSTANCE_PORT", ""),
    }


@pytest.fixture(scope="session")
def main_db_params_with_root_user():
    return {
        "dbname": os.environ.get("DB_MAIN_NAME", ""),
        "user": os.environ.get("SU_USER", ""),
        "host": os.environ.get("DB_INSTANCE_ADDRESS", ""),
        "password": os.environ.get("SU_USER_PW", ""),
        "port": os.environ.get("DB_INSTANCE_PORT", ""),
    }


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    compose_file = Path(__file__).parent.parent.parent / "docker-compose.dev.yml"
    assert compose_file.exists()
    return str(compose_file)


if os.environ.get("MANAGE_DOCKER", USE_DOCKER):

    @pytest.fixture(scope="session", autouse=True)
    def wait_for_services(docker_services, main_db_params, root_db_params):
        def is_responsive(params):
            succeeds = False
            try:
                with psycopg2.connect(**root_db_params):
                    succeeds = True
            except psycopg2.OperationalError:
                pass
            return succeeds

        wait_until_responsive(
            timeout=20, pause=0.5, check=lambda: is_responsive(root_db_params)
        )
        drop_hame_db(main_db_params, root_db_params)

else:

    @pytest.fixture(scope="session", autouse=True)
    def wait_for_services(main_db_params, root_db_params):
        wait_until_responsive(
            timeout=20, pause=0.5, check=lambda: is_responsive(root_db_params)
        )
        drop_hame_db(main_db_params, root_db_params)


@pytest.fixture(scope="session")
def alembic_cfg():
    return Config(Path(SCHEMA_FILES_PATH, "alembic.ini"))


@pytest.fixture(scope="session")
def current_head_version_id(alembic_cfg):
    script_dir = ScriptDirectory.from_config(alembic_cfg)
    return script_dir.get_current_head()


@pytest.fixture(scope="module")
def hame_database_created(root_db_params, main_db_params, current_head_version_id):
    event = {"event_type": 1}
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    yield current_head_version_id

    drop_hame_db(main_db_params, root_db_params)


@pytest.fixture()
def hame_database_migrated(root_db_params, main_db_params, current_head_version_id):
    event = {"event_type": 3}
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    yield current_head_version_id

    drop_hame_db(main_db_params, root_db_params)


@pytest.fixture()
def hame_database_migrated_down(hame_database_migrated):
    event = {"event_type": 3, "version": "base"}
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    yield "base"


def process_revision_directives_remove_empty(context, revision, directives):
    # remove migration if it is empty
    script = directives[0]
    if script.upgrade_ops.is_empty():
        directives[:] = []


def process_revision_directives_add_table(context, revision, directives):
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
            ],
        ),
        ops.DowngradeOps(
            ops=[ops.DropTableOp("test_table", schema="hame")],
        ),
    )


@pytest.fixture()
def autogenerated_migration(
    alembic_cfg, hame_database_migrated, current_head_version_id
):
    revision = command.revision(
        alembic_cfg,
        message="Test migration",
        head=current_head_version_id,
        autogenerate=True,
        process_revision_directives=process_revision_directives_remove_empty,
    )
    path = Path(revision.path) if revision else None
    yield path
    if path:
        path.unlink()


@pytest.fixture()
def new_migration(alembic_cfg, hame_database_migrated, current_head_version_id):
    revision = command.revision(
        alembic_cfg,
        message="Test migration",
        head=current_head_version_id,
        autogenerate=True,
        process_revision_directives=process_revision_directives_add_table,
    )
    path = Path(revision.path)
    assert path.is_file()
    new_head_version_id = revision.revision
    yield new_head_version_id
    path.unlink()


@pytest.fixture()
def hame_database_upgraded(new_migration):
    event = {"event_type": 3}
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    yield new_migration


@pytest.fixture()
def hame_database_downgraded(hame_database_upgraded, current_head_version_id):
    event = {"event_type": 3, "version": current_head_version_id}
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    yield current_head_version_id


def drop_hame_db(main_db_params, root_db_params):
    conn = psycopg2.connect(**root_db_params)
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                f"DROP DATABASE IF EXISTS {main_db_params['dbname']} WITH (FORCE)"
            )
            for user in os.environ.get("DB_USERS").split(","):
                cur.execute(f"DROP ROLE IF EXISTS {user}")
    finally:
        conn.close()


def wait_until_responsive(check, timeout, pause, clock=timeit.default_timer):
    """
    Wait until a service is responsive.
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
        with psycopg2.connect(**params):
            succeeds = True
    except psycopg2.OperationalError:
        pass
    return succeeds


def assert_database_is_alright(
    cur: psycopg2.extensions.cursor,
    expected_hame_count: int = hame_count,
    expected_codes_count: int = codes_count,
    expected_matview_count: int = matview_count,
):
    """
    Checks that the database has the right amount of tables with the right
    permissions.
    """
    # Check schemas
    cur.execute(
        "SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('hame', 'codes') ORDER BY schema_name DESC"  # noqa
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
            f"SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_schema = 'hame' AND table_name='{table_name}';"  # noqa
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
            f"SELECT * FROM pg_indexes WHERE schemaname = 'hame' AND tablename = '{table_name}';"  # noqa
        )
        indexes = cur.fetchall()
        cur.execute(
            f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'hame' AND table_name = '{table_name}';"  # noqa
        )
        columns = cur.fetchall()
        if ("id",) in columns:
            assert (
                "hame",
                table_name,
                f"{table_name}_pkey",
                None,
                f"CREATE UNIQUE INDEX {table_name}_pkey ON hame.{table_name} USING btree (id)",  # noqa
            ) in indexes
        if ("geom",) in columns:
            assert (
                "hame",
                table_name,
                f"idx_{table_name}_geom",
                None,
                f"CREATE INDEX idx_{table_name}_geom ON hame.{table_name} USING gist (geom)",  # noqa
            ) in indexes
        if ("ordering",) in columns:
            assert (
                "hame",
                table_name,
                f"ix_hame_{table_name}_ordering",
                None,
                f"CREATE INDEX ix_hame_{table_name}_ordering ON hame.{table_name} USING btree (ordering)",  # noqa
            ) in indexes

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
            f"SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_schema = 'codes' AND table_name='{table_name}';"  # noqa
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
            f"SELECT * FROM pg_indexes WHERE schemaname = 'codes' AND tablename = '{table_name}';"  # noqa
        )
        indexes = cur.fetchall()
        assert (
            "codes",
            table_name,
            f"{table_name}_pkey",
            None,
            f"CREATE UNIQUE INDEX {table_name}_pkey ON codes.{table_name} USING btree (id)",  # noqa
        ) in indexes
        assert (
            "codes",
            table_name,
            f"ix_codes_{table_name}_level",
            None,
            f"CREATE INDEX ix_codes_{table_name}_level ON codes.{table_name} USING btree (level)",  # noqa
        ) in indexes
        assert (
            "codes",
            table_name,
            f"ix_codes_{table_name}_parent_id",
            None,
            f"CREATE INDEX ix_codes_{table_name}_parent_id ON codes.{table_name} USING btree (parent_id)",  # noqa
        ) in indexes
        assert (
            "codes",
            table_name,
            f"ix_codes_{table_name}_short_name",
            None,
            f"CREATE INDEX ix_codes_{table_name}_short_name ON codes.{table_name} USING btree (short_name)",  # noqa
        ) in indexes
        assert (
            "codes",
            table_name,
            f"ix_codes_{table_name}_value",
            None,
            f"CREATE UNIQUE INDEX ix_codes_{table_name}_value ON codes.{table_name} USING btree (value)",  # noqa
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
def connection_string(hame_database_created) -> str:
    return DatabaseHelper().get_connection_string()


@pytest.fixture(scope="module")
def session(connection_string):
    engine = sqlalchemy.create_engine(connection_string)
    session = sessionmaker(bind=engine)
    yield session()


@pytest.fixture(scope="module")
def code_instance(session):
    instance = codes.LifeCycleStatus(value="test", status="LOCAL")
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def another_code_instance(session):
    instance = codes.LifeCycleStatus(value="test2", status="LOCAL")
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def plan_type_instance(session):
    instance = codes.PlanType(value="test", status="LOCAL")
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def type_of_underground_instance(session):
    instance = codes.TypeOfUnderground(value="test", status="LOCAL")
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def type_of_plan_regulation_group_instance(session):
    instance = codes.TypeOfPlanRegulationGroup(value="test", status="LOCAL")
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def type_of_plan_regulation_instance(session):
    instance = codes.TypeOfPlanRegulation(value="test", status="LOCAL")
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def type_of_verbal_plan_regulation_instance(session):
    instance = codes.TypeOfVerbalPlanRegulation(value="test", status="LOCAL")
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def type_of_additional_information_instance(session):
    instance = codes.TypeOfAdditionalInformation(value="test", status="LOCAL")
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def type_of_source_data_instance(session):
    instance = codes.TypeOfSourceData(value="test", status="LOCAL")
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def type_of_document_instance(session):
    instance = codes.TypeOfDocument(value="test", status="LOCAL")
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def administrative_region_instance(session):
    instance = codes.AdministrativeRegion(value="test", status="LOCAL")
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def plan_theme_instance(session):
    instance = codes.PlanTheme(value="test", status="LOCAL")
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def plan_instance(session, code_instance, organisation_instance, plan_type_instance):
    instance = models.Plan(
        geom=from_shape(
            MultiPolygon(
                [(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),)]
            ),
            srid=PROJECT_SRID,
            extended=True,
        ),
        scale=1,
        description={"fin": "test_plan"},
        lifecycle_status=code_instance,
        organisation=organisation_instance,
        plan_type=plan_type_instance,
    )
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def organisation_instance(session, administrative_region_instance):
    instance = models.Organisation(
        business_id="test", administrative_region=administrative_region_instance
    )
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def land_use_area_instance(
    session,
    code_instance,
    type_of_underground_instance,
    plan_instance,
    plan_regulation_group_instance,
):
    instance = models.LandUseArea(
        geom=from_shape(
            MultiPolygon(
                [(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),)]
            ),
            srid=PROJECT_SRID,
            extended=True,
        ),
        height_range=Range(0.0, 1.0),
        height_unit="m",
        lifecycle_status=code_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
        plan_regulation_group=plan_regulation_group_instance,
    )
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def plan_regulation_group_instance(session, type_of_plan_regulation_group_instance):
    instance = models.PlanRegulationGroup(
        short_name="K",
        type_of_plan_regulation_group=type_of_plan_regulation_group_instance,
    )
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def plan_regulation_instance(
    session,
    code_instance,
    type_of_plan_regulation_instance,
    plan_regulation_group_instance,
):
    instance = models.PlanRegulation(
        name={"fin": "test_regulation"},
        numeric_value=1.0,
        unit="m",
        lifecycle_status=code_instance,
        type_of_plan_regulation=type_of_plan_regulation_instance,
        plan_regulation_group=plan_regulation_group_instance,
    )
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def plan_proposition_instance(session, code_instance, plan_regulation_group_instance):
    instance = models.PlanProposition(
        lifecycle_status=code_instance,
        plan_regulation_group=plan_regulation_group_instance,
    )
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def source_data_instance(session):
    instance = models.SourceData(
        additional_information_uri="http://test.fi", detachment_date=datetime.now()
    )
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def document_instance(session, type_of_document_instance, plan_instance):
    instance = models.Document(
        name="Testidokumentti",
        type_of_document=type_of_document_instance,
        personal_details="Testihenkilö",
        publicity="julkinen",
        language="fin",
        decision=False,
        plan=plan_instance,
    )
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def lifecycle_date_instance(session, code_instance):
    instance = models.LifeCycleDate(lifecycle_status=code_instance)
    session.add(instance)
    return instance


@pytest.fixture(scope="module")
def complete_test_plan(
    session: Session,
    plan_instance: models.Plan,
    land_use_area_instance: models.LandUseArea,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    plan_theme_instance: codes.PlanTheme,
    type_of_verbal_plan_regulation_instance: codes.TypeOfVerbalPlanRegulation,
    type_of_additional_information_instance: codes.TypeOfAdditionalInformation,
) -> models.Plan:
    """
    Plan data that might be more or less complete, to be tested and validated with the
    Ryhti API.
    """
    # Add the optional (nullable) relationships. We don't want them to be present in
    # all fixtures.
    plan_regulation_instance.plan_theme = plan_theme_instance
    plan_regulation_instance.type_of_verbal_plan_regulation = (
        type_of_verbal_plan_regulation_instance
    )
    plan_regulation_instance.intended_use = type_of_additional_information_instance
    plan_proposition_instance.plan_theme = plan_theme_instance
    session.commit()
    return plan_instance
