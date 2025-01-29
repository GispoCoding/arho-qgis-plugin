import os
import time
import timeit
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, List, Mapping, Optional
from zoneinfo import ZoneInfo

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
from db_helper import DatabaseHelper, User
from db_manager import db_manager
from dotenv import load_dotenv
from enums import AttributeValueDataType
from geoalchemy2.shape import from_shape
from shapely.geometry import MultiLineString, MultiPoint, shape
from sqlalchemy.orm import Session, sessionmaker

hame_count: int = 16  # adjust me when adding tables
codes_count: int = 21  # adjust me when adding tables
matview_count: int = 0  # adjust me when adding views


USE_DOCKER = (
    "1"  # Use "" if you don't want pytest-docker to start and destroy the containers
)
SCHEMA_FILES_PATH = Path(".")
LOCAL_TZ = ZoneInfo("Europe/Helsinki")


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
    event = {"action": "create_db"}
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    yield current_head_version_id

    drop_hame_db(main_db_params, root_db_params)


@pytest.fixture()
def hame_database_migrated(root_db_params, main_db_params, current_head_version_id):
    event = {"action": "migrate_db"}
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    yield current_head_version_id

    drop_hame_db(main_db_params, root_db_params)


@pytest.fixture()
def hame_database_migrated_down(hame_database_migrated):
    event = {"action": "migrate_db", "version": "base"}
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
    event = {"action": "migrate_db"}
    response = db_manager.handler(event, None)
    assert response["statusCode"] == 200, response["body"]
    yield new_migration


@pytest.fixture()
def hame_database_downgraded(hame_database_upgraded, current_head_version_id):
    event = {"action": "migrate_db", "version": current_head_version_id}
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
def admin_connection_string(hame_database_created) -> str:
    return DatabaseHelper(user=User.ADMIN).get_connection_string()


@pytest.fixture(scope="module")
def rw_connection_string(hame_database_created) -> str:
    return DatabaseHelper(user=User.READ_WRITE).get_connection_string()


@pytest.fixture(scope="module")
def session(admin_connection_string):
    engine = sqlalchemy.create_engine(admin_connection_string)
    session = sessionmaker(bind=engine)
    yield session()


@pytest.fixture
def rollback_after(session: Session):
    yield
    session.rollback()


