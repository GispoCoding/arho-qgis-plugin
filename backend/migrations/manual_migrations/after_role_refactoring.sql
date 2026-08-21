/*
This migration script was run manually to the test environment after the database role refactoring.
This script is kept here for reference.
*/

GRANT arho_dba to hame_su;

GRANT hame_admin TO hame_su;
REASSIGN OWNED BY hame_admin TO arho_dba;
DROP OWNED BY hame_admin;
DROP ROLE hame_admin;

GRANT hame_read TO hame_su;
REASSIGN OWNED BY hame_read TO arho_dba;
DROP OWNED BY hame_read;
DROP ROLE hame_read;

GRANT hame_read_write TO hame_su;
REASSIGN OWNED BY hame_read_write TO arho_dba;
DROP OWNED BY hame_read_write;
DROP ROLE hame_read_write;

GRANT SELECT ON TABLE public.qgis_projects TO arho_read_only;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.qgis_projects TO arho_read_write;

ALTER TABLE codes.type_of_verbal_plan_regulation OWNER TO arho_dba;
ALTER TABLE codes.type_of_source_data OWNER TO arho_dba;
ALTER TABLE codes.type_of_underground OWNER TO arho_dba;
ALTER TABLE codes.lifecycle_status OWNER TO arho_dba;
ALTER TABLE codes.type_of_document OWNER TO arho_dba;
ALTER TABLE codes.plan_type OWNER TO arho_dba;
ALTER TABLE codes.type_of_additional_information OWNER TO arho_dba;
ALTER TABLE codes.type_of_plan_regulation OWNER TO arho_dba;
ALTER TABLE codes.type_of_plan_regulation_group OWNER TO arho_dba;
ALTER TABLE codes.plan_theme OWNER TO arho_dba;
ALTER TABLE codes.category_of_publicity OWNER TO arho_dba;
ALTER TABLE codes.name_of_plan_case_decision OWNER TO arho_dba;
ALTER TABLE codes.type_of_interaction_event OWNER TO arho_dba;
ALTER TABLE codes.type_of_processing_event OWNER TO arho_dba;
ALTER TABLE codes.type_of_decision_maker OWNER TO arho_dba;
ALTER TABLE codes.administrative_region OWNER TO arho_dba;
ALTER TABLE hame.plan_regulation_group OWNER TO arho_dba;
ALTER TABLE codes.language OWNER TO arho_dba;
ALTER TABLE codes.personal_data_content OWNER TO arho_dba;
ALTER TABLE codes.retention_time OWNER TO arho_dba;
ALTER TABLE codes.municipality OWNER TO arho_dba;
ALTER TABLE hame.organisation OWNER TO arho_dba;
ALTER TABLE hame.event_date OWNER TO arho_dba;
ALTER TABLE codes.allowed_events OWNER TO arho_dba;
ALTER TABLE hame.additional_information OWNER TO arho_dba;
ALTER TABLE hame.type_of_verbal_regulation_association OWNER TO arho_dba;
ALTER TABLE codes.legal_effects_of_master_plan OWNER TO arho_dba;
ALTER TABLE hame.legal_effects_association OWNER TO arho_dba;
ALTER TABLE hame.document OWNER TO arho_dba;
ALTER TABLE hame.plan_theme_association OWNER TO arho_dba;
ALTER TABLE hame.lifecycle_date OWNER TO arho_dba;
ALTER TABLE hame.regulation_group_association OWNER TO arho_dba;
ALTER TABLE hame.plan_matter OWNER TO arho_dba;
ALTER TABLE hame.source_data OWNER TO arho_dba;
ALTER TABLE hame.land_use_area OWNER TO arho_dba;
ALTER TABLE hame.line OWNER TO arho_dba;
ALTER TABLE hame.other_area OWNER TO arho_dba;
ALTER TABLE hame.plan_proposition OWNER TO arho_dba;
ALTER TABLE hame.plan_regulation OWNER TO arho_dba;
ALTER TABLE hame.point OWNER TO arho_dba;
ALTER VIEW hame.land_use_area_v OWNER TO arho_dba;
ALTER VIEW hame.other_area_v OWNER TO arho_dba;
ALTER VIEW hame.point_v OWNER TO arho_dba;
ALTER VIEW hame.line_v OWNER TO arho_dba;
ALTER TABLE hame.plan OWNER TO arho_dba;
ALTER TABLE public.alembic_version OWNER TO arho_dba;


ALTER FUNCTION hame.trgfunc_modified_at() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_validate_polygon_geometry() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_line_validate_geometry() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_land_use_area_update_lifecycle_status() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_line_update_lifecycle_status() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_other_area_update_lifecycle_status() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_add_plan_id_fkey() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_plan_plan_regulation_update_lifecycle_status() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_plan_plan_proposition_update_lifecycle_status() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_lifecycle_date_validate_dates() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_event_date_validate_dates() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_event_date_validate_inside_status_date() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_event_date_validate_type() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_new_object_add_lifecycle_date() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_new_lifecycle_date() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_plan_object_new_lifecycle_status() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_plan_regulation_new_lifecycle_status() OWNER TO arho_dba;
ALTER FUNCTION hame.regulation_values(table_name text, id uuid) OWNER TO arho_dba;
ALTER FUNCTION hame.short_names(table_name text, id uuid) OWNER TO arho_dba;
ALTER FUNCTION hame.trgf_iiud() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_point_update_lifecycle_status() OWNER TO arho_dba;
ALTER FUNCTION hame.primary_use_regulations(land_use_area_id uuid) OWNER TO arho_dba;
ALTER FUNCTION hame.sub_area_regulations(other_area_id uuid) OWNER TO arho_dba;
ALTER FUNCTION hame.type_regulations(table_name text, id uuid) OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_created_at() OWNER TO arho_dba;
ALTER FUNCTION hame.trgfunc_no_created_at_update() OWNER TO arho_dba;

ALTER SCHEMA codes OWNER TO arho_dba;
ALTER SCHEMA hame OWNER TO arho_dba;

-- Replace <database-name> with the database name of the instance.
ALTER DATABASE "<database-name>" OWNER TO arho_dba;
