import inspect
from textwrap import dedent, indent

from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

from database import models
from database.base import VersionedBase
from database.valid_views import LIFECYCLE_STATUS_REPEALED

# If new tables are added a new migration must be created in two steps.
# First to create the table, second to add triggers to it.
# To skip triggers for a new table, add a guard on the table name below.
all_versioned_tables: list[tuple[str, str]] = [
    (schema, table)
    for (schema, table) in VersionedBase.subclass_names()
    if table
    != "new_table_to_skip_triggers"  # Replace with actual table name to skip triggers for
]


# Regulations and propositions link to plan via plan regulation group
plan_regulation_tables = ["plan_regulation", "plan_proposition"]

# All plan objects also have lifecycle status and link directly to plan
plan_object_tables = [
    klass.__tablename__
    for _, klass in inspect.getmembers(models, inspect.isclass)
    if inspect.getmodule(klass) == models
    and issubclass(klass, models.PlanObjectBase)
    and hasattr(klass, "__tablename__")  # Ignore classes without __tablename__
]


def generate_created_at_triggers() -> tuple[list[PGTrigger], list[PGFunction]]:
    trgfunc_signature = "trgfunc_created_at()"
    trgfunc_definition = """
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.created_at = CURRENT_TIMESTAMP;
            NEW.creator = SESSION_USER;
            return NEW;
        END;
        $$ language 'plpgsql'
        """
    trgfunc = PGFunction(
        schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
    )

    trgs = []
    for schema, table in all_versioned_tables:
        trg_signature = f"trg_{table}_created_at"
        trg_definition = f"""
        BEFORE INSERT ON {schema}.{table}
        FOR EACH ROW
        EXECUTE FUNCTION hame.{trgfunc_signature}
        """

        trg = PGTrigger(
            schema=schema,
            signature=trg_signature,
            on_entity=f"{schema}.{table}",
            definition=trg_definition,
        )
        trgs.append(trg)

    return trgs, [trgfunc]


def generate_no_created_at_update_triggers() -> tuple[
    list[PGTrigger], list[PGFunction]
]:
    trgfunc_signature = "trgfunc_no_created_at_update()"
    trgfunc_definition = """
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.created_at = OLD.created_at;
            NEW.creator = OLD.creator;
            return NEW;
        END;
        $$ language 'plpgsql'
        """
    trgfunc = PGFunction(
        schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
    )

    trgs = []
    for schema, table in all_versioned_tables:
        trg_signature = f"trg_{table}_001_no_created_at_update"
        trg_definition = f"""
        BEFORE UPDATE ON {schema}.{table}
        FOR EACH ROW
        EXECUTE FUNCTION hame.{trgfunc_signature}
        """

        trg = PGTrigger(
            schema=schema,
            signature=trg_signature,
            on_entity=f"{schema}.{table}",
            definition=trg_definition,
        )
        trgs.append(trg)

    return trgs, [trgfunc]


def generate_modified_at_triggers() -> tuple[list[PGTrigger], list[PGFunction]]:
    trgfunc_signature = "trgfunc_modified_at()"
    trgfunc_definition = """
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW IS DISTINCT FROM OLD THEN
                NEW.modified_at = CURRENT_TIMESTAMP;
                NEW.modifier = SESSION_USER;
            END IF;
            return NEW;
        END;
        $$ language 'plpgsql'
        """

    trgfunc = PGFunction(
        schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
    )

    trgs = []
    for schema, table in all_versioned_tables:
        trg_signature = f"trg_{table}_modified_at"
        trg_definition = f"""
        BEFORE INSERT OR UPDATE ON {schema}.{table}
        FOR EACH ROW
        EXECUTE FUNCTION hame.{trgfunc_signature}
        """

        trg = PGTrigger(
            schema=schema,
            signature=trg_signature,
            on_entity=f"{schema}.{table}",
            is_constraint=False,
            definition=trg_definition,
        )
        trgs.append(trg)

    return trgs, [trgfunc]


