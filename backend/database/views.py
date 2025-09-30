from textwrap import dedent

from alembic_utils.pg_view import PGView

land_use_area_v = PGView(
    schema="hame",
    signature="land_use_area_v",
    definition=dedent(
        """\
        select
            *,
            hame.short_names('land_use_area', id) short_names,
            hame.primary_use_regulations(id) primary_use,
            hame.regulation_values('land_use_area', id) regulation_values
        from
            hame.land_use_area
        """
    ),
)

other_area_v = PGView(
    schema="hame",
    signature="other_area_v",
    definition=dedent(
        """\
        select
            *,
            hame.short_names('other_area', id) short_names,
            hame.sub_area_regulations(id) sub_area,
            hame.regulation_values('other_area', id) regulation_values
        from
            hame.other_area
        """
    ),
)

line_v = PGView(
    schema="hame",
    signature="line_v",
    definition=dedent(
        """\
        select
            *,
            hame.short_names('line', id) short_names,
            hame.type_regulations('line', id) type_regulations,
            hame.regulation_values('line', id) regulation_values
        from
            hame.line
        """
    ),
)

point_v = PGView(
    schema="hame",
    signature="point_v",
    definition=dedent(
        """\
        select
            *,
            hame.short_names('point', id) short_names,
            hame.type_regulations('point', id) type_regulations,
            hame.regulation_values('point', id) regulation_values
        from
            hame.point
        """
    ),
)


views = [land_use_area_v, other_area_v, line_v, point_v]
