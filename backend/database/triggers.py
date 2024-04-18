from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

hame_tables = [
    "plan",
    "land_use_area",
    "other_area",
    "line",
    "land_use_point",
    "other_point",
    "plan_regulation_group",
    "plan_regulation",
    "plan_proposition",
    "source_data",
    "organisation",
    "document",
    "lifecycle_date",
]

tables_with_lifecycle_date = [
    "plan",
    "plan_regulation",
    "plan_proposition",
]

tables_with_lifecycle_status = [
    # plan and lifecycle_date do not belong here
    "land_use_area",
    "other_area",
    "line",
    "land_use_point",
    "other_point",
    "plan_regulation",
    "plan_proposition",
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
                (lifecycle_status_id, {table}_id, starting_at)
            VALUES (NEW.lifecycle_status_id, NEW.id, CURRENT_TIMESTAMP);
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
