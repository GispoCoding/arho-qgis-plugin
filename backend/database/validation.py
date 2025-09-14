import inspect

from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger
from geoalchemy2 import Geometry
from sqlalchemy import Column

from database import models

tables_with_polygon_geometry = []
for _, klass in inspect.getmembers(models, inspect.isclass):
    if not hasattr(klass, "__table__") or inspect.getmodule(klass) != models:
        continue

    columns: dict[str, Column] = klass.__table__.c
    geom_column = columns.get("geom")
    if (
        geom_column is not None
        and isinstance(geom_column.type, Geometry)
        and geom_column.type.geometry_type in ("MULTIPOLYGON", "POLYGON")
    ):
        tables_with_polygon_geometry.append(klass.__tablename__)


def generate_validate_polygon_geometry_triggers() -> tuple[
    list[PGTrigger], list[PGFunction]
]:
    trgfunc_signature = "trgfunc_validate_polygon_geometry()"
    trgfunc_definition = """
    RETURNS TRIGGER AS $$
    BEGIN
        IF NOT ST_IsValid(NEW.geom) THEN
            RAISE EXCEPTION 'Invalid geometry. Must follow OGC rules.';
        END IF;
        RETURN NEW;
    END;
    $$ language 'plpgsql'
    """
    trgfunc = PGFunction(
        schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
    )

    trgs = []
    for table in tables_with_polygon_geometry:
        trg_signature = f"trg_{table}_validate_polygon_geometry"
        trg_definition = f"""
        BEFORE INSERT OR UPDATE ON {table}
        FOR EACH ROW
        EXECUTE FUNCTION hame.{trgfunc_signature}
        """

        trg = PGTrigger(
            schema="hame",
            signature=trg_signature,
            on_entity=f"hame.{table}",
            is_constraint=False,
            definition=trg_definition,
        )
        trgs.append(trg)

    return trgs, [trgfunc]


trgfunc_validate_line_geometry = PGFunction(
    schema="hame",
    signature="trgfunc_line_validate_geometry()",
    definition="""
    RETURNS TRIGGER AS $$
    BEGIN
        IF NOT ST_IsSimple(NEW.geom) THEN
            RAISE EXCEPTION 'Invalid geometry. Must not intersect itself.';
        END IF;
        RETURN NEW;
    END;
    $$ language 'plpgsql'
    """,
)

trg_validate_line_geometry = PGTrigger(
    schema="hame",
    signature="trg_line_validate_geometry",
    on_entity="hame.line",
    is_constraint=False,
    definition="""
    BEFORE INSERT OR UPDATE ON line
    FOR EACH ROW
    EXECUTE FUNCTION hame.trgfunc_line_validate_geometry()""",
)


trgfunc_validate_lifecycle_date = PGFunction(
    schema="hame",
    signature="trgfunc_lifecycle_date_validate_dates()",
    definition="""
    RETURNS TRIGGER AS $$
    BEGIN
        IF (
            NEW.starting_at IS NOT NULL AND
            NEW.ending_at IS NOT NULL AND
            NEW.starting_at > NEW.ending_at
        ) IS TRUE
        THEN
            RAISE EXCEPTION 'Status starting date % after ending date %',
                NEW.starting_at, NEW.ending_at
                USING HINT = 'Status ending date must be after starting date.';
        END IF;
        RETURN NEW;
    END;
    $$ language 'plpgsql'
    """,
)

trg_validate_lifecycle_date = PGTrigger(
    schema="hame",
    signature="trg_lifecycle_date_validate_dates",
    on_entity="hame.lifecycle_date",
    definition="""
        BEFORE INSERT OR UPDATE ON lifecycle_date
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_lifecycle_date_validate_dates()
    """,
)

