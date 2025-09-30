from textwrap import dedent

from alembic_utils.pg_function import PGFunction

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

functions = [
    regulation_values,
    primary_use_regulations,
    sub_area_regulations,
    type_regulations,
    short_names,
]
