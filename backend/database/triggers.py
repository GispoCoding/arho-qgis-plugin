import inspect
from typing import get_type_hints

import models
from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger
from shapely.geometry import MultiPolygon
from sqlalchemy.orm import Mapped

# All hame tables
hame_tables = [
    klass.__tablename__
    for _, klass in inspect.getmembers(models, inspect.isclass)
    if inspect.getmodule(klass) == models  # Ignore imported classes
]

# All tables that inherit PlanBase
tables_with_lifecycle_date = [
    klass.__tablename__
    for _, klass in inspect.getmembers(models, inspect.isclass)
    if inspect.getmodule(klass) == models and issubclass(klass, models.PlanBase)
]

# Regulations and propositions link to plan via plan regulation group
# or via plan regulation group *and* plan object, so lifecycle state
# will have to be updated in a slightly more convoluted fashion.
plan_regulation_tables = ["plan_regulation", "plan_proposition"]

# All plan objects also have lifecycle status and link directly to plan
plan_object_tables = [
    klass.__tablename__
    for _, klass in inspect.getmembers(models, inspect.isclass)
    if inspect.getmodule(klass) == models and issubclass(klass, models.PlanObjectBase)
]

tables_with_polygon_geometry = [
    klass.__tablename__
    for _, klass in inspect.getmembers(models, inspect.isclass)
    if inspect.getmodule(klass) == models
    and "geom" in get_type_hints(klass)
    and get_type_hints(klass)["geom"] == Mapped[MultiPolygon]
]


def generate_modified_at_triggers():
    trgfunc_signature = "trgfunc_modified_at()"
    trgfunc_definition = """
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.modified_at = CURRENT_TIMESTAMP;
            return NEW;
        END;
        $$ language 'plpgsql'
        """

    trgfunc = PGFunction(
        schema="hame",
        signature=trgfunc_signature,
        definition=trgfunc_definition,
    )

    trgs = []
    for table in hame_tables:
        trg_signature = f"trg_{table}_modified_at"
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


def generate_new_lifecycle_date_triggers():
    trgs = []
    trgfuncs = []
    for table in tables_with_lifecycle_date:
        trgfunc_signature = f"trgfunc_{table}_new_lifecycle_date()"
        trgfunc_definition = f"""
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO hame.lifecycle_date
                (lifecycle_status_id, {table}_id, starting_at)
            VALUES
                (NEW.lifecycle_status_id, NEW.id, CURRENT_TIMESTAMP);

            UPDATE hame.lifecycle_date
            SET ending_at=CURRENT_TIMESTAMP
            WHERE {table}_id=NEW.id
                AND ending_at IS NULL
                AND lifecycle_status_id=OLD.lifecycle_status_id;
            RETURN NEW;
        END;
        $$ language 'plpgsql'
        """

        trg_signature = f"trg_{table}_new_lifecycle_date"
        trg_definition = f"""
        BEFORE UPDATE ON {table}
        FOR EACH ROW
        WHEN (NEW.lifecycle_status_id <> OLD.lifecycle_status_id)
        EXECUTE FUNCTION hame.{trgfunc_signature}
        """

        trgfunc = PGFunction(
            schema="hame",
            signature=trgfunc_signature,
            definition=trgfunc_definition,
        )
        trgfuncs.append(trgfunc)

        trg = PGTrigger(
            schema="hame",
            signature=trg_signature,
            on_entity=f"hame.{table}",
            is_constraint=False,
            definition=trg_definition,
        )
        trgs.append(trg)

    return trgs, trgfuncs


