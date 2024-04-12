from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

# modified_at triggers
trgfunc_plan_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_plan_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
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
    definition="""BEFORE INSERT OR UPDATE ON plan
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_plan_modified_at()""",
)

trgfunc_land_use_area_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_land_use_area_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_land_use_area_modified_at = PGTrigger(
    schema="hame",
    signature="trg_land_use_area_modified_at",
    on_entity="hame.land_use_area",
    is_constraint=False,
    definition="""BEFORE INSERT OR UPDATE ON land_use_area
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_land_use_area_modified_at()""",
)

trgfunc_other_area_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_other_area_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_other_area_modified_at = PGTrigger(
    schema="hame",
    signature="trg_other_area_modified_at",
    on_entity="hame.other_area",
    is_constraint=False,
    definition="""BEFORE INSERT OR UPDATE ON other_area
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_other_area_modified_at()""",
)

trgfunc_line_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_line_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_line_modified_at = PGTrigger(
    schema="hame",
    signature="trg_line_modified_at",
    on_entity="hame.line",
    is_constraint=False,
    definition="""BEFORE INSERT OR UPDATE ON line
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_line_modified_at()""",
)

trgfunc_land_use_point_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_land_use_point_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_land_use_point_modified_at = PGTrigger(
    schema="hame",
    signature="trg_land_use_point_modified_at",
    on_entity="hame.land_use_point",
    is_constraint=False,
    definition="""BEFORE INSERT OR UPDATE ON land_use_point
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_land_use_point_modified_at()""",
)

trgfunc_other_point_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_other_point_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_other_point_modified_at = PGTrigger(
    schema="hame",
    signature="trg_other_point_modified_at",
    on_entity="hame.other_point",
    is_constraint=False,
    definition="""BEFORE INSERT OR UPDATE ON other_point
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_other_point_modified_at()""",
)

trgfunc_plan_regulation_group_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_plan_regulation_group_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_plan_regulation_group_modified_at = PGTrigger(
    schema="hame",
    signature="trg_plan_regulation_group_modified_at",
    on_entity="hame.plan_regulation_group",
    is_constraint=False,
    definition="""BEFORE INSERT OR UPDATE ON plan_regulation_group
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_plan_regulation_group_modified_at()""",
)

trgfunc_plan_regulation_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_plan_regulation_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_plan_regulation_modified_at = PGTrigger(
    schema="hame",
    signature="trg_plan_regulation_modified_at",
    on_entity="hame.plan_regulation",
    is_constraint=False,
    definition="""BEFORE INSERT OR UPDATE ON plan_regulation
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_plan_regulation_modified_at()""",
)

trgfunc_plan_proposition_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_plan_proposition_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_plan_proposition_modified_at = PGTrigger(
    schema="hame",
    signature="trg_plan_proposition_modified_at",
    on_entity="hame.plan_proposition",
    is_constraint=False,
    definition="""BEFORE INSERT OR UPDATE ON plan_proposition
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_plan_proposition_modified_at()""",
)

trgfunc_source_data_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_source_data_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_source_data_modified_at = PGTrigger(
    schema="hame",
    signature="trg_source_data_modified_at",
    on_entity="hame.source_data",
    is_constraint=False,
    definition="""BEFORE INSERT OR UPDATE ON source_data
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_source_data_modified_at()""",
)

trgfunc_organisation_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_organisation_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_organisation_modified_at = PGTrigger(
    schema="hame",
    signature="trg_organisation_modified_at",
    on_entity="hame.organisation",
    is_constraint=False,
    definition="""BEFORE INSERT OR UPDATE ON organisation
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_organisation_modified_at()""",
)

trgfunc_document_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_document_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_document_modified_at = PGTrigger(
    schema="hame",
    signature="trg_document_modified_at",
    on_entity="hame.document",
    is_constraint=False,
    definition="""BEFORE INSERT OR UPDATE ON document
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_document_modified_at()""",
)

trgfunc_lifecycle_date_modified_at = PGFunction(
    schema="hame",
    signature="trgfunc_lifecycle_date_modified_at()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    return NEW;
END;
$$ language 'plpgsql'
""",
)

trg_lifecycle_date_modified_at = PGTrigger(
    schema="hame",
    signature="trg_lifecycle_date_modified_at",
    on_entity="hame.lifecycle_date",
    is_constraint=False,
    definition="""BEFORE INSERT OR UPDATE ON lifecycle_date
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgfunc_lifecycle_date_modified_at()""",
)

# hame_tables = [
#     "plan",
#     "land_use_area",
#     "other_area",
#     "line",
#     "land_use_point",
#     "other_point",
#     "plan_regulation_group",
#     "plan_regulation",
#     "plan_proposition",
#     "source_data",
#     "organisation",
#     "document",
#     "lfiecycle_data",
# ]

# # modified_at triggers

# modified_at_trgs = []
# modified_at_trgfuncs = []

# for table in hame_tables:
#     trgfunc_signature = f"trgfunc_{table}_modified_at"
#     trgfunc_definition = f"""
#     RETURNS TRIGGER AS $$
#     BEGIN
#         NEW.modified_at = CURRENT_TIMESTAMP;
#         return NEW;
#     END;
#     $$ language 'plpgsql'
#     """

#     trg_signature = f"trg_{table}_modified_at"
#     trg_definition = f"""
#     BEFORE INSERT OR UPDATE ON {table}
#     FOR EACH ROW
#     EXECUTE FUNCTION {trgfunc_signature}()
#     """

#     trgfunc = PGFunction(
#         schema="hame",
#         signature=trgfunc_signature,
#         definition=trgfunc_definition,
#     )
#     modified_at_trgfuncs.append(trgfunc)

#     trg = PGTrigger(
#         schema="hame",
#         signature=trg_signature,
#         on_entity=f"hame.{table}",
#         is_constraint=False,
#         definition=trg_definition,
#     )
#     modified_at_trgs.append(trg)


# Lifecycle status triggers
trgfunc_update_plan_lifecycle_status = PGFunction(
    schema="hame",
    signature="trgfunc_update_lifecycle_status()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO hame.lifecycle_date (lifecycle_status_id, plan_id, starting_at)
    VALUES (NEW.lifecycle_status_id, NEW.id, CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$ language 'plpgsql'
""",
)


trg_update_plan_lifecycle_status = PGTrigger(
    schema="hame",
    signature="trg_update_lifecycle_status",
    on_entity="hame.plan",
    is_constraint=False,
    definition="""AFTER UPDATE ON plan
        FOR EACH ROW
        WHEN (NEW.lifecycle_status_id <> OLD.lifecycle_status_id)
        EXECUTE FUNCTION hame.trgfunc_update_lifecycle_status()""",
)
