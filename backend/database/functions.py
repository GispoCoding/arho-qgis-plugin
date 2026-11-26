from textwrap import dedent

from alembic_utils.pg_function import PGFunction

from database.valid_views import LIFECYCLE_STATUS_VALID, valid_today

regulation_values = PGFunction(
    schema="hame",
    signature="regulation_values(table_name text, id uuid)",
    definition=dedent(
        """\
            RETURNS jsonb
            LANGUAGE 'plpgsql'
            COST 100
            STABLE PARALLEL SAFE
        AS $BODY$
        DECLARE
            return_value jsonb;
        BEGIN
            EXECUTE format(
                $SQL$
                select
                    jsonb_object_agg(
                        tpr.value,
                        (
                            select
                                jsonb_strip_nulls(to_jsonb(ai_values))
                            from
                                (
                                    select
                                        r.numeric_value,
                                        r.unit,
                                        r.numeric_range_min,
                                        r.numeric_range_max,
                                        r.text_value,
                                        r.text_syntax,
                                        r.code_title,
                                        r.code_list,
                                        r.code_value
                                ) as ai_values
                        )
                    )
                from
                    hame.regulation_group_association rga
                    join hame.plan_regulation_group rg
                        on rga.plan_regulation_group_id = rg.id
                    join hame.plan_regulation r
                        on rg.id = r.plan_regulation_group_id
                    join codes.type_of_plan_regulation tpr
                        on r.type_of_plan_regulation_id = tpr.id
                where
                    rga.%I = $1
                    AND r.value_data_type is not null
                $SQL$,
                table_name||'_id'
            )
            INTO return_value
            USING id;

            RETURN return_value;
        END;
        $BODY$;
        """
    ),
)

primary_use_regulations = PGFunction(
    schema="hame",
    signature="primary_use_regulations(land_use_area_id uuid)",
    definition=dedent(
        """\
            RETURNS jsonb
            STABLE
            PARALLEL SAFE
            LANGUAGE sql
        AS
        $$
            select
                jsonb_object_agg(
                    tpr.value,
                    coalesce(
                        (
                            select
                            jsonb_object_agg(
                                ai_type,
                                ai_values_array
                            )
                            from (
                                select
                                    tai.value ai_type,
                                    jsonb_agg(
                                        (
                                            select
                                                jsonb_strip_nulls(to_jsonb(ai_values))
                                            from
                                                (
                                                select
                                                    ai.numeric_value,
                                                    ai.unit,
                                                    ai.numeric_range_min,
                                                    ai.numeric_range_max,
                                                    ai.text_value,
                                                    ai.text_syntax,
                                                    ai.code_title,
                                                    ai.code_list,
                                                    ai.code_value
                                                ) as ai_values
                                        )
                                    ) ai_values_array
                                from
                                    hame.additional_information ai
                                    join codes.type_of_additional_information tai
                                        on ai.type_additional_information_id = tai.id
                                where
                                    ai.plan_regulation_id = r.id
                                    AND tai.value != 'paakayttotarkoitus'
                                group by tai.value
                            ) ai_values
                        ),
                        '{}'::jsonb
                    )
                )
            from
                hame.regulation_group_association rga
                join hame.plan_regulation_group rg
                    on rga.plan_regulation_group_id = rg.id
                join hame.plan_regulation r
                    on rg.id = r.plan_regulation_group_id
                join codes.type_of_plan_regulation tpr
                    on r.type_of_plan_regulation_id = tpr.id
            where
                rga.land_use_area_id = $1
                AND EXISTS (  -- select only regulations that have paakayttotarkoitus additional information
                    select
                    from hame.additional_information ai
                    where
                    ai.plan_regulation_id = r.id
                    AND ai.type_additional_information_id = (
                        select id
                        from codes.type_of_additional_information
                        where value = 'paakayttotarkoitus')
                )
        $$
        ;
        """  # noqa: E501
    ),
)


