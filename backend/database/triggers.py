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

# trgfunc_change_lifecycle_status = PGFunction(
#     schema="hame",
#     signature="trgfunc_change_lifecycle_status()",
#     definition="""
# RETURNS TRIGGER AS $$
# BEGIN

#     IF NEW.lifecycle_status = 'Valid' AND OLD.lifecycle_status != 'Valid' THEN
#         SET NEW.valid_from = CURRENT_TIMESTAMP;
#     END IF;

#     RETURN NEW;
# END;
# $$ language 'plpgsql'
# """,
# )

trg_plan_modified_at = PGTrigger(
    schema="hame",
    signature="trg_plan_modified_at",
    on_entity="hame.plan",
    is_constraint=False,
    definition="""AFTER UPDATE ON plan
        FOR EACH STATEMENT
        EXECUTE FUNCTION hame.trgfunc_plan_modified_at()""",
)

# trg_change_lifecycle_status = PGTrigger(
#     schema="hame",
#     signature="trg_change_lifecycle_status",
#     on_entity="hame.plan",
#     is_constraint=False,
#     definition="""AFTER UPDATE ON plan
#         FOR EACH STATEMENT
#         EXECUTE FUNCTION hame.trgfunc_change_lifecycle_status()""",
# )
