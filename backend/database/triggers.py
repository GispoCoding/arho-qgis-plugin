import inspect

import models
from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

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

# All tables that inherit PlanBase, excluding plan
tables_with_dependent_lifecycle_status = [
    klass.__tablename__
    for _, klass in inspect.getmembers(models, inspect.isclass)
    if inspect.getmodule(klass) == models
    and issubclass(klass, models.PlanBase)
    and klass is not models.Plan
]

plan_object_tables = [
    klass.__tablename__
    for _, klass in inspect.getmembers(models, inspect.isclass)
    if inspect.getmodule(klass) == models and issubclass(klass, models.PlanObjectBase)
]


def generate_modified_at_triggers():
    modified_at_trgs = []
    modified_at_trgfuncs = []

    for table in hame_tables:
        trgfunc_signature = f"trgfunc_{table}_modified_at()"
        trgfunc_definition = """
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.modified_at = CURRENT_TIMESTAMP;
            return NEW;
        END;
        $$ language 'plpgsql'
        """

        trg_signature = f"trg_{table}_modified_at"
        trg_definition = f"""
        BEFORE INSERT OR UPDATE ON {table}
        FOR EACH ROW
        EXECUTE FUNCTION hame.{trgfunc_signature}
        """

        trgfunc = PGFunction(
            schema="hame",
            signature=trgfunc_signature,
            definition=trgfunc_definition,
        )
        modified_at_trgfuncs.append(trgfunc)

        trg = PGTrigger(
            schema="hame",
            signature=trg_signature,
            on_entity=f"hame.{table}",
            is_constraint=False,
            definition=trg_definition,
        )
        modified_at_trgs.append(trg)

    return modified_at_trgs, modified_at_trgfuncs


def generate_new_lifecycle_date_triggers():
    new_lifecycle_date_trgs = []
    new_lifecycle_date_trgfuncs = []

    for table in tables_with_lifecycle_date:
        trgfunc_signature = f"trgfunc_{table}_new_lifecycle_date()"
        trgfunc_definition = f"""
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO hame.lifecycle_date
                (lifecycle_status_id, {table}_id, starting_at, ending_at)
            VALUES
                (NEW.lifecycle_status_id, NEW.id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
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
        new_lifecycle_date_trgfuncs.append(trgfunc)

        trg = PGTrigger(
            schema="hame",
            signature=trg_signature,
            on_entity=f"hame.{table}",
            is_constraint=False,
            definition=trg_definition,
        )
        new_lifecycle_date_trgs.append(trg)

    return new_lifecycle_date_trgs, new_lifecycle_date_trgfuncs


def generate_update_lifecycle_status_triggers():
    update_lifecycle_status_trgs = []
    update_lifecycle_status_trgfuncs = []

    for table in tables_with_dependent_lifecycle_status:
        trgfunc_signature = f"trgfunc_{table}_update_lifecycle_status()"
        trgfunc_definition = f"""
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE hame.{table}
            SET lifecycle_status_id = NEW.lifecycle_status_id
            WHERE plan_regulation_group_id = NEW.plan_regulation_group_id;
            RETURN NEW;
        END;
        $$ language 'plpgsql'
        """

        trg_signature = f"trg_{table}_update_lifecycle_status"
        trg_definition = f"""
        BEFORE UPDATE ON plan
        FOR EACH ROW
        WHEN (NEW.lifecycle_status_id <> OLD.lifecycle_status_id)
        EXECUTE FUNCTION hame.{trgfunc_signature}
        """

        trgfunc = PGFunction(
            schema="hame", signature=trgfunc_signature, definition=trgfunc_definition
        )
        update_lifecycle_status_trgfuncs.append(trgfunc)

        trg = PGTrigger(
            schema="hame",
            signature=trg_signature,
            on_entity="hame.plan",
            is_constraint=False,
            definition=trg_definition,
        )
        update_lifecycle_status_trgs.append(trg)

    return update_lifecycle_status_trgs, update_lifecycle_status_trgfuncs


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