trgfunc_validate_event_date = PGFunction(
    schema="hame",
    signature="trgfunc_event_date_validate_dates()",
    definition="""
    RETURNS TRIGGER AS $$
    BEGIN
        IF (
            NEW.starting_at IS NOT NULL AND
            NEW.ending_at IS NOT NULL AND
            NEW.starting_at > NEW.ending_at
        ) IS TRUE
        THEN
            RAISE EXCEPTION 'Event starting date % after ending date %',
                NEW.starting_at, NEW.ending_at
                USING HINT = 'Event ending date must be after starting date.';
        END IF;
        RETURN NEW;
    END;
    $$ language 'plpgsql'
    """,
)

trg_validate_event_date = PGTrigger(
    schema="hame",
    signature="trg_event_date_validate_dates",
    on_entity="hame.event_date",
    definition="""
        BEFORE INSERT OR UPDATE ON event_date
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_event_date_validate_dates()
    """,
)

trgfunc_validate_event_date_inside_status_date = PGFunction(
    schema="hame",
    signature="trgfunc_event_date_validate_inside_status_date()",
    definition="""
    RETURNS TRIGGER AS $$
    DECLARE
        status_starting_at TIMESTAMP WITH TIME ZONE;
        status_ending_at TIMESTAMP WITH TIME ZONE;
    BEGIN
        SELECT starting_at, ending_at INTO status_starting_at, status_ending_at
        FROM hame.lifecycle_date
        WHERE NEW.lifecycle_date_id = hame.lifecycle_date.id;
        IF (
            -- Does the event start before status starts?
            (
             NEW.starting_at < status_starting_at
            ) OR
            -- Missing event ending date means event is instantaneous. Only
            -- events with ending date have a duration. Both must have ending
            -- date specified to check if event ends after status ends.
            (
             NEW.ending_at IS NOT NULL AND status_ending_at IS NOT NULL AND
             NEW.ending_at > status_ending_at
            )
        ) IS TRUE
        THEN
            RAISE EXCEPTION 'Event dates % - % outside status dates % - %',
                NEW.starting_at, NEW.ending_at, status_starting_at, status_ending_at
                USING HINT = 'Event cannot be outside lifecycle status dates.';
        END IF;
        RETURN NEW;
    END;
    $$ language 'plpgsql'
    """,
)

trg_validate_event_date_inside_status_date = PGTrigger(
    schema="hame",
    signature="trg_event_date_validate_inside_status_date",
    on_entity="hame.event_date",
    definition="""
        BEFORE INSERT OR UPDATE ON event_date
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_event_date_validate_inside_status_date()
    """,
)

trgfunc_validate_event_type = PGFunction(
    schema="hame",
    signature="trgfunc_event_date_validate_type()",
    definition="""
    RETURNS TRIGGER AS $$
    DECLARE
        status_id UUID;
        association_id UUID;
    BEGIN
        SELECT lifecycle_status_id INTO status_id
        FROM
            hame.lifecycle_date
        WHERE
            NEW.lifecycle_date_id = lifecycle_date.id;
        SELECT id INTO association_id
        FROM
            codes.allowed_events
        WHERE
            lifecycle_status_id = status_id AND (
                (NEW.decision_id IS NOT NULL AND
                 name_of_plan_case_decision_id = NEW.decision_id) OR
                (NEW.processing_event_id IS NOT NULL AND
                 type_of_processing_event_id = NEW.processing_event_id) OR
                (NEW.interaction_event_id IS NOT NULL AND
                 type_of_interaction_event_id = NEW.interaction_event_id)
            );
        IF association_id IS NULL
        THEN
            RAISE EXCEPTION 'Wrong event type for status'
            USING HINT = 'This event type cannot be added to this lifecycle status.';
        END IF;
        RETURN NEW;
    END;
    $$ language 'plpgsql'
    """,
)

trg_validate_event_type = PGTrigger(
    schema="hame",
    signature="trg_event_date_validate_type",
    on_entity="hame.event_date",
    definition="""
        BEFORE INSERT OR UPDATE ON event_date
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_event_date_validate_type()
    """,
)