def generate_update_lifecycle_status_triggers():
    trgs = []
    trgfuncs = []
    for object_table in plan_object_tables:
        trgfunc_signature = f"trgfunc_{object_table}_update_lifecycle_status()"
        trgfunc_definition = f"""
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE hame.{object_table}
            SET lifecycle_status_id = NEW.lifecycle_status_id
            WHERE (plan_id = NEW.id
            AND lifecycle_status_id = OLD.lifecycle_status_id);
            RETURN NEW;
        END;
        $$ language 'plpgsql'
        """

        trg_signature = f"trg_{object_table}_update_lifecycle_status"
        trg_definition = f"""
        BEFORE UPDATE ON plan
        FOR EACH ROW
        WHEN (NEW.lifecycle_status_id <> OLD.lifecycle_status_id)
        EXECUTE FUNCTION hame.{trgfunc_signature}
        """

        trgfunc = PGFunction(
            schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
        )
        trgfuncs.append(trgfunc)

        trg = PGTrigger(
            schema="hame",
            signature=trg_signature,
            on_entity="hame.plan",
            is_constraint=False,
            definition=trg_definition,
        )
        trgs.append(trg)

        # Also, each plan object table may trigger changes in *all* regulations linked
        # to the plan object table *through* a regulation group, let's create the
        # two extra trigger functions for each plan object table here:
        for regulation_table in plan_regulation_tables:
            trgfunc_signature = (
                f"trgfunc_{object_table}_{regulation_table}_update_lifecycle_status()"
            )
            trgfunc_definition = f"""
            RETURNS TRIGGER AS $$
            BEGIN
                UPDATE hame.{regulation_table}
                SET lifecycle_status_id = NEW.lifecycle_status_id
                WHERE (plan_regulation_group_id = NEW.plan_regulation_group_id
                AND lifecycle_status_id = OLD.lifecycle_status_id);
                RETURN NEW;
            END;
            $$ language 'plpgsql'
            """

            trg_signature = (
                f"trg_{object_table}_{regulation_table}_update_lifecycle_status"
            )
            trg_definition = f"""
            BEFORE UPDATE ON hame.{object_table}
            FOR EACH ROW
            WHEN (NEW.lifecycle_status_id <> OLD.lifecycle_status_id)
            EXECUTE FUNCTION hame.{trgfunc_signature}
            """

            trgfunc = PGFunction(
                schema="hame",
                signature=trgfunc_signature,
                definition=trgfunc_definition,
            )
            trgfuncs.append(trgfunc)

            trg = PGTrigger(
                schema="hame",
                signature=trg_signature,
                on_entity=f"hame.{object_table}",
                is_constraint=False,
                definition=trg_definition,
            )
            trgs.append(trg)

    # Finally, we want to update general regulations as well:
    for regulation_table in plan_regulation_tables:
        trgfunc_signature = f"trgfunc_plan_{regulation_table}_update_lifecycle_status()"
        trgfunc_definition = f"""
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE hame.{regulation_table}
            SET lifecycle_status_id = NEW.lifecycle_status_id
            WHERE (plan_regulation_group_id = NEW.plan_regulation_group_id
            AND lifecycle_status_id = OLD.lifecycle_status_id);
            RETURN NEW;
        END;
        $$ language 'plpgsql'
        """

        trg_signature = f"trg_plan_{regulation_table}_update_lifecycle_status"
        trg_definition = f"""
        BEFORE UPDATE ON hame.plan
        FOR EACH ROW
        WHEN (NEW.lifecycle_status_id <> OLD.lifecycle_status_id)
        EXECUTE FUNCTION hame.{trgfunc_signature}
        """

        trgfunc = PGFunction(
            schema="hame",
            signature=trgfunc_signature,
            definition=trgfunc_definition,
        )
        trgfuncs.append(trgfunc)

        trg = PGTrigger(
            schema="hame",
            signature=trg_signature,
            on_entity="hame.plan",
            is_constraint=False,
            definition=trg_definition,
        )
        trgs.append(trg)

    return trgs, trgfuncs