sub_area_regulations = PGFunction(
    schema="hame",
    signature="sub_area_regulations(other_area_id uuid)",
    definition=dedent(
        """\
            RETURNS jsonb
            STABLE
            PARALLEL SAFE
            LANGUAGE sql
        AS
        $$
            select
                jsonb_object_agg(
                    tpr.value,
                    coalesce(
                        (
                            select
                                jsonb_object_agg(
                                    ai_type,
                                    ai_values_array
                                )
                            from (
                                select
                                    tai.value ai_type,
                                    jsonb_agg(
                                        (
                                            select
                                                jsonb_strip_nulls(to_jsonb(ai_values))
                                            from (
                                                select
                                                        ai.numeric_value,
                                                        ai.unit,
                                                        ai.numeric_range_min,
                                                        ai.numeric_range_max,
                                                        ai.text_value,
                                                        ai.text_syntax,
                                                        ai.code_title,
                                                        ai.code_list,
                                                        ai.code_value
                                            ) as ai_values
                                        )
                                    ) as ai_values_array
                                from
                                    hame.additional_information ai
                                    join codes.type_of_additional_information tai
                                        on ai.type_additional_information_id = tai.id
                                where
                                    ai.plan_regulation_id = r.id
                                    AND tai.value != 'osaAlue'
                                group by tai.value
                            ) ai_values
                        ),
                        '{}'::jsonb
                    )
                )
            from
                hame.regulation_group_association rga
                join hame.plan_regulation_group rg
                    on rga.plan_regulation_group_id = rg.id
                join hame.plan_regulation r
                    on rg.id = r.plan_regulation_group_id
                join codes.type_of_plan_regulation tpr
                    on r.type_of_plan_regulation_id = tpr.id
            where
                rga.other_area_id = $1
                AND EXISTS (  -- select only regulations that have osaAlue additional information
                    select
                    from hame.additional_information ai
                    where
                        ai.plan_regulation_id = r.id
                        AND ai.type_additional_information_id = (
                            select id
                            from codes.type_of_additional_information
                            where value = 'osaAlue')
                )
        $$
        ;
        """  # noqa: E501
    ),
)


short_names = PGFunction(
    schema="hame",
    signature="short_names(table_name text, id uuid)",
    definition=dedent(
        """\
            RETURNS text[]
            STABLE
            PARALLEL SAFE
            LANGUAGE plpgsql
        AS
        $BODY$
        DECLARE
            return_value text[];
        BEGIN
            EXECUTE format(
                $SQL$
                SELECT array(
                    SELECT rg.short_name
                    FROM
                        hame.regulation_group_association rga
                        join hame.plan_regulation_group rg
                            on rga.plan_regulation_group_id = rg.id
                    WHERE
                        rga.%I = $1
                        AND rg.short_name is not null
                )
                $SQL$,
                table_name||'_id'
            )
            INTO return_value
            USING id;

            RETURN return_value;
        END;
        $BODY$
        ;
        """
    ),
)

type_regulations = PGFunction(
    schema="hame",
    signature="type_regulations(table_name text, id uuid)",
    definition=dedent(
        """\
            RETURNS jsonb
            STABLE
            PARALLEL SAFE
            LANGUAGE plpgsql
        AS
        $BODY$
        DECLARE
            return_value jsonb;
        BEGIN
            EXECUTE format(
                $SQL$
                select
                    jsonb_object_agg(
                        tpr.value,
                        coalesce(
                            (
                                select
                                    jsonb_object_agg(
                                        ai_type,
                                        ai_values_array
                                    )
                                from (
                                    select
                                        tai.value ai_type,
                                        jsonb_agg(
                                            (
                                                select
                                                jsonb_strip_nulls(to_jsonb(ai_values))
                                                from
                                                    (
                                                    select
                                                        ai.numeric_value,
                                                        ai.unit,
                                                        ai.numeric_range_min,
                                                        ai.numeric_range_max,
                                                        ai.text_value,
                                                        ai.text_syntax,
                                                        ai.code_title,
                                                        ai.code_list,
                                                        ai.code_value
                                                    ) as ai_values
                                            )
                                        ) as ai_values_array
                                    from
                                        hame.additional_information ai
                                        join codes.type_of_additional_information tai
                                            on ai.type_additional_information_id = tai.id
                                    where
                                        ai.plan_regulation_id = r.id
                                    group by tai.value
                                ) ai_values
                            ),
                            '{}'::jsonb
                        )
                    )
                from
                    hame.regulation_group_association rga
                    join hame.plan_regulation_group rg
                        on rga.plan_regulation_group_id = rg.id
                    join hame.plan_regulation r
                        on rg.id = r.plan_regulation_group_id
                    join codes.type_of_plan_regulation tpr
                        on r.type_of_plan_regulation_id = tpr.id
                where
                    rga.%I = $1
                    AND r.value_data_type is null
                $SQL$,
                table_name||'_id'
            )
            INTO return_value
            USING id;

            RETURN return_value;
        END;
        $BODY$
        ;
        """
    ),
)

