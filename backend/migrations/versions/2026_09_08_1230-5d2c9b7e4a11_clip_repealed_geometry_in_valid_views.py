"""clip repealed geometry in valid views

Revision ID: 5d2c9b7e4a11
Revises: 43cae9a4407a
Create Date: 2026-09-08 12:30:00.000000

"""

from collections.abc import Sequence

from alembic import op
from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_view import PGView

# revision identifiers, used by Alembic.
revision: str = "5d2c9b7e4a11"
down_revision: str | None = "43cae9a4407a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The views are written by hand, because alembic --autogenerate cannot compare
# a view that the other valid views depend on. Every view keeps its column
# list, so CREATE OR REPLACE VIEW works and the grants on the views survive.
# The definitions are those of database/valid_views.py before and after
# docs/adr/0002-valid-views-clip-repealed-geometry.md.
NEW_PLAN_VALID = "select\n    p.plan_matter_id,\n    p.name,\n    p.description,\n    p.scale,\n    p.official_use_only,\n    p.approval_date,\n    p.locked,\n    remaining.geom,\n    p.validated_at,\n    p.validation_errors,\n    p.exported_at,\n    p.id,\n    p.creator,\n    p.created_at,\n    p.modified_at,\n    p.modifier,\n    p.lifecycle_status_id,\n    p.period_of_validity_start,\n    p.period_of_validity_end\nfrom\n    hame.plan p\n    join codes.lifecycle_status ls on ls.id = p.lifecycle_status_id\n    cross join lateral (\n        select st_multi(st_collectionextract(\n            coalesce(st_difference(p.geom, st_union(repealing.geom)), p.geom), 3\n        ))::geometry(MultiPolygon, 3067) geom\n        from\n            hame.plan_cancellation_info ci\n            join hame.plan repealing on repealing.id = ci.plan_id\n        where\n            ci.cancelled_plan_id = p.id\n            and repealing.final and current_date >= coalesce(repealing.period_of_validity_start, '-infinity'::date)\n    ) remaining\nwhere\n    p.final\n    and ls.value = '13'\n    and current_date between coalesce(p.period_of_validity_start, '-infinity'::date) and coalesce(p.period_of_validity_end, 'infinity'::date)\n    and not st_isempty(remaining.geom)"
OLD_PLAN_VALID = "select\n    p.plan_matter_id,\n    p.name,\n    p.description,\n    p.scale,\n    p.official_use_only,\n    p.approval_date,\n    p.locked,\n    p.geom,\n    p.validated_at,\n    p.validation_errors,\n    p.exported_at,\n    p.id,\n    p.creator,\n    p.created_at,\n    p.modified_at,\n    p.modifier,\n    p.lifecycle_status_id,\n    p.period_of_validity_start,\n    p.period_of_validity_end\nfrom\n    hame.plan p\n    join codes.lifecycle_status ls on ls.id = p.lifecycle_status_id\nwhere\n    p.final\n    and ls.value = '13'\n    and current_date between coalesce(p.period_of_validity_start, '-infinity'::date) and coalesce(p.period_of_validity_end, 'infinity'::date)"
NEW_LAND_USE_AREA_VALID = "select\n    t.id,\n    remaining.geom,\n    t.name,\n    t.source_data_object,\n    t.height_unit,\n    t.ordering,\n    t.type_of_underground_id,\n    t.plan_id,\n    t.exported_at,\n    t.lifecycle_status_id,\n    t.created_at,\n    t.creator,\n    t.modified_at,\n    t.modifier,\n    t.description,\n    t.height_min,\n    t.height_max,\n    t.height_reference_point,\n    t.period_of_validity_start,\n    t.period_of_validity_end,\n    t.short_names,\n    t.primary_use,\n    t.regulation_values\nfrom\n    hame.land_use_area_v t\n    join hame.plan_valid p on p.id = t.plan_id\n    join codes.lifecycle_status ls on ls.id = t.lifecycle_status_id\n    cross join lateral (\n        select\n            bool_or(oci.cancels_entire_plan_object) repealed_entirely,\n            st_multi(st_collectionextract(\n                coalesce(\n                    hame.intersection_all(array_agg(oci.remaining_valid_geom_polygon)),\n                    t.geom\n                ),\n                3\n            ))::geometry(MultiPolygon, 3067) geom\n        from\n            hame.plan_object_cancellation_info oci\n            join hame.plan_cancellation_info ci\n                on ci.id = oci.plan_cancellation_info_id\n            join hame.plan repealing on repealing.id = ci.plan_id\n        where\n            oci.land_use_area_id = t.id\n            and repealing.final and current_date >= coalesce(repealing.period_of_validity_start, '-infinity'::date)\n    ) remaining\nwhere\n    ls.value = '13'\n    and current_date between coalesce(t.period_of_validity_start, '-infinity'::date) and coalesce(t.period_of_validity_end, 'infinity'::date)\n    and not coalesce(remaining.repealed_entirely, false)\n    and not st_isempty(remaining.geom)"
OLD_LAND_USE_AREA_VALID = "select\n    t.id,\n    t.geom,\n    t.name,\n    t.source_data_object,\n    t.height_unit,\n    t.ordering,\n    t.type_of_underground_id,\n    t.plan_id,\n    t.exported_at,\n    t.lifecycle_status_id,\n    t.created_at,\n    t.creator,\n    t.modified_at,\n    t.modifier,\n    t.description,\n    t.height_min,\n    t.height_max,\n    t.height_reference_point,\n    t.period_of_validity_start,\n    t.period_of_validity_end,\n    t.short_names,\n    t.primary_use,\n    t.regulation_values\nfrom\n    hame.land_use_area_v t\n    join hame.plan_valid p on p.id = t.plan_id\n    join codes.lifecycle_status ls on ls.id = t.lifecycle_status_id\nwhere\n    ls.value = '13'\n    and current_date between coalesce(t.period_of_validity_start, '-infinity'::date) and coalesce(t.period_of_validity_end, 'infinity'::date)"
NEW_OTHER_AREA_VALID = "select\n    t.id,\n    remaining.geom,\n    t.name,\n    t.source_data_object,\n    t.height_unit,\n    t.ordering,\n    t.type_of_underground_id,\n    t.plan_id,\n    t.exported_at,\n    t.lifecycle_status_id,\n    t.created_at,\n    t.creator,\n    t.modified_at,\n    t.modifier,\n    t.description,\n    t.height_min,\n    t.height_max,\n    t.height_reference_point,\n    t.period_of_validity_start,\n    t.period_of_validity_end,\n    t.short_names,\n    t.sub_area,\n    t.regulation_values\nfrom\n    hame.other_area_v t\n    join hame.plan_valid p on p.id = t.plan_id\n    join codes.lifecycle_status ls on ls.id = t.lifecycle_status_id\n    cross join lateral (\n        select\n            bool_or(oci.cancels_entire_plan_object) repealed_entirely,\n            st_multi(st_collectionextract(\n                coalesce(\n                    hame.intersection_all(array_agg(oci.remaining_valid_geom_polygon)),\n                    t.geom\n                ),\n                3\n            ))::geometry(MultiPolygon, 3067) geom\n        from\n            hame.plan_object_cancellation_info oci\n            join hame.plan_cancellation_info ci\n                on ci.id = oci.plan_cancellation_info_id\n            join hame.plan repealing on repealing.id = ci.plan_id\n        where\n            oci.other_area_id = t.id\n            and repealing.final and current_date >= coalesce(repealing.period_of_validity_start, '-infinity'::date)\n    ) remaining\nwhere\n    ls.value = '13'\n    and current_date between coalesce(t.period_of_validity_start, '-infinity'::date) and coalesce(t.period_of_validity_end, 'infinity'::date)\n    and not coalesce(remaining.repealed_entirely, false)\n    and not st_isempty(remaining.geom)"
OLD_OTHER_AREA_VALID = "select\n    t.id,\n    t.geom,\n    t.name,\n    t.source_data_object,\n    t.height_unit,\n    t.ordering,\n    t.type_of_underground_id,\n    t.plan_id,\n    t.exported_at,\n    t.lifecycle_status_id,\n    t.created_at,\n    t.creator,\n    t.modified_at,\n    t.modifier,\n    t.description,\n    t.height_min,\n    t.height_max,\n    t.height_reference_point,\n    t.period_of_validity_start,\n    t.period_of_validity_end,\n    t.short_names,\n    t.sub_area,\n    t.regulation_values\nfrom\n    hame.other_area_v t\n    join hame.plan_valid p on p.id = t.plan_id\n    join codes.lifecycle_status ls on ls.id = t.lifecycle_status_id\nwhere\n    ls.value = '13'\n    and current_date between coalesce(t.period_of_validity_start, '-infinity'::date) and coalesce(t.period_of_validity_end, 'infinity'::date)"
NEW_LINE_VALID = "select\n    t.id,\n    remaining.geom,\n    t.name,\n    t.source_data_object,\n    t.height_unit,\n    t.ordering,\n    t.type_of_underground_id,\n    t.plan_id,\n    t.exported_at,\n    t.lifecycle_status_id,\n    t.created_at,\n    t.creator,\n    t.modified_at,\n    t.modifier,\n    t.description,\n    t.height_min,\n    t.height_max,\n    t.height_reference_point,\n    t.period_of_validity_start,\n    t.period_of_validity_end,\n    t.short_names,\n    t.type_regulations,\n    t.regulation_values\nfrom\n    hame.line_v t\n    join hame.plan_valid p on p.id = t.plan_id\n    join codes.lifecycle_status ls on ls.id = t.lifecycle_status_id\n    cross join lateral (\n        select\n            bool_or(oci.cancels_entire_plan_object) repealed_entirely,\n            st_multi(st_collectionextract(\n                coalesce(\n                    hame.intersection_all(array_agg(oci.remaining_valid_geom_line)),\n                    t.geom\n                ),\n                2\n            ))::geometry(MultiLineString, 3067) geom\n        from\n            hame.plan_object_cancellation_info oci\n            join hame.plan_cancellation_info ci\n                on ci.id = oci.plan_cancellation_info_id\n            join hame.plan repealing on repealing.id = ci.plan_id\n        where\n            oci.line_id = t.id\n            and repealing.final and current_date >= coalesce(repealing.period_of_validity_start, '-infinity'::date)\n    ) remaining\nwhere\n    ls.value = '13'\n    and current_date between coalesce(t.period_of_validity_start, '-infinity'::date) and coalesce(t.period_of_validity_end, 'infinity'::date)\n    and not coalesce(remaining.repealed_entirely, false)\n    and not st_isempty(remaining.geom)"
OLD_LINE_VALID = "select\n    t.id,\n    t.geom,\n    t.name,\n    t.source_data_object,\n    t.height_unit,\n    t.ordering,\n    t.type_of_underground_id,\n    t.plan_id,\n    t.exported_at,\n    t.lifecycle_status_id,\n    t.created_at,\n    t.creator,\n    t.modified_at,\n    t.modifier,\n    t.description,\n    t.height_min,\n    t.height_max,\n    t.height_reference_point,\n    t.period_of_validity_start,\n    t.period_of_validity_end,\n    t.short_names,\n    t.type_regulations,\n    t.regulation_values\nfrom\n    hame.line_v t\n    join hame.plan_valid p on p.id = t.plan_id\n    join codes.lifecycle_status ls on ls.id = t.lifecycle_status_id\nwhere\n    ls.value = '13'\n    and current_date between coalesce(t.period_of_validity_start, '-infinity'::date) and coalesce(t.period_of_validity_end, 'infinity'::date)"
NEW_POINT_VALID = "select\n    t.id,\n    remaining.geom,\n    t.name,\n    t.source_data_object,\n    t.height_unit,\n    t.ordering,\n    t.type_of_underground_id,\n    t.plan_id,\n    t.exported_at,\n    t.lifecycle_status_id,\n    t.created_at,\n    t.creator,\n    t.modified_at,\n    t.modifier,\n    t.description,\n    t.height_min,\n    t.height_max,\n    t.height_reference_point,\n    t.period_of_validity_start,\n    t.period_of_validity_end,\n    t.short_names,\n    t.type_regulations,\n    t.regulation_values\nfrom\n    hame.point_v t\n    join hame.plan_valid p on p.id = t.plan_id\n    join codes.lifecycle_status ls on ls.id = t.lifecycle_status_id\n    cross join lateral (\n        select\n            bool_or(oci.cancels_entire_plan_object) repealed_entirely,\n            st_multi(st_collectionextract(\n                coalesce(\n                    hame.intersection_all(array_agg(oci.remaining_valid_geom_point)),\n                    t.geom\n                ),\n                1\n            ))::geometry(MultiPoint, 3067) geom\n        from\n            hame.plan_object_cancellation_info oci\n            join hame.plan_cancellation_info ci\n                on ci.id = oci.plan_cancellation_info_id\n            join hame.plan repealing on repealing.id = ci.plan_id\n        where\n            oci.point_id = t.id\n            and repealing.final and current_date >= coalesce(repealing.period_of_validity_start, '-infinity'::date)\n    ) remaining\nwhere\n    ls.value = '13'\n    and current_date between coalesce(t.period_of_validity_start, '-infinity'::date) and coalesce(t.period_of_validity_end, 'infinity'::date)\n    and not coalesce(remaining.repealed_entirely, false)\n    and not st_isempty(remaining.geom)"
OLD_POINT_VALID = "select\n    t.id,\n    t.geom,\n    t.name,\n    t.source_data_object,\n    t.height_unit,\n    t.ordering,\n    t.type_of_underground_id,\n    t.plan_id,\n    t.exported_at,\n    t.lifecycle_status_id,\n    t.created_at,\n    t.creator,\n    t.modified_at,\n    t.modifier,\n    t.description,\n    t.height_min,\n    t.height_max,\n    t.height_reference_point,\n    t.period_of_validity_start,\n    t.period_of_validity_end,\n    t.short_names,\n    t.type_regulations,\n    t.regulation_values\nfrom\n    hame.point_v t\n    join hame.plan_valid p on p.id = t.plan_id\n    join codes.lifecycle_status ls on ls.id = t.lifecycle_status_id\nwhere\n    ls.value = '13'\n    and current_date between coalesce(t.period_of_validity_start, '-infinity'::date) and coalesce(t.period_of_validity_end, 'infinity'::date)"

