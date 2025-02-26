import inspect

from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

from database import models

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
plan_regulation_tables = ["plan_regulation", "plan_proposition"]

# All plan objects also have lifecycle status and link directly to plan
plan_object_tables = [
    klass.__tablename__
    for _, klass in inspect.getmembers(models, inspect.isclass)
    if inspect.getmodule(klass) == models and issubclass(klass, models.PlanObjectBase)
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


def generate_new_object_add_lifecycle_date_triggers():
    trgs = []
    trgfunc_signature = "trgfunc_new_object_add_lifecycle_date()"
    trgfunc_definition = """
    RETURNS TRIGGER AS $$
    BEGIN
        EXECUTE format(
            $query$
            INSERT INTO hame.lifecycle_date
                (lifecycle_status_id, %I, starting_at)
            VALUES
                ($1, $2, CURRENT_TIMESTAMP)
            $query$,
            TG_TABLE_NAME || '_id'
        ) USING NEW.lifecycle_status_id, NEW.id;
        RETURN NEW;
    END;
    $$ language 'plpgsql'
        """
    trgfunc = PGFunction(
        schema="hame",
        signature=trgfunc_signature,
        definition=trgfunc_definition,
    )

    for table in tables_with_lifecycle_date:
        trg_signature = f"trg_new_{table}_add_lifecycle_date"
        trg_definition = f"""
        AFTER INSERT ON {table}
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
    trgfunc_signature = "trgfunc_new_lifecycle_date()"
    trgfunc_definition = """
    RETURNS TRIGGER AS $$
    BEGIN
        EXECUTE format(
            $query$
            INSERT INTO hame.lifecycle_date
                (lifecycle_status_id, %I, starting_at)
            VALUES
                ($1, $2, CURRENT_TIMESTAMP)
            $query$,
            TG_TABLE_NAME || '_id'
        ) USING NEW.lifecycle_status_id, NEW.id;
        EXECUTE format(
            $query$
            UPDATE hame.lifecycle_date
            SET ending_at=CURRENT_TIMESTAMP
            WHERE %I = $1
                AND ending_at IS NULL
                AND lifecycle_status_id = $2
            $query$,
            TG_TABLE_NAME || '_id'
        ) USING NEW.id, OLD.lifecycle_status_id;
        RETURN NEW;
    END;
    $$ language 'plpgsql'
    """
    trgfunc = PGFunction(
        schema="hame",
        signature=trgfunc_signature,
        definition=trgfunc_definition,
    )

    for table in tables_with_lifecycle_date:
        trg_signature = f"trg_{table}_new_lifecycle_date"
        trg_definition = f"""
        BEFORE UPDATE ON {table}
        FOR EACH ROW
        WHEN (NEW.lifecycle_status_id <> OLD.lifecycle_status_id)
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

    # Update lifecycle status of regulations after a lifecycle status change of a plan
    for regulation_table in plan_regulation_tables:
        trgfunc_signature = f"trgfunc_plan_{regulation_table}_update_lifecycle_status()"
        trgfunc_definition = f"""
            RETURNS TRIGGER AS $$
            BEGIN
                UPDATE hame.{regulation_table} rt
                SET lifecycle_status_id = NEW.lifecycle_status_id
                WHERE
                    EXISTS (
                        SELECT 1
                        FROM hame.plan_regulation_group prg
                        WHERE
                            prg.id = rt.plan_regulation_group_id
                            AND prg.plan_id = NEW.id
                    )
                    AND lifecycle_status_id = OLD.lifecycle_status_id
                ;
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
    trgfunc_signature = "trgfunc_plan_object_new_lifecycle_status()"
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
    trgfunc = PGFunction(
        schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
    )
    trgfuncs.append(trgfunc)

    for object_table in plan_object_tables:
        trg_signature = f"trg_{object_table}_new_lifecycle_status"
        trg_definition = f"""
        BEFORE INSERT ON {object_table}
        FOR EACH ROW
        WHEN (NEW.plan_id IS NOT NULL)
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


def generate_add_plan_id_fkey_triggers():
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
