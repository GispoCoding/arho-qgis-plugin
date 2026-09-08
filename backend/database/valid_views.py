"""Read-only views that contain only currently valid plan data.

A plan is valid when it is marked final, its lifecycle status is VALID and
its validity period covers the current date. The other views only contain
rows that belong to a valid plan; rows with their own lifecycle status and
validity period must also pass those checks themselves. The views get select
grants only, unlike the writable visualization views in views.py.

A plan that a repealing plan repeals only in part stays valid, and the plan
view shows its remaining valid geometry: the plan geometry minus the plans
that repeal it. The views derive that geometry when they are queried instead
of storing it, see docs/adr/0002-valid-views-clip-repealed-geometry.md.

The views have the columns of their base tables (for the plan object views,
the columns of the corresponding visualization view), apart from the final
column of the plan table.
"""

from collections.abc import Container, Mapping
from textwrap import dedent, indent

from alembic_utils.pg_view import PGView
from sqlalchemy import Table

from database import models
from database.base import PROJECT_SRID, Base
from database.views import plan_object_columns


def _hame_table(name: str) -> Table:
    """Look up a table of the hame schema from the model metadata."""
    return Base.metadata.tables[f"hame.{name}"]


def _all_columns(
    table: Table,
    alias: str,
    exclude: Container[str] = (),
    replace: Mapping[str, str] | None = None,
) -> str:
    """List all columns of the table for a select, qualified with the alias.

    replace maps a column name to the expression that is selected in its
    place, so that the column keeps its position in the select list.
    """
    replace = replace or {}
    return ",\n            ".join(
        replace.get(column.name, f"{alias}.{column.name}")
        for column in table.columns
        if column.name not in exclude
    )


def valid_today(alias: str) -> str:
    """Predicate that checks that the validity period covers the current date.

    A null start date is treated as -infinity and a null end date as +infinity.
    """
    return (
        f"current_date between "
        f"coalesce({alias}.period_of_validity_start, '-infinity'::date) "
        f"and coalesce({alias}.period_of_validity_end, 'infinity'::date)"
    )


# The VALID (Voimassa) code value of the kaavaelinkaari code list
# (codes.lifecycle_status.value). The code list is still a draft, so the code
# values may change. Therefore the views match the status by its code value
# at query time instead of baking a code table UUID into the view.
LIFECYCLE_STATUS_VALID = "13"
# The REPEALED (Kumoutunut) code value of the same code list, used by
# generate_plan_repealed_triggers in database/triggers.py.
LIFECYCLE_STATUS_REPEALED = "14"


def _repeal_in_force(alias: str) -> str:
    """Predicate that checks that the repealing plan has repealed what it names.

    The finalize action of ryhti_client repeals the plans and plan objects the
    cancellation infos name, so a plan repeals from the day its validity period
    starts once it is final. A repeal is one way: the lifecycle status of the
    repealing plan does not matter, so a repealing plan that is later repealed
    itself keeps the earlier repeal in force. A null start date counts as
    started.
    """
    return (
        f"{alias}.final and current_date >= "
        f"coalesce({alias}.period_of_validity_start, '-infinity'::date)"
    )


# The remaining valid geometry of a plan: its geometry minus the union of the
# geometries of the plans that repeal it. A plan that nothing repeals keeps its
# geometry, as st_union of no rows is null. The difference can be a polygon or
# a collection, so the polygons are extracted and cast back to the column type
# of hame.plan.geom, which lets CREATE OR REPLACE VIEW keep the column.
PLAN_REMAINING_VALID_GEOM = dedent(
    f"""\
    cross join lateral (
        select st_multi(st_collectionextract(
            coalesce(st_difference(p.geom, st_union(repealing.geom)), p.geom), 3
        ))::geometry(MultiPolygon, {PROJECT_SRID}) geom
        from
            hame.plan_cancellation_info ci
            join hame.plan repealing on repealing.id = ci.plan_id
        where
            ci.cancelled_plan_id = p.id
            and {_repeal_in_force("repealing")}
    ) remaining"""
)

# The final column is left out of the select list on purpose: every row of the
# view is final, so the column carries no information here. Keeping the column
# list unchanged also lets a later migration update the view with
# CREATE OR REPLACE VIEW instead of dropping every dependent view.
plan_valid = PGView(
    schema="hame",
    signature="plan_valid",
    definition=dedent(
        f"""\
        select
            {
            _all_columns(
                _hame_table("plan"),
                "p",
                exclude=("final",),
                replace={"geom": "remaining.geom"},
            )
        }
        from
            hame.plan p
            join codes.lifecycle_status ls on ls.id = p.lifecycle_status_id
            {indent(PLAN_REMAINING_VALID_GEOM, " " * 12).lstrip()}
        where
            p.final
            and ls.value = '{LIFECYCLE_STATUS_VALID}'
            and {valid_today("p")}
            and not st_isempty(remaining.geom)
        """
    ),
)


