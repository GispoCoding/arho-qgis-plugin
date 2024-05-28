# hame.plan_regulation

## Description

## Columns

| Name | Type | Default | Nullable | Children | Parents | Comment |
| ---- | ---- | ------- | -------- | -------- | ------- | ------- |
| plan_regulation_group_id | uuid |  | false |  | [hame.plan_regulation_group](hame.plan_regulation_group.md) |  |
| type_of_plan_regulation_id | uuid |  | false |  | [codes.type_of_plan_regulation](codes.type_of_plan_regulation.md) |  |
| type_of_verbal_plan_regulation_id | uuid |  | true |  | [codes.type_of_verbal_plan_regulation](codes.type_of_verbal_plan_regulation.md) |  |
| numeric_range | numrange |  | true |  |  |  |
| unit | varchar |  | true |  |  |  |
| text_value | jsonb | '{"eng": "", "fin": "", "swe": ""}'::jsonb | false |  |  |  |
| numeric_value | double precision |  | true |  |  |  |
| exported_at | timestamp without time zone |  | true |  |  |  |
| lifecycle_status_id | uuid |  | false |  | [codes.lifecycle_status](codes.lifecycle_status.md) |  |
| id | uuid | gen_random_uuid() | false | [hame.lifecycle_date](hame.lifecycle_date.md) |  |  |
| created_at | timestamp without time zone | now() | false |  |  |  |
| modified_at | timestamp without time zone | now() | false |  |  |  |
| ordering | integer |  | true |  |  |  |
| name | jsonb | '{"eng": "", "fin": "", "swe": ""}'::jsonb | false |  |  |  |
| intended_use_id | uuid |  | true |  | [codes.type_of_additional_information](codes.type_of_additional_information.md) |  |
| existence_id | uuid |  | true |  | [codes.type_of_additional_information](codes.type_of_additional_information.md) |  |
| regulation_type_additional_information_id | uuid |  | true |  | [codes.type_of_additional_information](codes.type_of_additional_information.md) |  |
| significance_id | uuid |  | true |  | [codes.type_of_additional_information](codes.type_of_additional_information.md) |  |
| reservation_id | uuid |  | true |  | [codes.type_of_additional_information](codes.type_of_additional_information.md) |  |
| development_id | uuid |  | true |  | [codes.type_of_additional_information](codes.type_of_additional_information.md) |  |
| disturbance_prevention_id | uuid |  | true |  | [codes.type_of_additional_information](codes.type_of_additional_information.md) |  |
| construction_control_id | uuid |  | true |  | [codes.type_of_additional_information](codes.type_of_additional_information.md) |  |
| plan_theme_id | uuid |  | true |  | [codes.plan_theme](codes.plan_theme.md) |  |

## Viewpoints

| Name | Definition |
| ---- | ---------- |
| [All tables](viewpoint-0.md) | All tables that make up maakuntakaava plan data. |

## Constraints

| Name | Type | Definition |
| ---- | ---- | ---------- |
| plan_lifecycle_status_id_fkey | FOREIGN KEY | FOREIGN KEY (lifecycle_status_id) REFERENCES codes.lifecycle_status(id) |
| construction_control_id_fkey | FOREIGN KEY | FOREIGN KEY (construction_control_id) REFERENCES codes.type_of_additional_information(id) |
| development_id_fkey | FOREIGN KEY | FOREIGN KEY (development_id) REFERENCES codes.type_of_additional_information(id) |
| disturbance_prevention_id_fkey | FOREIGN KEY | FOREIGN KEY (disturbance_prevention_id) REFERENCES codes.type_of_additional_information(id) |
| existence_id_fkey | FOREIGN KEY | FOREIGN KEY (existence_id) REFERENCES codes.type_of_additional_information(id) |
| intended_use_id_fkey | FOREIGN KEY | FOREIGN KEY (intended_use_id) REFERENCES codes.type_of_additional_information(id) |
| regulation_type_additional_information_id_fkey | FOREIGN KEY | FOREIGN KEY (regulation_type_additional_information_id) REFERENCES codes.type_of_additional_information(id) |
| reservation_id_fkey | FOREIGN KEY | FOREIGN KEY (reservation_id) REFERENCES codes.type_of_additional_information(id) |
| significance_id_fkey | FOREIGN KEY | FOREIGN KEY (significance_id) REFERENCES codes.type_of_additional_information(id) |
| type_of_plan_regulation_id_fkey | FOREIGN KEY | FOREIGN KEY (type_of_plan_regulation_id) REFERENCES codes.type_of_plan_regulation(id) |
| type_of_verbal_plan_regulation_id_fkey | FOREIGN KEY | FOREIGN KEY (type_of_verbal_plan_regulation_id) REFERENCES codes.type_of_verbal_plan_regulation(id) |
| plan_regulation_group_id_fkey | FOREIGN KEY | FOREIGN KEY (plan_regulation_group_id) REFERENCES hame.plan_regulation_group(id) |
| plan_regulation_pkey | PRIMARY KEY | PRIMARY KEY (id) |
| plan_theme_id_fkey | FOREIGN KEY | FOREIGN KEY (plan_theme_id) REFERENCES codes.plan_theme(id) |

## Indexes

| Name | Definition |
| ---- | ---------- |
| plan_regulation_pkey | CREATE UNIQUE INDEX plan_regulation_pkey ON hame.plan_regulation USING btree (id) |
| ix_hame_plan_regulation_ordering | CREATE INDEX ix_hame_plan_regulation_ordering ON hame.plan_regulation USING btree (ordering) |
| ix_hame_plan_regulation_lifecycle_status_id | CREATE INDEX ix_hame_plan_regulation_lifecycle_status_id ON hame.plan_regulation USING btree (lifecycle_status_id) |

## Triggers

| Name | Definition |
| ---- | ---------- |
| trg_plan_regulation_modified_at | CREATE TRIGGER trg_plan_regulation_modified_at BEFORE INSERT OR UPDATE ON hame.plan_regulation FOR EACH ROW EXECUTE FUNCTION hame.trgfunc_modified_at() |
| trg_plan_regulation_new_lifecycle_date | CREATE TRIGGER trg_plan_regulation_new_lifecycle_date BEFORE UPDATE ON hame.plan_regulation FOR EACH ROW WHEN ((new.lifecycle_status_id <> old.lifecycle_status_id)) EXECUTE FUNCTION hame.trgfunc_plan_regulation_new_lifecycle_date() |

## Relations

![er](hame.plan_regulation.svg)

---

> Generated by [tbls](https://github.com/k1LoW/tbls)
