"""Read-only views that contain only currently valid plan data.

A plan is valid when it is marked final, its lifecycle status is VALID and
its validity period covers the current date. The other views only contain
rows that belong to a valid plan; rows with their own lifecycle status and
validity period must also pass those checks themselves. The views get select
grants only, unlike the writable visualization views in views.py.

The views have the columns of their base tables (for the plan object views,
the columns of the corresponding visualization view), apart from the final
column of the plan table.
"""

from collections.abc import Container
from textwrap import dedent

from alembic_utils.pg_view import PGView
from sqlalchemy import Table

from database import models
from database.base import Base
from database.views import plan_object_columns


def _hame_table(name: str) -> Table:
    """Look up a table of the hame schema from the model metadata."""
    return Base.metadata.tables[f"hame.{name}"]


def _all_columns(table: Table, alias: str, exclude: Container[str] = ()) -> str:
    """List all columns of the table for a select, qualified with the alias."""
    return ",\n            ".join(
        f"{alias}.{column.name}"
        for column in table.columns
        if column.name not in exclude
    )


def _valid_today(alias: str) -> str:
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
            {_all_columns(_hame_table("plan"), "p", exclude=("final",))}
        from
            hame.plan p
            join codes.lifecycle_status ls on ls.id = p.lifecycle_status_id
        where
            p.final
            and ls.value = '{LIFECYCLE_STATUS_VALID}'
            and {_valid_today("p")}
        """
    ),
)


def _plan_object_valid_view(name: str, extra_columns: tuple[str, ...]) -> PGView:
    """View of the plan objects of valid plans that are themselves valid today.

    Selects from the corresponding visualization view in views.py, so the
    aggregated regulation columns are included. extra_columns names those
    view-only columns on top of plan_object_columns. Plan objects with a null
    plan_id are left out: an object that is not attached to any plan cannot
    belong to a valid plan.
    """
    columns = ",\n                ".join(
        f"t.{column}" for column in (*plan_object_columns, *extra_columns)
    )
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
            where
                ls.value = '{LIFECYCLE_STATUS_VALID}'
                and {_valid_today("t")}
            """
        ),
    )


land_use_area_valid = _plan_object_valid_view(
    "land_use_area", ("short_names", "primary_use", "regulation_values")
)
other_area_valid = _plan_object_valid_view(
    "other_area", ("short_names", "sub_area", "regulation_values")
)
line_valid = _plan_object_valid_view(
    "line", ("short_names", "type_regulations", "regulation_values")
)
point_valid = _plan_object_valid_view(
    "point", ("short_names", "type_regulations", "regulation_values")
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
                and {_valid_today("r")}
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