# The intersection of the remaining valid geometries of a plan object, called
# by the plan object views. See intersection_all in database/functions.py.
INTERSECTION_ALL = PGFunction(
    schema="hame",
    signature="intersection_all(geoms geometry[])",
    definition="RETURNS geometry\n    IMMUTABLE\n    PARALLEL SAFE\n    STRICT\n    LANGUAGE plpgsql\nAS $$\nDECLARE\n    result geometry;\n    geom geometry;\nBEGIN\n    FOREACH geom IN ARRAY geoms LOOP\n        IF geom IS NULL THEN\n            CONTINUE;\n        END IF;\n        IF result IS NULL THEN\n            result := geom;\n        ELSE\n            result := st_intersection(result, geom);\n        END IF;\n    END LOOP;\n    RETURN result;\nEND;\n$$",
)

# hame.repealed_plans reads the geometry of the repealed plan from hame.plan
# instead of the now clipped hame.plan_valid, see database/functions.py.
NEW_REPEALED_PLANS = PGFunction(
    schema="hame",
    signature="repealed_plans(repealing_plan_id uuid)",
    definition="RETURNS TABLE (cancelled_plan_id uuid, cancels_entire_plan boolean)\n    STABLE\n    PARALLEL SAFE\n    LANGUAGE sql\nAS $$\n    select\n        cancelled.id,\n        st_coveredby(cancelled.geom, repealing.geom)\n    from\n        hame.plan repealing\n        join hame.plan_matter repealing_matter\n            on repealing_matter.id = repealing.plan_matter_id\n        join hame.plan cancelled\n            on st_intersects(cancelled.geom, repealing.geom)\n        join hame.plan_valid valid on valid.id = cancelled.id\n        join hame.plan_matter_valid cancelled_matter\n            on cancelled_matter.id = cancelled.plan_matter_id\n    where\n        repealing.id = $1\n        and repealing_matter.repealing\n        and cancelled.plan_matter_id <> repealing.plan_matter_id\n        and cancelled_matter.plan_type\n            = hame.plan_type_root_value(repealing_matter.plan_type_id)\n        -- The interiors must meet, so a plan that only touches the\n        -- border of the repealing plan is not repealed.\n        and st_relate(cancelled.geom, repealing.geom, 'T********')\n$$",
)
OLD_REPEALED_PLANS = PGFunction(
    schema="hame",
    signature="repealed_plans(repealing_plan_id uuid)",
    definition="RETURNS TABLE (cancelled_plan_id uuid, cancels_entire_plan boolean)\n    STABLE\n    PARALLEL SAFE\n    LANGUAGE sql\nAS $$\n    select\n        cancelled.id,\n        st_coveredby(cancelled.geom, repealing.geom)\n    from\n        hame.plan repealing\n        join hame.plan_matter repealing_matter\n            on repealing_matter.id = repealing.plan_matter_id\n        join hame.plan_valid cancelled\n            on st_intersects(cancelled.geom, repealing.geom)\n        join hame.plan_matter_valid cancelled_matter\n            on cancelled_matter.id = cancelled.plan_matter_id\n    where\n        repealing.id = $1\n        and repealing_matter.repealing\n        and cancelled.plan_matter_id <> repealing.plan_matter_id\n        and cancelled_matter.plan_type\n            = hame.plan_type_root_value(repealing_matter.plan_type_id)\n        -- The interiors must meet, so a plan that only touches the\n        -- border of the repealing plan is not repealed.\n        and st_relate(cancelled.geom, repealing.geom, 'T********')\n$$",
)