def generate_new_lifecycle_status_triggers() -> tuple[
    list[PGTrigger], list[PGFunction]
]:
    trgs = []
    trgfuncs = []
    trgfunc_signature = "trgfunc_plan_object_new_lifecycle_status()"
    trgfunc_definition = """
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.lifecycle_status_id = (
                SELECT lifecycle_status_id
                FROM hame.plan
                WHERE plan.id = NEW.plan_id
            );
            RETURN NEW;
        END;
        $$ language 'plpgsql'
    """
    trgfunc = PGFunction(
        schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
    )
    trgfuncs.append(trgfunc)

    for object_table in plan_object_tables:
        trg_signature = f"trg_{object_table}_new_lifecycle_status"
        trg_definition = f"""
        BEFORE INSERT ON {object_table}
        FOR EACH ROW
        WHEN (NEW.lifecycle_status_id IS NULL)
        EXECUTE FUNCTION hame.{trgfunc_signature}
        """
        trg = PGTrigger(
            schema="hame",
            signature=trg_signature,
            on_entity=f"hame.{object_table}",
            is_constraint=False,
            definition=trg_definition,
        )
        trgs.append(trg)

    # Set the life cycle status of the new regulation to the same as the plan
    trgfunc_signature = "trgfunc_plan_regulation_new_lifecycle_status()"
    trgfunc_definition = """
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.lifecycle_status_id = (
                SELECT p.lifecycle_status_id
                FROM
                    hame.plan p
                    JOIN hame.plan_regulation_group prg
                        ON p.id = prg.plan_id
                WHERE prg.id = NEW.plan_regulation_group_id
            );
            RETURN NEW;
        END;
        $$ language 'plpgsql'
    """
    trgfunc = PGFunction(
        schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
    )
    trgfuncs.append(trgfunc)

    for regulation_table in plan_regulation_tables:
        trg_signature = f"trg_{regulation_table}_new_lifecycle_status"
        trg_definition = f"""
            BEFORE INSERT ON hame.{regulation_table}
            FOR EACH ROW
            WHEN (NEW.lifecycle_status_id IS NULL)
            EXECUTE FUNCTION hame.{trgfunc_signature}
        """
        trg = PGTrigger(
            schema="hame",
            signature=trg_signature,
            on_entity=f"hame.{regulation_table}",
            is_constraint=False,
            definition=trg_definition,
        )
        trgs.append(trg)

    return trgs, trgfuncs


def generate_plan_repealed_triggers() -> tuple[list[PGTrigger], list[PGFunction]]:
    """Repeal the children of a plan when the plan is repealed.

    Ryhti sets the plan objects, regulations and recommendations of a repealed
    plan to the repealed lifecycle status with the same end date as the plan,
    without a new version of the plan. The trigger does the same in hame, so it
    holds whoever repeals the plan: finalize_plan of ryhti_client, or a user who
    sets the status by hand.

    A child that is already repealed keeps its own status and end date, so an
    earlier partial repeal is not overwritten. A child whose own end date is
    earlier keeps that too.
    """
    updates = "\n".join(
        dedent(
            f"""\
            UPDATE hame.{object_table}
            SET
                lifecycle_status_id = NEW.lifecycle_status_id,
                period_of_validity_end = least(
                    period_of_validity_end, NEW.period_of_validity_end
                )
            WHERE
                plan_id = NEW.id
                AND lifecycle_status_id <> NEW.lifecycle_status_id;
            """
        )
        for object_table in plan_object_tables
    ) + "\n".join(
        dedent(
            f"""\
            UPDATE hame.{regulation_table} r
            SET
                lifecycle_status_id = NEW.lifecycle_status_id,
                period_of_validity_end = least(
                    r.period_of_validity_end, NEW.period_of_validity_end
                )
            FROM hame.plan_regulation_group prg
            WHERE
                prg.id = r.plan_regulation_group_id
                AND prg.plan_id = NEW.id
                AND r.lifecycle_status_id <> NEW.lifecycle_status_id;
            """
        )
        for regulation_table in plan_regulation_tables
    )
    trgfunc_signature = "trgfunc_plan_repealed()"
    trgfunc_definition = (
        dedent(
            f"""\
            RETURNS TRIGGER
            LANGUAGE plpgsql
            AS $$
            BEGIN
                -- A subquery is not allowed in the WHEN clause of the trigger,
                -- so the code value is checked here.
                IF NOT EXISTS (
                    SELECT 1
                    FROM codes.lifecycle_status
                    WHERE
                        id = NEW.lifecycle_status_id
                        AND value = '{LIFECYCLE_STATUS_REPEALED}'
                ) THEN
                    RETURN NULL;
                END IF;
            """
        )
        + indent(updates, "    ")
        + dedent(
            """\
                RETURN NULL;
            END;
            $$;
            """
        )
    )
    trgfunc = PGFunction(
        schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
    )
    trg = PGTrigger(
        schema="hame",
        signature="trg_plan_repealed",
        on_entity="hame.plan",
        is_constraint=False,
        definition=dedent(
            f"""\
            AFTER UPDATE ON hame.plan
            FOR EACH ROW
            WHEN (NEW.lifecycle_status_id IS DISTINCT FROM OLD.lifecycle_status_id)
            EXECUTE FUNCTION hame.{trgfunc_signature}
            """
        ),
    )
    return [trg], [trgfunc]