def generate_new_lifecycle_status_triggers():
    trgs = []
    trgfuncs = []
    for object_table in plan_object_tables:
        trgfunc_signature = f"trgfunc_{object_table}_new_lifecycle_status()"
        trgfunc_definition = """
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.lifecycle_status_id = (
                SELECT lifecycle_status_id FROM hame.plan WHERE plan.id = NEW.plan_id
            );
            RETURN NEW;
        END;
        $$ language 'plpgsql'
        """

        trg_signature = f"trg_{object_table}_new_lifecycle_status"
        trg_definition = f"""
        BEFORE INSERT ON {object_table}
        FOR EACH ROW
        WHEN (NEW.plan_id IS NOT NULL)
        EXECUTE FUNCTION hame.{trgfunc_signature}
        """

        trgfunc = PGFunction(
            schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
        )
        trgfuncs.append(trgfunc)

        trg = PGTrigger(
            schema="hame",
            signature=trg_signature,
            on_entity=f"hame.{object_table}",
            is_constraint=False,
            definition=trg_definition,
        )
        trgs.append(trg)

        # Also, each plan object table may trigger changes in *all* regulations linked
        # to the plan object table *through* a regulation group, let's create the
        # two extra trigger functions for each plan object table here:
        for regulation_table in plan_regulation_tables:
            trgfunc_signature = (
                f"trgfunc_{regulation_table}_{object_table}_new_lifecycle_status()"
            )
            # We must *only* update the lifecycle status *if* the plan regulation
            # group is linked to plan object. If SELECT returns NONE, the lifecycle
            # status should *not* be changed. This *cannot* be in the trigger condition,
            # because PostgreSQL does not allow subqueries in trigger conditions.
            trgfunc_definition = f"""
            RETURNS TRIGGER AS $$
            DECLARE status_id UUID := (
                SELECT lifecycle_status_id
                FROM hame.{object_table}
                WHERE plan_regulation_group_id = NEW.plan_regulation_group_id
                LIMIT 1
                );
            BEGIN
                IF status_id IS NOT NULL THEN
                    NEW.lifecycle_status_id = status_id;
                END IF;
                RETURN NEW;
            END;
            $$ language 'plpgsql'
            """

            trg_signature = (
                f"trg_{regulation_table}_{object_table}_new_lifecycle_status"
            )
            trg_definition = f"""
            BEFORE INSERT ON hame.{regulation_table}
            FOR EACH ROW
            EXECUTE FUNCTION hame.{trgfunc_signature}
            """

            trgfunc = PGFunction(
                schema="hame",
                signature=trgfunc_signature,
                definition=trgfunc_definition,
            )
            trgfuncs.append(trgfunc)
            print(trgfuncs)
            # assert False

            trg = PGTrigger(
                schema="hame",
                signature=trg_signature,
                on_entity=f"hame.{regulation_table}",
                is_constraint=False,
                definition=trg_definition,
            )
            trgs.append(trg)

    # Finally, we want to update general regulations as well:
    for regulation_table in ["plan_regulation"]:
        trgfunc_signature = f"trgfunc_{regulation_table}_plan_new_lifecycle_status()"
        # We must *only* update the lifecycle status *if* the plan regulation
        # group is linked to plan. If SELECT returns NONE, the lifecycle
        # status should *not* be changed. This *cannot* be in the trigger condition,
        # because PostgreSQL does not allow subqueries in trigger conditions.
        trgfunc_definition = """
        RETURNS TRIGGER AS $$
        DECLARE status_id UUID := (
            SELECT lifecycle_status_id
            FROM hame.plan
            WHERE plan_regulation_group_id = NEW.plan_regulation_group_id
            LIMIT 1
            );
        BEGIN
            IF status_id IS NOT NULL THEN
                NEW.lifecycle_status_id = status_id;
            END IF;
            RETURN NEW;
        END;
        $$ language 'plpgsql'
        """

        trg_signature = f"trg_{regulation_table}_plan_new_lifecycle_status"
        trg_definition = f"""
            BEFORE INSERT ON hame.{regulation_table}
            FOR EACH ROW
            EXECUTE FUNCTION hame.{trgfunc_signature}
        """

        trgfunc = PGFunction(
            schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
        )
        trgfuncs.append(trgfunc)

        trg = PGTrigger(
            schema="hame",
            signature=trg_signature,
            on_entity=f"hame.{regulation_table}",
            is_constraint=False,
            definition=trg_definition,
        )
        trgs.append(trg)

    return trgs, trgfuncs


def generate_add_plan_id_fkey_triggers():
    trgfunc_signature = "trgfunc_add_plan_id_fkey()"
    trgfunc_definition = """
    RETURNS TRIGGER AS $$
    BEGIN
        -- Get the most recent plan whose geometry contains the plan object
        NEW.plan_id := (
            SELECT id
            FROM hame.plan
            WHERE ST_Contains(geom, NEW.geom)
            ORDER BY created_at DESC
            LIMIT 1
        );
        RETURN NEW;
    END;
    $$ language 'plpgsql'
    """
    trgfunc = PGFunction(
        schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
    )

    trgs = []
    for table in plan_object_tables:
        trg_signature = f"trg_{table}_add_plan_id_fkey"
        trg_definition = f"""
        BEFORE INSERT ON {table}
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


def generate_validate_polygon_geometry_triggers():
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


trgfunc_add_intersecting_other_area_geometries = PGFunction(
    schema="hame",
    signature="trgfunc_other_area_insert_intersecting_geometries()",
    definition="""
    RETURNS TRIGGER AS $$
    BEGIN
        -- Check if the new entry has id of a plan_regulation_group
        -- which has id of a plan_regulation that has intended_use_id
        -- that equals to 'paakayttotarkoitus'
        IF EXISTS (
            SELECT 1
            FROM hame.plan_regulation_group prg
            JOIN hame.plan_regulation pr ON pr.plan_regulation_group_id = prg.id
            JOIN codes.type_of_additional_information tai ON tai.id = pr.intended_use_id
            WHERE tai.value = 'paakayttotarkoitus'
            AND prg.id = NEW.plan_regulation_group_id
        ) THEN
            -- check if there already is an entry in other_area table with the same
            -- plan_regulation_group that the new geometry intersects
            IF EXISTS (
                SELECT 1
                FROM hame.other_area oa
                WHERE oa.plan_regulation_group_id = NEW.plan_regulation_group_id
                AND ST_Intersects(oa.geom, NEW.geom)
            ) THEN
                RAISE EXCEPTION 'New entry intersects with existing entry, both with
                intended_use of paakayttotarkoitus';
            END IF;
        END IF;

        RETURN NEW;
    END;
    $$ language 'plpgsql'
    """,
)

trg_add_intersecting_other_area_geometries = PGTrigger(
    schema="hame",
    signature="trg_other_area_insert_intersecting_geometries",
    on_entity="hame.other_area",
    is_constraint=False,
    definition="""
    BEFORE INSERT ON other_area
    FOR EACH ROW
    EXECUTE FUNCTION hame.trgfunc_other_area_insert_intersecting_geometries()""",
)
