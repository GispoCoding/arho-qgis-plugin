from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

trgfunc_update_plan_regulation_exported_at = PGFunction(
    schema="hame",
    signature="trgfunc_update_plan_regulation_exported_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO plan_regulation (
        exported_at,
    ) values (
        NEW.exported_at,
    )
    WHERE plan_regulation.plan_id = NEW.id;

    return NEW;
END;
$$ language 'plpgsql';
""",
)

trg_update_exported_at = PGTrigger(
    schema="hame",
    signature="trg_update_exported_at",
    on_entity="hame.plan_regulation",
    is_constraint=False,
    definition="""AFTER INSERT ON plan
        FOR EACH STATEMENT
        EXECUTE FUNCTION trgfunc_update_plan_regulation_exported_at()""",
)