# Kaavan kumoamistieto. The two functions below answer what the rows of
# hame.plan_cancellation_info and hame.plan_object_cancellation_info of one
# repealing plan should be. hame.refresh_plan_cancellation_info, generated in
# database/triggers.py, writes those rows into the tables.

# Maps one kaavalaji code to the level 1 code it descends from. The level 1 code
# values are 1 maakuntakaava, 2 yleiskaava and 3 asemakaava, while a plan matter
# usually refers to a lower level code such as 11 Kokonaismaakuntakaava.
# PLAN_TYPE_ROOT_CTE in database/valid_views.py answers the same question for
# every plan matter at once, by walking down from the level 1 codes instead.
plan_type_root_value = PGFunction(
    schema="hame",
    signature="plan_type_root_value(plan_type_id uuid)",
    definition=dedent(
        """\
            RETURNS text
            STABLE
            PARALLEL SAFE
            LANGUAGE sql
        AS $$
            with recursive ancestor as (
                select id, parent_id, level, value
                from codes.plan_type
                where id = $1
              union all
                select parent.id, parent.parent_id, parent.level, parent.value
                from ancestor a
                join codes.plan_type parent on parent.id = a.parent_id
            )
            select value
            from ancestor
            where level = 1
        $$;
        """
    ),
)

# A repealing plan repeals every valid plan that it overlaps and that has the
# same level 1 plan type (Ryhti rule 240). The plan matter of the repealed plan
# must be another one, so that a plan does not repeal the earlier phases of its
# own plan matter (rule 239).
#
# hame.plan_valid only says which plans are valid; the overlap and the cover
# are tested against the stored geometry of hame.plan. The view clips the
# geometry by the plans that repeal it, this one included once it is final,
# so a test against the view would make a final repealing plan miss its own
# target and hame.refresh_plan_cancellation_info would delete the row and
# write it again with a new id. Ryhti tests the cover against the stored
# geometry too (rule 245).
repealed_plans = PGFunction(
    schema="hame",
    signature="repealed_plans(repealing_plan_id uuid)",
    definition=dedent(
        """\
            RETURNS TABLE (cancelled_plan_id uuid, cancels_entire_plan boolean)
            STABLE
            PARALLEL SAFE
            LANGUAGE sql
        AS $$
            select
                cancelled.id,
                st_coveredby(cancelled.geom, repealing.geom)
            from
                hame.plan repealing
                join hame.plan_matter repealing_matter
                    on repealing_matter.id = repealing.plan_matter_id
                join hame.plan cancelled
                    on st_intersects(cancelled.geom, repealing.geom)
                join hame.plan_valid valid on valid.id = cancelled.id
                join hame.plan_matter_valid cancelled_matter
                    on cancelled_matter.id = cancelled.plan_matter_id
            where
                repealing.id = $1
                and repealing_matter.repealing
                and cancelled.plan_matter_id <> repealing.plan_matter_id
                and cancelled_matter.plan_type
                    = hame.plan_type_root_value(repealing_matter.plan_type_id)
                -- The interiors must meet, so a plan that only touches the
                -- border of the repealing plan is not repealed.
                and st_relate(cancelled.geom, repealing.geom, 'T********')
        $$;
        """
    ),
)

# The plan object columns of hame.plan_object_cancellation_info, in the order
# the table declares them. Exactly one of the four names the repealed object and
# exactly one of the three geometries is set, see CANCELLED_PLAN_OBJECT_CHECK
# and ck_plan_object_cancellation_info_remaining_valid_geom in database/models.py.
CANCELLED_PLAN_OBJECT_COLUMNS = (
    "land_use_area_id",
    "other_area_id",
    "line_id",
    "point_id",
)
REMAINING_VALID_GEOM_COLUMNS = (
    "remaining_valid_geom_polygon",
    "remaining_valid_geom_line",
    "remaining_valid_geom_point",
)