# The geometry column of hame.plan_object_cancellation_info, the
# ST_CollectionExtract type number and the PostGIS type of the geometry of each
# plan object geometry type, see REMAINING_VALID_GEOM_COLUMNS in
# database/functions.py.
PLAN_OBJECT_GEOMETRY_TYPES = {
    "polygon": ("remaining_valid_geom_polygon", 3, "MultiPolygon"),
    "line": ("remaining_valid_geom_line", 2, "MultiLineString"),
    "point": ("remaining_valid_geom_point", 1, "MultiPoint"),
}


def _plan_object_remaining_valid_geom(name: str, geometry_type: str) -> str:
    """The lateral subquery that derives the remaining valid geometry of t.

    Every cancellation info in force that names the plan object stores the
    part of it that stays valid, and the object keeps the part they all share.
    An object that no cancellation info names keeps its geometry, as
    array_agg of no rows is null. repealed_entirely tells whether a
    cancellation info in force repeals the whole object: such an object has no
    geometry left.
    The intersection can be a collection, so the wanted type is extracted and
    cast back to the type of the geometry column of the base table.
    """
    geom_column, collection_type, postgis_type = PLAN_OBJECT_GEOMETRY_TYPES[
        geometry_type
    ]
    return dedent(
        f"""\
        cross join lateral (
            select
                bool_or(oci.cancels_entire_plan_object) repealed_entirely,
                st_multi(st_collectionextract(
                    coalesce(
                        hame.intersection_all(array_agg(oci.{geom_column})),
                        t.geom
                    ),
                    {collection_type}
                ))::geometry({postgis_type}, {PROJECT_SRID}) geom
            from
                hame.plan_object_cancellation_info oci
                join hame.plan_cancellation_info ci
                    on ci.id = oci.plan_cancellation_info_id
                join hame.plan repealing on repealing.id = ci.plan_id
            where
                oci.{name}_id = t.id
                and {_repeal_in_force("repealing")}
        ) remaining"""
    )


def _plan_object_valid_view(
    name: str, extra_columns: tuple[str, ...], geometry_type: str
) -> PGView:
    """View of the plan objects of valid plans that are themselves valid today.

    Selects from the corresponding visualization view in views.py, so the
    aggregated regulation columns are included. extra_columns names those
    view-only columns on top of plan_object_columns. Plan objects with a null
    plan_id are left out: an object that is not attached to any plan cannot
    belong to a valid plan. geometry_type is a key of PLAN_OBJECT_GEOMETRY_TYPES
    and picks the remaining valid geometry column of the cancellation infos.

    A plan object that a repealing plan repeals only in part is shown with its
    remaining valid geometry; one that a repealing plan repeals entirely, or
    that has no geometry left, is left out.
    """
    columns = ",\n                ".join(
        "remaining.geom" if column == "geom" else f"t.{column}"
        for column in (*plan_object_columns, *extra_columns)
    )
    remaining = _plan_object_remaining_valid_geom(name, geometry_type)
    return PGView(
        schema="hame",
        signature=f"{name}_valid",
        definition=dedent(
            f"""\
            select
                {columns}
            from
                hame.{name}_v t
                join hame.plan_valid p on p.id = t.plan_id
                join codes.lifecycle_status ls on ls.id = t.lifecycle_status_id
                {indent(remaining, " " * 16).lstrip()}
            where
                ls.value = '{LIFECYCLE_STATUS_VALID}'
                and {valid_today("t")}
                and not coalesce(remaining.repealed_entirely, false)
                and not st_isempty(remaining.geom)
            """
        ),
    )


land_use_area_valid = _plan_object_valid_view(
    "land_use_area",
    ("short_names", "primary_use", "regulation_values"),
    geometry_type="polygon",
)
other_area_valid = _plan_object_valid_view(
    "other_area",
    ("short_names", "sub_area", "regulation_values"),
    geometry_type="polygon",
)
line_valid = _plan_object_valid_view(
    "line",
    ("short_names", "type_regulations", "regulation_values"),
    geometry_type="line",
)
point_valid = _plan_object_valid_view(
    "point",
    ("short_names", "type_regulations", "regulation_values"),
    geometry_type="point",
)

plan_regulation_group_valid = PGView(
    schema="hame",
    signature="plan_regulation_group_valid",
    definition=dedent(
        f"""\
        select
            {_all_columns(_hame_table("plan_regulation_group"), "g")}
        from
            hame.plan_regulation_group g
            join hame.plan_valid p on p.id = g.plan_id
        """
    ),
)


def _regulation_valid_view(table: Table) -> PGView:
    """View of the regulations of valid plans that are themselves valid today."""
    return PGView(
        schema="hame",
        signature=f"{table.name}_valid",
        definition=dedent(
            f"""\
            select
                {_all_columns(table, "r")}
            from
                hame.{table.name} r
                join hame.plan_regulation_group_valid g
                    on g.id = r.plan_regulation_group_id
                join codes.lifecycle_status ls on ls.id = r.lifecycle_status_id
            where
                ls.value = '{LIFECYCLE_STATUS_VALID}'
                and {valid_today("r")}
            """
        ),
    )


plan_regulation_valid = _regulation_valid_view(_hame_table("plan_regulation"))
plan_proposition_valid = _regulation_valid_view(_hame_table("plan_proposition"))

