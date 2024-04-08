from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

trgfunc_plan_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_plan_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN

    UPDATE plan
    SET modified_at = CURRENT_TIMESTAMP
    WHERE plan_id = NEW.plan_id;

    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_plan_modified_at = PGTrigger(
    schema="hame",
    signature="trg_plan_modified_at",
    on_entity="hame.plan",
    is_constraint=False,
    definition="""AFTER UPDATE ON plan
        FOR EACH STATEMENT
        EXECUTE FUNCTION hame.trgfunc_plan_modified_at()""",
)

# Not working
trgfunc_update_lifecycle_status = PGFunction(
    schema="hame",
    signature="trgfunc_update_lifecycle_status()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM lifecycle_date
        WHERE lifecycle_status_id = NEW.lifecycle_status_id
    )
    THEN
        UPDATE lifecycle_date
        SET starting_at = CURRENT_TIMESTAMP
        WHERE plan_id = NEW.plan_id AND lifecycle_status_id = NEW.lifecycle_status_id;
    ELSE
        INSERT INTO lifecycle_date (lifecycle_status_id, starting_at)
        VALUES (NEW.lifecycle_status_id, CURRENT_TIMESTAMP);
    END IF;

#     RETURN NEW;
# END;
# $$ language 'plpgsql'
# """,
)

# Not working
trg_update_lifecycle_status = PGTrigger(
    schema="hame",
    signature="trg_update_lifecycle_status",
    on_entity="hame.plan",
    is_constraint=False,
    definition="""AFTER UPDATE ON plan
        FOR EACH ROW
        WHEN (NEW.lifecycle_status_id <> OLD.lifecycle_status_id)
        EXECUTE FUNCTION hame.trgfunc_update_lifecycle_status()""",
)