def generate_add_plan_id_fkey_triggers() -> tuple[list[PGTrigger], list[PGFunction]]:
    trgfunc_signature = "trgfunc_add_plan_id_fkey()"
    trgfunc_definition = """
    RETURNS TRIGGER AS $$
    BEGIN
        -- Get the most recent plan whose geometry contains the plan object
        IF NEW.plan_id IS NULL THEN
            NEW.plan_id := (
                SELECT id
                FROM hame.plan
                WHERE ST_Contains(geom, NEW.geom)
                ORDER BY created_at DESC
                LIMIT 1
            );
        END IF;
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


def generate_instead_of_triggers_for_visualization_views() -> tuple[
    list[PGTrigger], list[PGFunction]
]:
    trgfunc_signature = "trgf_iiud()"
    trgfunc_definition = dedent(
        """\
            RETURNS TRIGGER
            LANGUAGE plpgsql AS
        $$
        DECLARE
            _tbl  regclass := quote_ident(TG_TABLE_SCHEMA) || '.'
                            || quote_ident(substring(TG_TABLE_NAME from '(.+)_v$'));
            _cols text;
            _vals text;
        BEGIN
            IF TG_OP = 'DELETE' THEN
                EXECUTE format(
                    'DELETE FROM %s WHERE id = $1',
                    _tbl
                )
                USING OLD.id;
                RETURN OLD;
            END IF;

            SELECT INTO _cols, _vals
                    string_agg(quote_ident(attname), ', '),
                    string_agg('x.' || quote_ident(attname), ', ')
            FROM pg_attribute
            WHERE
                attrelid = _tbl
                AND NOT attisdropped   -- no dropped (dead) columns
                AND attnum > 0;        -- no system columns

            CASE TG_OP
                WHEN 'INSERT' THEN
                    EXECUTE format('
                        INSERT INTO %s(%s) SELECT %s
                        FROM  (SELECT ($1).*) x',
                    _tbl, _cols, _vals
                    )
                    USING NEW;
                WHEN 'UPDATE' THEN
                    EXECUTE format('
                        UPDATE %s a
                        SET   (%s) = (%s)
                        FROM  (SELECT ($2).*) x
                        WHERE a.id = $1',
                        _tbl, _cols, _vals
                    )
                    USING OLD.id, NEW;
            END CASE;

        RETURN NEW;
        END
        $$;
    """
    )

    trgfunc = PGFunction(
        schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
    )

    trgs = []
    for view in ("land_use_area_v", "other_area_v", "point_v", "line_v"):
        trg_signature = f"trg_iiud_{view}"
        trg_definition = dedent(
            f"""\
        INSTEAD OF INSERT OR UPDATE OR DELETE
        ON hame.{view}
        FOR EACH ROW
        EXECUTE FUNCTION hame.{trgfunc_signature}
        """
        )
        trg = PGTrigger(
            schema="hame",
            signature=trg_signature,
            on_entity=f"hame.{view}",
            is_constraint=False,
            definition=trg_definition,
        )
        trgs.append(trg)

    return trgs, [trgfunc]


def generate_plan_cancellation_info_triggers() -> tuple[
    list[PGTrigger], list[PGFunction]
]:
    """Keep the cancellation info of a repealing plan in step with its geometry.

    hame.repealed_plans and hame.repealed_plan_objects in database/functions.py
    say what the rows should be; the function generated here writes them into
    hame.plan_cancellation_info and hame.plan_object_cancellation_info.
    """
    trgfuncs = []

    # The plan rows are written with an upsert, so a repealed plan that stays
    # repealed keeps its row id and with it the cancelled group relations that
    # were added by hand. The plan object rows hold nothing added by hand and
    # have no natural key, so they are written again from scratch.
    refresh_signature = "refresh_plan_cancellation_info(repealing_plan_id uuid)"
    refresh_definition = dedent(
        """\
            RETURNS void
            LANGUAGE plpgsql
        AS $$
        DECLARE
            cancellation record;
        BEGIN
            -- hame.repealed_plans returns nothing when the plan matter is not
            -- repealing, so this also clears the rows when the flag is unset.
            DELETE FROM hame.plan_cancellation_info i
            WHERE i.plan_id = $1
                AND i.cancelled_plan_id NOT IN (
                    SELECT cancelled_plan_id FROM hame.repealed_plans($1)
                );

            INSERT INTO hame.plan_cancellation_info (
                plan_id, cancelled_plan_id, cancels_entire_plan
            )
            SELECT $1, r.cancelled_plan_id, r.cancels_entire_plan
            FROM hame.repealed_plans($1) r
            ON CONFLICT (plan_id, cancelled_plan_id) DO UPDATE
                SET cancels_entire_plan = excluded.cancels_entire_plan;

            FOR cancellation IN
                SELECT id, cancelled_plan_id, cancels_entire_plan
                FROM hame.plan_cancellation_info
                WHERE plan_id = $1
            LOOP
                DELETE FROM hame.plan_object_cancellation_info
                WHERE plan_cancellation_info_id = cancellation.id;

                -- Ryhti allows no plan object cancellation infos when the whole
                -- plan is repealed.
                CONTINUE WHEN cancellation.cancels_entire_plan;

                -- hame.repealed_plan_objects returns the columns below in this
                -- order.
                INSERT INTO hame.plan_object_cancellation_info (
                    plan_cancellation_info_id,
                    land_use_area_id,
                    other_area_id,
                    line_id,
                    point_id,
                    cancels_entire_plan_object,
                    remaining_valid_geom_polygon,
                    remaining_valid_geom_line,
                    remaining_valid_geom_point
                )
                SELECT cancellation.id, o.*
                FROM hame.repealed_plan_objects(
                    $1, cancellation.cancelled_plan_id
                ) o;
            END LOOP;
        END;
        $$;
        """
    )
    trgfuncs.append(
        PGFunction(
            schema="hame", signature=refresh_signature, definition=refresh_definition
        )
    )

    plan_trgfunc_signature = "trgfunc_refresh_plan_cancellation_info()"
    plan_trgfunc_definition = """
        RETURNS TRIGGER AS $$
        BEGIN
            PERFORM hame.refresh_plan_cancellation_info(NEW.id);
            RETURN NULL;
        END;
        $$ language 'plpgsql'
        """
    trgfuncs.append(
        PGFunction(
            schema="hame",
            signature=plan_trgfunc_signature,
            definition=plan_trgfunc_definition,
        )
    )

    matter_trgfunc_signature = "trgfunc_refresh_plan_matter_cancellation_info()"
    matter_trgfunc_definition = """
        RETURNS TRIGGER AS $$
        DECLARE
            repealing_plan_id uuid;
        BEGIN
            FOR repealing_plan_id IN
                SELECT id FROM hame.plan WHERE plan_matter_id = NEW.id
            LOOP
                PERFORM hame.refresh_plan_cancellation_info(repealing_plan_id);
            END LOOP;
            RETURN NULL;
        END;
        $$ language 'plpgsql'
        """
    trgfuncs.append(
        PGFunction(
            schema="hame",
            signature=matter_trgfunc_signature,
            definition=matter_trgfunc_definition,
        )
    )

    # The triggers fire after the row is written, because the plan_id foreign
    # key of hame.plan_cancellation_info is not deferred, so the plan row has to
    # exist already. The when clauses keep an edit that cannot change the
    # cancellation info, such as a name change, from recomputing anything.
    trgs = [
        PGTrigger(
            schema="hame",
            signature="trg_plan_refresh_cancellation_info_insert",
            on_entity="hame.plan",
            is_constraint=False,
            definition=dedent(
                f"""\
                AFTER INSERT ON hame.plan
                FOR EACH ROW
                EXECUTE FUNCTION hame.{plan_trgfunc_signature}
                """
            ),
        ),
        PGTrigger(
            schema="hame",
            signature="trg_plan_refresh_cancellation_info_update",
            on_entity="hame.plan",
            is_constraint=False,
            definition=dedent(
                f"""\
                AFTER UPDATE ON hame.plan
                FOR EACH ROW
                WHEN (
                    NEW.geom IS DISTINCT FROM OLD.geom
                    OR NEW.plan_matter_id IS DISTINCT FROM OLD.plan_matter_id
                )
                EXECUTE FUNCTION hame.{plan_trgfunc_signature}
                """
            ),
        ),
        PGTrigger(
            schema="hame",
            signature="trg_plan_matter_refresh_cancellation_info",
            on_entity="hame.plan_matter",
            is_constraint=False,
            definition=dedent(
                f"""\
                AFTER UPDATE ON hame.plan_matter
                FOR EACH ROW
                WHEN (NEW.repealing IS DISTINCT FROM OLD.repealing)
                EXECUTE FUNCTION hame.{matter_trgfunc_signature}
                """
            ),
        ),
    ]

    return trgs, trgfuncs