additional_information_valid = PGView(
    schema="hame",
    signature="additional_information_valid",
    definition=dedent(
        f"""\
        select
            {_all_columns(_hame_table("additional_information"), "ai")}
        from
            hame.additional_information ai
            join hame.plan_regulation_valid r on r.id = ai.plan_regulation_id
        """
    ),
)

document_valid = PGView(
    schema="hame",
    signature="document_valid",
    definition=dedent(
        f"""\
        select
            {_all_columns(_hame_table("document"), "d")}
        from
            hame.document d
            join hame.plan_valid p on p.id = d.plan_id
        """
    ),
)

# An association row is included when its regulation group belongs to a valid
# plan and the linked target (the plan itself or a plan object) is also valid.
# Exactly one of the link columns is set; exists is false for null links.
regulation_group_association_valid = PGView(
    schema="hame",
    signature="regulation_group_association_valid",
    definition=dedent(
        f"""\
        select
            {_all_columns(models.regulation_group_association, "a")}
        from
            hame.regulation_group_association a
            join hame.plan_regulation_group_valid g
                on g.id = a.plan_regulation_group_id
        where
            exists (select 1 from hame.plan_valid p
                where p.id = a.plan_id)
            or exists (select 1 from hame.land_use_area_valid t
                where t.id = a.land_use_area_id)
            or exists (select 1 from hame.other_area_valid t
                where t.id = a.other_area_id)
            or exists (select 1 from hame.line_valid t
                where t.id = a.line_id)
            or exists (select 1 from hame.point_valid t
                where t.id = a.point_id)
        """
    ),
)

legal_effects_association_valid = PGView(
    schema="hame",
    signature="legal_effects_association_valid",
    definition=dedent(
        f"""\
        select
            {_all_columns(models.legal_effects_association, "a")}
        from
            hame.legal_effects_association a
            join hame.plan_valid p on p.id = a.plan_id
        """
    ),
)

plan_theme_association_valid = PGView(
    schema="hame",
    signature="plan_theme_association_valid",
    definition=dedent(
        f"""\
        select
            {_all_columns(models.plan_theme_association, "a")}
        from
            hame.plan_theme_association a
        where
            exists (select 1 from hame.plan_regulation_valid r
                where r.id = a.plan_regulation_id)
            or exists (select 1 from hame.plan_proposition_valid pp
                where pp.id = a.plan_proposition_id)
        """
    ),
)

type_of_verbal_regulation_association_valid = PGView(
    schema="hame",
    signature="type_of_verbal_regulation_association_valid",
    definition=dedent(
        f"""\
        select
            {_all_columns(models.type_of_verbal_regulation_association, "a")}
        from
            hame.type_of_verbal_regulation_association a
            join hame.plan_regulation_valid r on r.id = a.plan_regulation_id
        """
    ),
)

# Maps every kaavalaji code to the level 1 code it descends from. The level 1
# code values are 1 maakuntakaava, 2 yleiskaava and 3 asemakaava, while a plan
# matter usually refers to a lower level code such as 11 Kokonaismaakuntakaava.
# The anchor is the level 1 codes and the recursive step walks down through
# parent_id, so the level 1 code is one join instead of a walk up the chain for
# every row. level is imported from the RYTJ hierarchyLevel field, see
# lambdas/koodistot_loader/koodistot_loader.py.
PLAN_TYPE_ROOT_CTE = dedent(
    """\
    with recursive plan_type_root as (
        select id, id root_id
        from codes.plan_type
        where level = 1
      union all
        select child.id, r.root_id
        from plan_type_root r
        join codes.plan_type child on child.parent_id = r.id
    )"""
)

# plan_type is the last column, so every earlier column keeps its position and a
# migration can update the view with CREATE OR REPLACE VIEW instead of dropping
# it. The plan type joins are left joins, so a plan matter stays in the view with
# a null plan_type even if its code has no level 1 ancestor.
plan_matter_valid = PGView(
    schema="hame",
    signature="plan_matter_valid",
    # The CTE is concatenated instead of interpolated, so that dedent only ever
    # sees the uniformly indented part of the statement.
    definition=PLAN_TYPE_ROOT_CTE
    + dedent(
        f"""
        select
            {_all_columns(_hame_table("plan_matter"), "m")},
            root.value plan_type
        from
            hame.plan_matter m
            left join plan_type_root ptr on ptr.id = m.plan_type_id
            left join codes.plan_type root on root.id = ptr.root_id
        where
            exists (select 1 from hame.plan_valid p
                where p.plan_matter_id = m.id)
        """
    ),
)

valid_views = [
    plan_valid,
    land_use_area_valid,
    other_area_valid,
    line_valid,
    point_valid,
    plan_regulation_group_valid,
    plan_regulation_valid,
    plan_proposition_valid,
    additional_information_valid,
    document_valid,
    regulation_group_association_valid,
    legal_effects_association_valid,
    plan_theme_association_valid,
    type_of_verbal_regulation_association_valid,
    plan_matter_valid,
]