# (view name, new definition, old definition), in dependency order: plan_valid
# first, as the plan object views select from it.
VIEWS = [
    ("plan_valid", NEW_PLAN_VALID, OLD_PLAN_VALID),
    ("land_use_area_valid", NEW_LAND_USE_AREA_VALID, OLD_LAND_USE_AREA_VALID),
    ("other_area_valid", NEW_OTHER_AREA_VALID, OLD_OTHER_AREA_VALID),
    ("line_valid", NEW_LINE_VALID, OLD_LINE_VALID),
    ("point_valid", NEW_POINT_VALID, OLD_POINT_VALID),
]


def replace_views(new: bool) -> None:
    """Replace every view and grant select on it again.

    alembic_utils falls back to DROP VIEW + CREATE VIEW when CREATE OR
    REPLACE VIEW fails, and dropping the view drops the grants with it.
    """
    for name, new_definition, old_definition in VIEWS:
        definition = new_definition if new else old_definition
        op.replace_entity(PGView(schema="hame", signature=name, definition=definition))
        op.execute(f"GRANT SELECT ON hame.{name} TO arho_read_only;")
        op.execute(f"GRANT SELECT ON hame.{name} TO arho_read_write;")


def upgrade() -> None:
    op.create_entity(INTERSECTION_ALL)
    op.replace_entity(NEW_REPEALED_PLANS)
    replace_views(new=True)


def downgrade() -> None:
    replace_views(new=False)
    op.replace_entity(OLD_REPEALED_PLANS)
    op.drop_entity(INTERSECTION_ALL)
