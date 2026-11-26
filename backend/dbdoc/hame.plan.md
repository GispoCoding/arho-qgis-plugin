# hame.plan

## Description

## Columns

| Name | Type | Default | Nullable | Children | Parents | Comment |
| ---- | ---- | ------- | -------- | -------- | ------- | ------- |
| name | jsonb | '{"eng": "", "fin": "", "swe": ""}'::jsonb | false |  |  |  |
| id | uuid | gen_random_uuid() | false | [hame.source_data](hame.source_data.md) [hame.land_use_area](hame.land_use_area.md) [hame.land_use_point](hame.land_use_point.md) [hame.line](hame.line.md) [hame.other_area](hame.other_area.md) [hame.other_point](hame.other_point.md) [hame.document](hame.document.md) [hame.lifecycle_date](hame.lifecycle_date.md) |  |  |
| created_at | timestamp without time zone | now() | false |  |  |  |
| modified_at | timestamp without time zone | now() | false |  |  |  |
| exported_at | timestamp without time zone |  | true |  |  |  |
| geom | geometry(MultiPolygon,3067) |  | false |  |  |  |
| lifecycle_status_id | uuid |  | false |  | [codes.lifecycle_status](codes.lifecycle_status.md) |  |
| organisation_id | uuid |  | false |  | [hame.organisation](hame.organisation.md) |  |
| plan_regulation_group_id | uuid |  | true |  | [hame.plan_regulation_group](hame.plan_regulation_group.md) |  |
| plan_type_id | uuid |  | false |  | [codes.plan_type](codes.plan_type.md) |  |
| permanent_plan_identifier | varchar |  | true |  |  |  |
| producers_plan_identifier | varchar |  | true |  |  |  |
| description | jsonb | '{"eng": "", "fin": "", "swe": ""}'::jsonb | false |  |  |  |
| scale | integer |  | true |  |  |  |
| matter_management_identifier | varchar |  | true |  |  |  |
| record_number | varchar |  | true |  |  |  |
| validated_at | timestamp without time zone |  | true |  |  |  |
| validation_errors | jsonb |  | true |  |  |  |

## Viewpoints

| Name | Definition |
| ---- | ---------- |
| [All tables](viewpoint-0.md) | All tables that make up maakuntakaava plan data. |

## Constraints

| Name | Type | Definition |
| ---- | ---- | ---------- |
| plan_pkey | PRIMARY KEY | PRIMARY KEY (id) |
| plan_lifecycle_status_id_fkey | FOREIGN KEY | FOREIGN KEY (lifecycle_status_id) REFERENCES codes.lifecycle_status(id) |
| plan_type_id_fkey | FOREIGN KEY | FOREIGN KEY (plan_type_id) REFERENCES codes.plan_type(id) |
| plan_regulation_group_id_fkey | FOREIGN KEY | FOREIGN KEY (plan_regulation_group_id) REFERENCES hame.plan_regulation_group(id) |
| organisation_id_fkey | FOREIGN KEY | FOREIGN KEY (organisation_id) REFERENCES hame.organisation(id) |

## Indexes

| Name | Definition |
| ---- | ---------- |
| plan_pkey | CREATE UNIQUE INDEX plan_pkey ON hame.plan USING btree (id) |
| idx_plan_geom | CREATE INDEX idx_plan_geom ON hame.plan USING gist (geom) |
| ix_hame_plan_lifecycle_status_id | CREATE INDEX ix_hame_plan_lifecycle_status_id ON hame.plan USING btree (lifecycle_status_id) |

## Triggers

| Name | Definition |
| ---- | ---------- |
| trg_plan_modified_at | CREATE TRIGGER trg_plan_modified_at BEFORE INSERT OR UPDATE ON hame.plan FOR EACH ROW EXECUTE FUNCTION hame.trgfunc_modified_at() |
| trg_plan_validate_polygon_geometry | CREATE TRIGGER trg_plan_validate_polygon_geometry BEFORE INSERT OR UPDATE ON hame.plan FOR EACH ROW EXECUTE FUNCTION hame.trgfunc_validate_polygon_geometry() |
| trg_plan_new_lifecycle_date | CREATE TRIGGER trg_plan_new_lifecycle_date BEFORE UPDATE ON hame.plan FOR EACH ROW WHEN ((new.lifecycle_status_id <> old.lifecycle_status_id)) EXECUTE FUNCTION hame.trgfunc_plan_new_lifecycle_date() |
| trg_land_use_area_update_lifecycle_status | CREATE TRIGGER trg_land_use_area_update_lifecycle_status BEFORE UPDATE ON hame.plan FOR EACH ROW WHEN ((new.lifecycle_status_id <> old.lifecycle_status_id)) EXECUTE FUNCTION hame.trgfunc_land_use_area_update_lifecycle_status() |
| trg_land_use_point_update_lifecycle_status | CREATE TRIGGER trg_land_use_point_update_lifecycle_status BEFORE UPDATE ON hame.plan FOR EACH ROW WHEN ((new.lifecycle_status_id <> old.lifecycle_status_id)) EXECUTE FUNCTION hame.trgfunc_land_use_point_update_lifecycle_status() |
| trg_line_update_lifecycle_status | CREATE TRIGGER trg_line_update_lifecycle_status BEFORE UPDATE ON hame.plan FOR EACH ROW WHEN ((new.lifecycle_status_id <> old.lifecycle_status_id)) EXECUTE FUNCTION hame.trgfunc_line_update_lifecycle_status() |
| trg_other_area_update_lifecycle_status | CREATE TRIGGER trg_other_area_update_lifecycle_status BEFORE UPDATE ON hame.plan FOR EACH ROW WHEN ((new.lifecycle_status_id <> old.lifecycle_status_id)) EXECUTE FUNCTION hame.trgfunc_other_area_update_lifecycle_status() |
| trg_other_point_update_lifecycle_status | CREATE TRIGGER trg_other_point_update_lifecycle_status BEFORE UPDATE ON hame.plan FOR EACH ROW WHEN ((new.lifecycle_status_id <> old.lifecycle_status_id)) EXECUTE FUNCTION hame.trgfunc_other_point_update_lifecycle_status() |
| trg_plan_proposition_update_lifecycle_status | CREATE TRIGGER trg_plan_proposition_update_lifecycle_status BEFORE UPDATE ON hame.plan FOR EACH ROW WHEN ((new.lifecycle_status_id <> old.lifecycle_status_id)) EXECUTE FUNCTION hame.trgfunc_plan_proposition_update_lifecycle_status() |
| trg_plan_regulation_update_lifecycle_status | CREATE TRIGGER trg_plan_regulation_update_lifecycle_status BEFORE UPDATE ON hame.plan FOR EACH ROW WHEN ((new.lifecycle_status_id <> old.lifecycle_status_id)) EXECUTE FUNCTION hame.trgfunc_plan_regulation_update_lifecycle_status() |

## Relations

![er](hame.plan.svg)

---

> Generated by [tbls](https://github.com/k1LoW/tbls)