# Each plan object table with the column that names an object of it, the column
# that holds the geometry that stays valid, and the ST_CollectionExtract type
# number of its geometry (1 point, 2 line, 3 polygon). ST_Difference may return
# a collection, so the wanted type is extracted before the geometry is stored.
PLAN_OBJECT_CANCELLATION = (
    ("land_use_area", "land_use_area_id", "remaining_valid_geom_polygon", 3),
    ("other_area", "other_area_id", "remaining_valid_geom_polygon", 3),
    ("line", "line_id", "remaining_valid_geom_line", 2),
    ("point", "point_id", "remaining_valid_geom_point", 1),
)


def _repealed_plan_objects_select(
    table: str, id_column: str, geom_column: str, collection_type: int
) -> str:
    """Select the repealed objects of one plan object table.

    Every select returns the columns of hame.plan_object_cancellation_info in
    the order the table declares them, so that the four selects can be combined
    with union all. The columns of the other plan object tables and of the other
    geometry types are null.

    The objects are read from the base table instead of from the *_valid view,
    because that view selects through the visualization view, which builds the
    aggregated regulation columns for every row.
    """
    ids = ",\n                ".join(
        "o.id" if column == id_column else "null::uuid"
        for column in CANCELLED_PLAN_OBJECT_COLUMNS
    )
    # The geometry that stays valid and cancels_entire_plan_object both come
    # from the same difference, so the two can never contradict each other.
    geoms = ",\n                ".join(
        "case when st_isempty(remaining.geom) then null else remaining.geom end"
        if column == geom_column
        else "null::geometry"
        for column in REMAINING_VALID_GEOM_COLUMNS
    )
    return dedent(
        f"""\
            select
                {ids},
                st_isempty(remaining.geom),
                {geoms}
            from
                hame.{table} o
                join codes.lifecycle_status ls on ls.id = o.lifecycle_status_id
                cross join hame.plan repealing
                cross join lateral (
                    select st_multi(st_collectionextract(
                        st_difference(o.geom, repealing.geom), {collection_type}
                    )) geom
                ) remaining
            where
                repealing.id = $1
                and o.plan_id = $2
                and ls.value = '{LIFECYCLE_STATUS_VALID}'
                and {valid_today("o")}
                and st_intersects(o.geom, repealing.geom)
                and st_relate(o.geom, repealing.geom, 'T********')
        """
    )


# The plan objects of one repealed plan that the repealing plan overlaps. A plan
# object that the repealing plan covers is repealed entirely; of the others the
# part outside the repealing plan stays valid (Ryhti validityGeometry).
repealed_plan_objects = PGFunction(
    schema="hame",
    signature="repealed_plan_objects(repealing_plan_id uuid, cancelled_plan_id uuid)",
    definition=dedent(
        """\
            RETURNS TABLE (
                land_use_area_id uuid,
                other_area_id uuid,
                line_id uuid,
                point_id uuid,
                cancels_entire_plan_object boolean,
                remaining_valid_geom_polygon geometry,
                remaining_valid_geom_line geometry,
                remaining_valid_geom_point geometry
            )
            STABLE
            PARALLEL SAFE
            LANGUAGE sql
        AS $$
        """
    )
    + "union all\n".join(
        _repealed_plan_objects_select(*columns) for columns in PLAN_OBJECT_CANCELLATION
    )
    + "$$;\n",
)

# The intersection of every geometry of the array, for the valid views in
# database/valid_views.py: a plan object that several plans repeal in part keeps
# the part that every remaining valid geometry has. PostGIS has no intersection
# aggregate, so the views collect the geometries with array_agg and call this.
# Null elements are skipped, like an aggregate skips null rows, and the result
# is null when nothing is left to intersect.
intersection_all = PGFunction(
    schema="hame",
    signature="intersection_all(geoms geometry[])",
    definition=dedent(
        """\
            RETURNS geometry
            IMMUTABLE
            PARALLEL SAFE
            STRICT
            LANGUAGE plpgsql
        AS $$
        DECLARE
            result geometry;
            geom geometry;
        BEGIN
            FOREACH geom IN ARRAY geoms LOOP
                IF geom IS NULL THEN
                    CONTINUE;
                END IF;
                IF result IS NULL THEN
                    result := geom;
                ELSE
                    result := st_intersection(result, geom);
                END IF;
            END LOOP;
            RETURN result;
        END;
        $$;
        """
    ),
)

functions = [
    regulation_values,
    primary_use_regulations,
    sub_area_regulations,
    type_regulations,
    short_names,
    plan_type_root_value,
    repealed_plans,
    repealed_plan_objects,
    intersection_all,
]