@pytest.fixture()
def code_instance(session):
    instance = codes.LifeCycleStatus(value="test", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def another_code_instance(session):
    instance = codes.LifeCycleStatus(value="test2", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def preparation_status_instance(session):
    instance = codes.LifeCycleStatus(value="03", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def plan_proposal_status_instance(session):
    instance = codes.LifeCycleStatus(value="04", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def plan_type_instance(session):
    # Let's use real code to allow testing API endpoints that require this
    # code value as parameter
    # https://koodistot.suomi.fi/codescheme;registryCode=rytj;schemeCode=RY_Kaavalaji
    # 11: Kokonaismaakuntakaava
    instance = codes.PlanType(value="11", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def type_of_underground_instance(session):
    instance = codes.TypeOfUnderground(value="01", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def type_of_plan_regulation_group_instance(session):
    instance = codes.TypeOfPlanRegulationGroup(value="test", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def type_of_general_plan_regulation_group_instance(session):
    instance = codes.TypeOfPlanRegulationGroup(
        value="generalRegulations", status="LOCAL"
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def type_of_plan_regulation_instance(session):
    instance = codes.TypeOfPlanRegulation(value="asumisenAlue", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def type_of_plan_regulation_allowed_area_instance(session):
    instance = codes.TypeOfPlanRegulation(value="sallittuKerrosala", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def type_of_plan_regulation_number_of_stories_instance(session):
    instance = codes.TypeOfPlanRegulation(
        value="maanpaallinenKerroslukuArvovali", status="LOCAL"
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def type_of_plan_regulation_verbal_instance(session):
    instance = codes.TypeOfPlanRegulation(value="sanallinenMaarays", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def type_of_verbal_plan_regulation_instance(session):
    instance = codes.TypeOfVerbalPlanRegulation(value="perustaminen", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def type_of_main_use_additional_information_instance(session):
    instance = codes.TypeOfAdditionalInformation(
        value="paakayttotarkoitus", status="LOCAL"
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def type_of_source_data_instance(session):
    instance = codes.TypeOfSourceData(value="test", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def type_of_document_plan_map_instance(session):
    instance = codes.TypeOfDocument(value="03", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def category_of_publicity_public_instance(session):
    instance = codes.CategoryOfPublicity(value="1", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def personal_data_content_no_personal_data_instance(session):
    instance = codes.PersonalDataContent(value="1", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def retention_time_permanent_instance(session):
    instance = codes.RetentionTime(value="01", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def language_finnish_instance(session):
    instance = codes.Language(value="fi", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def municipality_instance(session):
    instance = codes.Municipality(value="577", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def administrative_region_instance(session):
    instance = codes.AdministrativeRegion(value="01", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def another_administrative_region_instance(session):
    instance = codes.AdministrativeRegion(value="02", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def plan_theme_instance(session):
    instance = codes.PlanTheme(value="01", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def plan_instance(
    session,
    code_instance,
    another_code_instance,
    preparation_status_instance,
    plan_proposal_status_instance,
    organisation_instance,
    another_organisation_instance,
    plan_type_instance,
):
    # Any status and organisation instances that may be added to the plan later
    # have to be included above. If they are only created later, they will be torn
    # down too early and teardown will fail, because plan cannot have empty
    # status or organisation.
    instance = models.Plan(
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
        to_be_exported=True,
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def another_plan_instance(
    session,
    code_instance,
    another_code_instance,
    preparation_status_instance,
    plan_proposal_status_instance,
    organisation_instance,
    another_organisation_instance,
    plan_type_instance,
):
    # Any status and organisation instances that may be added to the plan later
    # have to be included above. If they are only created later, they will be torn
    # down too early and teardown will fail, because plan cannot have empty
    # status or organisation.
    instance = models.Plan(
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
        to_be_exported=True,
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def organisation_instance(session, administrative_region_instance):
    instance = models.Organisation(
        business_id="test", administrative_region=administrative_region_instance
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def another_organisation_instance(session, another_administrative_region_instance):
    instance = models.Organisation(
        business_id="other-test",
        administrative_region=another_administrative_region_instance,
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def land_use_area_instance(
    session,
    preparation_status_instance,
    type_of_underground_instance,
    plan_instance,
    plan_regulation_group_instance,
    numeric_plan_regulation_group_instance,
):
    instance = models.LandUseArea(
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
        name={"fin": "test_land_use_area"},
        description={"fin": "test_land_use_area"},
        height_min=0.0,
        height_max=1.0,
        height_unit="m",
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
        plan_regulation_groups=[
            plan_regulation_group_instance,
            numeric_plan_regulation_group_instance,
        ],
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def other_area_instance(
    session,
    preparation_status_instance,
    type_of_underground_instance,
    plan_instance,
    plan_regulation_group_instance,
):
    instance = models.OtherArea(
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
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def line_instance(
    session,
    preparation_status_instance,
    type_of_underground_instance,
    plan_instance,
    plan_regulation_group_instance,
):
    instance = models.Line(
        geom=from_shape(
            MultiLineString(
                [
                    [[382000, 6678000], [383000, 6678000]],
                ]
            )
        ),
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
        plan_regulation_groups=[plan_regulation_group_instance],
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def land_use_point_instance(
    session,
    preparation_status_instance,
    type_of_underground_instance,
    plan_instance,
    point_plan_regulation_group_instance,
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
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def other_point_instance(
    session,
    preparation_status_instance,
    type_of_underground_instance,
    plan_instance,
    point_plan_regulation_group_instance,
):
    instance = models.OtherPoint(
        geom=from_shape(MultiPoint([[382000, 6678000], [383000, 6678000]])),
        lifecycle_status=preparation_status_instance,
        type_of_underground=type_of_underground_instance,
        plan=plan_instance,
        plan_regulation_groups=[point_plan_regulation_group_instance],
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def plan_regulation_group_instance(
    session, plan_instance, type_of_plan_regulation_group_instance
):
    instance = models.PlanRegulationGroup(
        short_name="K",
        plan=plan_instance,
        ordering=2,
        type_of_plan_regulation_group=type_of_plan_regulation_group_instance,
        name={"fin": "test_plan_regulation_group"},
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


# Multiple numerical/decimal regulations cannot be in the same plan regulation group.
# Therefore, these plan regulations require their own groups.
@pytest.fixture(scope="function")
def numeric_plan_regulation_group_instance(
    session, plan_instance, type_of_plan_regulation_group_instance
):
    instance = models.PlanRegulationGroup(
        short_name="N",
        plan=plan_instance,
        ordering=3,
        type_of_plan_regulation_group=type_of_plan_regulation_group_instance,
        name={"fin": "test_numeric_plan_regulation_group"},
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def point_plan_regulation_group_instance(
    session, plan_instance, type_of_plan_regulation_group_instance
):
    instance = models.PlanRegulationGroup(
        short_name="L",
        plan=plan_instance,
        ordering=1,
        type_of_plan_regulation_group=type_of_plan_regulation_group_instance,
        name={"fin": "test_point_plan_regulation_group"},
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def general_regulation_group_instance(
    session, plan_instance, type_of_general_plan_regulation_group_instance
):
    instance = models.PlanRegulationGroup(
        short_name="Y",
        plan=plan_instance,
        ordering=1,
        type_of_plan_regulation_group=type_of_general_plan_regulation_group_instance,
        name={"fin": "test_general_regulation_group"},
    )
    session.add(instance)
    plan_instance.general_plan_regulation_groups.append(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def empty_value_plan_regulation_instance(
    session,
    preparation_status_instance,
    type_of_plan_regulation_instance,
    plan_regulation_group_instance,
):
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_instance,
        plan_regulation_group=plan_regulation_group_instance,
        ordering=1,
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def numeric_plan_regulation_instance(
    session,
    preparation_status_instance,
    type_of_plan_regulation_allowed_area_instance,
    numeric_plan_regulation_group_instance,
):
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
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def numeric_range_plan_regulation_instance(
    session,
    preparation_status_instance,
    type_of_plan_regulation_number_of_stories_instance,
    plan_regulation_group_instance,
):
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
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def text_plan_regulation_instance(
    session,
    preparation_status_instance,
    type_of_plan_regulation_instance,
    plan_regulation_group_instance,
):
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
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def point_text_plan_regulation_instance(
    session,
    preparation_status_instance,
    type_of_plan_regulation_instance,
    point_plan_regulation_group_instance,
):
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        value_data_type=AttributeValueDataType.LOCALIZED_TEXT,
        text_value={"fin": "test_value"},
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_instance,
        plan_regulation_group=point_plan_regulation_group_instance,
        ordering=1,
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def verbal_plan_regulation_instance(
    session,
    preparation_status_instance,
    type_of_plan_regulation_verbal_instance,
    type_of_verbal_plan_regulation_instance,
    plan_regulation_group_instance,
):
    """
    Looks like verbal plan regulations have to be serialized differently, type of
    verbal plan regulation is not allowed in other plan regulations. No idea how
    they differ from text regulations otherwise, though.
    """
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        value_data_type=AttributeValueDataType.LOCALIZED_TEXT,
        text_value={"fin": "test_value"},
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_verbal_instance,
        type_of_verbal_plan_regulation=type_of_verbal_plan_regulation_instance,
        plan_regulation_group=plan_regulation_group_instance,
        ordering=5,
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def general_plan_regulation_instance(
    session,
    preparation_status_instance,
    type_of_plan_regulation_instance,
    general_regulation_group_instance,
):
    instance = models.PlanRegulation(
        subject_identifiers=["#test_regulation"],
        value_data_type=AttributeValueDataType.LOCALIZED_TEXT,
        text_value={"fin": "test_value"},
        lifecycle_status=preparation_status_instance,
        type_of_plan_regulation=type_of_plan_regulation_instance,
        plan_regulation_group=general_regulation_group_instance,
        ordering=1,
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def plan_proposition_instance(
    session, preparation_status_instance, plan_regulation_group_instance
):
    instance = models.PlanProposition(
        lifecycle_status=preparation_status_instance,
        plan_regulation_group=plan_regulation_group_instance,
        text_value={"fin": "test_recommendation"},
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def source_data_instance(session, plan_instance, type_of_source_data_instance):
    instance = models.SourceData(
        additional_information_uri="http://test.fi",
        detachment_date=datetime.now(tz=LOCAL_TZ),
        plan=plan_instance,
        type_of_source_data=type_of_source_data_instance,
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


# @pytest.fixture(scope="function")
# def document_instance(
#     session, type_of_document_instance, category_of_publicity_instance, plan_instance
# ):
#     instance = models.Document(
#         name="Testidokumentti",
#         type_of_document=type_of_document_instance,
#         personal_details="Testihenkilö",
#         publicity=category_of_publicity_instance,
#         language="fin",
#         decision=False,
#         plan=plan_instance,
#     )
#     session.add(instance)
#     session.commit()
#     yield instance
#     session.delete(instance)
#     session.commit()


@pytest.fixture(scope="function")
def plan_map_instance(
    session,
    plan_instance,
    type_of_document_plan_map_instance,
    category_of_publicity_public_instance,
    personal_data_content_no_personal_data_instance,
    retention_time_permanent_instance,
    language_finnish_instance,
):
    instance = models.Document(
        name={"fin": "Kaavakartta"},
        type_of_document=type_of_document_plan_map_instance,
        category_of_publicity=category_of_publicity_public_instance,
        personal_data_content=personal_data_content_no_personal_data_instance,
        retention_time=retention_time_permanent_instance,
        language=language_finnish_instance,
        document_date=datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
        decision=False,
        plan=plan_instance,
        url="https://raw.githubusercontent.com/GeoTIFF/test-data/refs/heads/main/files/GeogToWGS84GeoKey5.tif",
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def lifecycle_date_instance(session, code_instance):
    instance = models.LifeCycleDate(
        lifecycle_status=code_instance,
        starting_at=datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
        ending_at=datetime(2025, 1, 1, tzinfo=LOCAL_TZ),
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def decision_date_instance(
    session,
    preparation_date_instance: models.LifeCycleDate,
    participation_plan_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
):
    instance = models.EventDate(
        lifecycle_date=preparation_date_instance,
        decision=participation_plan_presenting_for_public_decision,
        starting_at=datetime(2024, 2, 5, tzinfo=LOCAL_TZ),
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def processing_event_date_instance(
    session,
    preparation_date_instance: models.LifeCycleDate,
    participation_plan_presenting_for_public_event: codes.TypeOfProcessingEvent,
):
    instance = models.EventDate(
        lifecycle_date=preparation_date_instance,
        processing_event=participation_plan_presenting_for_public_event,
        starting_at=datetime(2024, 2, 15, tzinfo=LOCAL_TZ),
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def interaction_event_date_instance(
    session,
    preparation_date_instance: models.LifeCycleDate,
    presentation_to_the_public_interaction: codes.TypeOfInteractionEvent,
):
    instance = models.EventDate(
        lifecycle_date=preparation_date_instance,
        interaction_event=presentation_to_the_public_interaction,
        starting_at=datetime(2024, 2, 15, tzinfo=LOCAL_TZ),
        ending_at=datetime(2024, 2, 28, tzinfo=LOCAL_TZ),
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def main_use_additional_information_instance(
    session,
    type_of_main_use_additional_information_instance,
    empty_value_plan_regulation_instance,
):
    instance = models.AdditionalInformation(
        plan_regulation=empty_value_plan_regulation_instance,
        type_of_additional_information=type_of_main_use_additional_information_instance,
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture
def make_additional_information_instance_for_plan_regulation(session: Session):
    created_instances = []

    def _make_additional_information_instance_for_plan_regulation(
        plan_regulation: models.PlanRegulation,
        type_of_additional_information: codes.TypeOfAdditionalInformation,
    ):
        instance = models.AdditionalInformation(
            plan_regulation=plan_regulation,
            type_of_additional_information=type_of_additional_information,
        )
        session.add(instance)
        session.commit()
        created_instances.append(instance)
        return instance

    yield _make_additional_information_instance_for_plan_regulation

    for instance in created_instances:
        session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def complete_test_plan(
    session: Session,
    plan_map_instance: models.Document,
    plan_instance: models.Plan,
    land_use_area_instance: models.LandUseArea,
    land_use_point_instance: models.LandUsePoint,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    numeric_plan_regulation_group_instance: models.PlanRegulationGroup,
    point_plan_regulation_group_instance: models.PlanRegulationGroup,
    general_regulation_group_instance: models.PlanRegulationGroup,
    empty_value_plan_regulation_instance: models.PlanRegulation,
    text_plan_regulation_instance: models.PlanRegulation,
    point_text_plan_regulation_instance: models.PlanRegulation,
    numeric_plan_regulation_instance: models.PlanRegulation,
    numeric_range_plan_regulation_instance: models.PlanRegulation,
    verbal_plan_regulation_instance: models.PlanRegulation,
    general_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    plan_theme_instance: codes.PlanTheme,
    type_of_main_use_additional_information_instance: codes.TypeOfAdditionalInformation,
    make_additional_information_instance_for_plan_regulation: Callable[
        [models.PlanRegulation, codes.TypeOfAdditionalInformation],
        models.AdditionalInformation,
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
) -> Iterable[models.Plan]:
    """
    Plan data that might be more or less complete, to be tested and validated with the
    Ryhti API.

    For the plan *matter* to be validated, we also need extra code objects (that are not
    linked to the plan in the database) to be committed to the database, and some
    dates for the plan lifecycle statuses to be set.
    """
    # Add the optional (nullable) relationships. We don't want them to be present in
    # all fixtures.
    empty_value_plan_regulation_instance.plan_theme = plan_theme_instance
    # empty value plan regulation may have intended use
    empty_value_plan_regulation_instance.additional_information.append(
        make_additional_information_instance_for_plan_regulation(
            empty_value_plan_regulation_instance,
            type_of_main_use_additional_information_instance,
        )
    )

    numeric_plan_regulation_instance.plan_theme = plan_theme_instance
    # allowed area numeric value cannot be used with intended use regulation type

    text_plan_regulation_instance.plan_theme = plan_theme_instance
    # text value plan regulation may have intended use
    text_plan_regulation_instance.additional_information.append(
        make_additional_information_instance_for_plan_regulation(
            text_plan_regulation_instance,
            type_of_main_use_additional_information_instance,
        )
    )

    point_text_plan_regulation_instance.plan_theme = plan_theme_instance
    # point cannot *currently* be used with intended use regulation type

    numeric_range_plan_regulation_instance.plan_theme = plan_theme_instance
    # numeric range cannot be used with intended use regulation type

    verbal_plan_regulation_instance.plan_theme = plan_theme_instance
    # verbal plan regulation cannot be used with intended use regulation type

    general_plan_regulation_instance.plan_theme = plan_theme_instance
    # general plan regulation cannot be used with intended use regulation type

    plan_proposition_instance.plan_theme = plan_theme_instance
    session.commit()
    yield plan_instance


@pytest.fixture()
def another_test_plan(session, another_plan_instance):
    yield another_plan_instance


@pytest.fixture()
def pending_status_instance(session):
    instance = codes.LifeCycleStatus(value="02", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def pending_date_instance(
    session, plan_instance, pending_status_instance
) -> Iterable[models.LifeCycleDate]:
    instance = models.LifeCycleDate(
        plan=plan_instance,
        lifecycle_status=pending_status_instance,
        starting_at=datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
        ending_at=datetime(2024, 2, 1, tzinfo=LOCAL_TZ),
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def preparation_date_instance(
    session, plan_instance, preparation_status_instance
) -> Iterable[models.LifeCycleDate]:
    instance = models.LifeCycleDate(
        plan=plan_instance,
        lifecycle_status=preparation_status_instance,
        starting_at=datetime(2024, 2, 1, tzinfo=LOCAL_TZ),
        ending_at=datetime(2024, 3, 1, tzinfo=LOCAL_TZ),
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def approved_status_instance(session):
    instance = codes.LifeCycleStatus(value="06", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def approved_date_instance(
    session, plan_instance, approved_status_instance
) -> Iterable[models.LifeCycleDate]:
    instance = models.LifeCycleDate(
        plan=plan_instance,
        lifecycle_status=approved_status_instance,
        starting_at=datetime(2024, 3, 1, tzinfo=LOCAL_TZ),
        ending_at=datetime(2024, 4, 1, tzinfo=LOCAL_TZ),
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def valid_status_instance(session):
    instance = codes.LifeCycleStatus(value="13", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def valid_date_instance(
    session, plan_instance, valid_status_instance
) -> Iterable[models.LifeCycleDate]:
    instance = models.LifeCycleDate(
        plan=plan_instance,
        lifecycle_status=valid_status_instance,
        starting_at=datetime(2024, 4, 1, tzinfo=LOCAL_TZ),
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def participation_plan_presenting_for_public_decision(
    session, preparation_status_instance
):
    instance = codes.NameOfPlanCaseDecision(
        value="04", status="LOCAL", allowed_statuses=[preparation_status_instance]
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def plan_material_presenting_for_public_decision(session, preparation_status_instance):
    instance = codes.NameOfPlanCaseDecision(
        value="05", status="LOCAL", allowed_statuses=[preparation_status_instance]
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def draft_plan_presenting_for_public_decision(session, preparation_status_instance):
    instance = codes.NameOfPlanCaseDecision(
        value="06", status="LOCAL", allowed_statuses=[preparation_status_instance]
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def plan_proposal_sending_out_for_opinions_decision(
    session, plan_proposal_status_instance
):
    instance = codes.NameOfPlanCaseDecision(
        value="07", status="LOCAL", allowed_statuses=[plan_proposal_status_instance]
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def plan_proposal_presenting_for_public_decision(
    session, plan_proposal_status_instance
):
    instance = codes.NameOfPlanCaseDecision(
        value="08", status="LOCAL", allowed_statuses=[plan_proposal_status_instance]
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def participation_plan_presenting_for_public_event(
    session, preparation_status_instance
):
    instance = codes.TypeOfProcessingEvent(
        value="05", status="LOCAL", allowed_statuses=[preparation_status_instance]
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def plan_material_presenting_for_public_event(session, preparation_status_instance):
    instance = codes.TypeOfProcessingEvent(
        value="06", status="LOCAL", allowed_statuses=[preparation_status_instance]
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def plan_proposal_presenting_for_public_event(session, plan_proposal_status_instance):
    instance = codes.TypeOfProcessingEvent(
        value="07", status="LOCAL", allowed_statuses=[plan_proposal_status_instance]
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def plan_proposal_requesting_for_opinions_event(session, plan_proposal_status_instance):
    instance = codes.TypeOfProcessingEvent(
        value="08", status="LOCAL", allowed_statuses=[plan_proposal_status_instance]
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def presentation_to_the_public_interaction(
    session, preparation_status_instance, plan_proposal_status_instance
):
    instance = codes.TypeOfInteractionEvent(
        value="01",
        status="LOCAL",
        allowed_statuses=[preparation_status_instance, plan_proposal_status_instance],
    )
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture()
def decisionmaker_type(session):
    instance = codes.TypeOfDecisionMaker(value="01", status="LOCAL")
    session.add(instance)
    session.commit()
    yield instance
    session.delete(instance)
    session.commit()


@pytest.fixture(scope="function")
def desired_plan_dict(
    plan_instance: models.Plan,
    land_use_area_instance: models.LandUseArea,
    land_use_point_instance: models.LandUsePoint,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    numeric_plan_regulation_group_instance: models.PlanRegulationGroup,
    point_plan_regulation_group_instance: models.PlanRegulationGroup,
    general_regulation_group_instance: models.PlanRegulationGroup,
    empty_value_plan_regulation_instance: models.PlanRegulation,
    text_plan_regulation_instance: models.PlanRegulation,
    point_text_plan_regulation_instance: models.PlanRegulation,
    numeric_plan_regulation_instance: models.PlanRegulation,
    numeric_range_plan_regulation_instance: models.PlanRegulation,
    verbal_plan_regulation_instance: models.PlanRegulation,
    general_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    pending_date_instance: models.LifeCycleDate,
) -> dict:
    """
    Plan dict based on https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Avoin/ryhti-plan-public-validate-api.json

    Let's 1) write explicitly the complex fields, and 2) just check that the simple fields have
    the same values as the original plan fixture in the database.
    """

    return {
        "planKey": plan_instance.id,
        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
        "scale": plan_instance.scale,
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
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01",
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            general_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    },
                ],
                "planRecommendations": [],
            }
        ],
        "planDescription": plan_instance.description[
            "fin"
        ],  # TODO: should this be a single language string? why?
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
                                [381849.834412134019658, 6680613.389312859624624],
                                [386378.427863708813675, 6680613.389312859624624],
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
                "planObjectKey": land_use_point_instance.id,
                "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                "undergroundStatus": "http://uri.suomi.fi/codelist/rytj/RY_MaanalaisuudenLaji/code/01",
                "geometry": {
                    "srid": str(PROJECT_SRID),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [382000.0, 6678000.0],
                    },
                },
                "name": land_use_point_instance.name,
                "description": land_use_point_instance.description,
                "objectNumber": land_use_point_instance.ordering,
                "periodOfValidity": None,
            },
        ],
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
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01",
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
                            }
                        ],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01",
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
                            "minimumValue": int(
                                numeric_range_plan_regulation_instance.numeric_range_min
                            ),
                            "maximumValue": int(
                                numeric_range_plan_regulation_instance.numeric_range_max
                            ),
                            # "unitOfMeasure": numeric_range_plan_regulation_instance.unit,  #  floor range does not have unit
                        },
                        "subjectIdentifiers": numeric_range_plan_regulation_instance.subject_identifiers,
                        "additionalInformations": [],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01",
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
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01",
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
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01",
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
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01",
                        ],
                        "recommendationNumber": plan_proposition_instance.ordering,
                        # TODO: plan recommendation documents to be added.
                        "periodOfValidity": None,
                    },
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
                            "number": int(
                                numeric_plan_regulation_instance.numeric_value
                            ),
                            "unitOfMeasure": numeric_plan_regulation_instance.unit,
                        },
                        "subjectIdentifiers": numeric_plan_regulation_instance.subject_identifiers,
                        "additionalInformations": [],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/01",
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            numeric_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    },
                ],
                "planRecommendations": [],
                "letterIdentifier": numeric_plan_regulation_group_instance.short_name,
                "groupNumber": numeric_plan_regulation_group_instance.ordering,
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
                "planRegulationGroupKey": plan_regulation_group_instance.id,
            },
            {
                "planObjectKey": land_use_point_instance.id,
                "planRegulationGroupKey": point_plan_regulation_group_instance.id,
            },
        ],
    }


@pytest.fixture(scope="function")
def another_plan_dict(another_plan_instance: models.Plan) -> dict:
    """
    Minimal invalid plan dict with no related objects.
    """
    return {
        "planKey": another_plan_instance.id,
        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
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
        "planDescription": another_plan_instance.description[
            "fin"
        ],  # TODO: should this be a single language string? why?
        "planObjects": [],
        "planRegulationGroups": [],
        "planRegulationGroupRelations": [],
        "planMaps": [],
        "planAnnexes": [],
        "otherPlanMaterials": [],
        "planReport": None,
    }


@pytest.fixture(scope="function")
def desired_plan_matter_dict(
    session: Session,
    desired_plan_dict: dict,
    plan_instance: models.Plan,
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
) -> dict:
    """
    Plan matter dict based on https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Palveluväylä/Kaavoitus%20OpenApi.json

    Constructing the plan matter requires certain additional codes to be present in the database and set in the plan instance.

    Let's 1) write explicitly the complex fields, and 2) just check that the simple fields have
    the same values as the original plan fixture in the database.
    """

    return {
        "permanentPlanIdentifier": "MK-123456",
        "planType": "http://uri.suomi.fi/codelist/rytj/RY_Kaavalaji/code/11",
        "name": plan_instance.name,
        "timeOfInitiation": "2024-01-01",
        "description": plan_instance.description,
        "producerPlanIdentifier": plan_instance.producers_plan_identifier,
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
                    },
                ],
                "planDecision": {
                    "planDecisionKey": "whatever",
                    "name": "http://uri.suomi.fi/codelist/rytj/kaavpaatnimi/code/04",
                    "decisionDate": "2024-02-05",
                    "dateOfDecision": "2024-02-05",
                    "typeOfDecisionMaker": "http://uri.suomi.fi/codelist/rytj/PaatoksenTekija/code/01",
                    "plans": [
                        {
                            # Maps must be added to the valid plan inside plan matter
                            **desired_plan_dict,
                            "planMaps": [
                                {
                                    "planMapKey": "whatever",
                                    "name": {
                                        "fin": "Kaavakartta",
                                    },
                                    "fileKey": "whatever else",
                                    "coordinateSystem": "3067",
                                }
                            ],
                        }
                    ],
                },
            },
        ],
        # TODO: source data etc. non-mandatory fields to be added
    }


def assert_lists_equal(
    list1: list,
    list2: list,
    ignore_keys: Optional[List] = None,
    ignore_order_for_keys: Optional[List] = None,
    ignore_list_order: Optional[bool] = False,
    path: str = "",
):
    assert len(list1) == len(list2), f"Lists differ in length in path {path}"
    for i, item1 in enumerate(list1):
        current_path = f"{path}[{i}]" if path else f"[{i}]"
        items_to_compare = list2 if ignore_list_order else [list2[i]]
        latest_error = AssertionError()
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
                latest_error = error
                continue
            else:
                break
        else:
            raise latest_error


def assert_dicts_equal(
    dict1: Mapping,
    dict2: Mapping,
    ignore_keys: Optional[List] = None,
    ignore_order_for_keys: Optional[List] = None,
    path: str = "",
):
    assert len(dict1) == len(dict2), f"Dicts differ in length in {path}"
    for key in dict2.keys():
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
                ignore_list_order=key in ignore_order_for_keys
                if ignore_order_for_keys
                else False,
                path=current_path,
            )


def deepcompare(
    item1: object,
    item2: object,
    ignore_keys: Optional[List] = None,
    ignore_order_for_keys: Optional[List] = None,
    ignore_list_order: Optional[bool] = False,
    path: str = "",
):
    """
    Recursively check that dicts and lists in two items have the same items (type and value)
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
