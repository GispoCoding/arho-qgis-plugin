import codes
import models
from sqlalchemy.orm import Session

"""Tests that check all relationships in sqlalchemy classes are defined correctly.
This caused a lot of trouble with koodistot loader.

When non-nullable fields or relations are added, the fixtures must be updated accordingly."""


def test_codes(
    session: Session,
    code_instance: codes.LifeCycleStatus,
    another_code_instance: codes.LifeCycleStatus,
):
    # nullable code relations
    assert code_instance.parent is None
    assert code_instance.children == []
    assert another_code_instance.parent is None
    assert another_code_instance.children == []
    another_code_instance.parent = code_instance
    session.flush()
    assert code_instance.parent is None
    assert code_instance.children == [another_code_instance]
    assert another_code_instance.parent is code_instance
    assert another_code_instance.children == []
    session.rollback()


def test_plan(
    plan_instance: models.Plan,
    preparation_status_instance: codes.LifeCycleStatus,
    organisation_instance: models.Organisation,
    general_regulation_group_instance: models.PlanRegulationGroup,
    plan_type_instance: codes.PlanType,
):
    # non-nullable plan relations
    assert plan_instance.lifecycle_status is preparation_status_instance
    assert preparation_status_instance.plans == [plan_instance]
    assert plan_instance.organisation is organisation_instance
    assert organisation_instance.plans == [plan_instance]
    assert plan_instance.plan_type is plan_type_instance
    assert plan_type_instance.plans == [plan_instance]

    # Let's not change plan instance lifecycle status here. It's just asking
    # for trouble, and we will test all those triggers in test_triggers anyway.
    # nullable plan relations
    assert plan_instance.general_plan_regulation_groups == [
        general_regulation_group_instance
    ]

    # General regulation group belongs to the plan
    assert general_regulation_group_instance.plan == plan_instance


def test_land_use_area(
    land_use_area_instance: models.LandUseArea,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: models.Plan,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    numeric_plan_regulation_group_instance: models.PlanRegulationGroup,
):
    # non-nullable plan object relations
    assert land_use_area_instance.lifecycle_status is preparation_status_instance
    assert preparation_status_instance.land_use_areas == [land_use_area_instance]
    assert land_use_area_instance.type_of_underground is type_of_underground_instance
    assert type_of_underground_instance.land_use_areas == [land_use_area_instance]
    assert land_use_area_instance.plan is plan_instance
    assert plan_instance.land_use_areas == [land_use_area_instance]
    assert land_use_area_instance.plan_regulation_groups == [
        numeric_plan_regulation_group_instance,
        plan_regulation_group_instance,
    ]

    assert plan_regulation_group_instance.land_use_areas == [land_use_area_instance]


def test_other_area(
    other_area_instance: models.OtherArea,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: models.Plan,
    plan_regulation_group_instance: models.PlanRegulationGroup,
):
    # non-nullable plan object relations
    assert other_area_instance.lifecycle_status is preparation_status_instance
    assert preparation_status_instance.other_areas == [other_area_instance]
    assert other_area_instance.type_of_underground is type_of_underground_instance
    assert type_of_underground_instance.other_areas == [other_area_instance]
    assert other_area_instance.plan is plan_instance
    assert plan_instance.other_areas == [other_area_instance]
    assert other_area_instance.plan_regulation_groups == [
        plan_regulation_group_instance
    ]
    assert plan_regulation_group_instance.other_areas == [other_area_instance]


def test_line(
    line_instance: models.Line,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: models.Plan,
    plan_regulation_group_instance: models.PlanRegulationGroup,
):
    # non-nullable plan object relations
    assert line_instance.lifecycle_status is preparation_status_instance
    assert preparation_status_instance.lines == [line_instance]
    assert line_instance.type_of_underground is type_of_underground_instance
    assert type_of_underground_instance.lines == [line_instance]
    assert line_instance.plan is plan_instance
    assert plan_instance.lines == [line_instance]
    assert line_instance.plan_regulation_groups == [plan_regulation_group_instance]
    assert plan_regulation_group_instance.lines == [line_instance]


def test_land_use_point(
    land_use_point_instance: models.LandUsePoint,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: models.Plan,
    point_plan_regulation_group_instance: models.PlanRegulationGroup,
):
    # non-nullable plan object relations
    assert land_use_point_instance.lifecycle_status is preparation_status_instance
    assert preparation_status_instance.land_use_points == [land_use_point_instance]
    assert land_use_point_instance.type_of_underground is type_of_underground_instance
    assert type_of_underground_instance.land_use_points == [land_use_point_instance]
    assert land_use_point_instance.plan is plan_instance
    assert plan_instance.land_use_points == [land_use_point_instance]
    assert land_use_point_instance.plan_regulation_groups == [
        point_plan_regulation_group_instance
    ]

    assert point_plan_regulation_group_instance.land_use_points == [
        land_use_point_instance
    ]


def test_other_point(
    other_point_instance: models.OtherPoint,
    preparation_status_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: models.Plan,
    point_plan_regulation_group_instance: models.PlanRegulationGroup,
):
    # non-nullable plan object relations
    assert other_point_instance.lifecycle_status is preparation_status_instance
    assert preparation_status_instance.other_points == [other_point_instance]
    assert other_point_instance.type_of_underground is type_of_underground_instance
    assert type_of_underground_instance.other_points == [other_point_instance]
    assert other_point_instance.plan is plan_instance
    assert plan_instance.other_points == [other_point_instance]
    assert other_point_instance.plan_regulation_groups == [
        point_plan_regulation_group_instance
    ]

    assert point_plan_regulation_group_instance.other_points == [other_point_instance]


def test_plan_regulation_group(
    plan_regulation_group_instance: models.PlanRegulationGroup,
    type_of_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
):
    # non-nullable plan regulation group relations
    assert (
        plan_regulation_group_instance.type_of_plan_regulation_group
        is type_of_plan_regulation_group_instance
    )
    assert (
        plan_regulation_group_instance
        in type_of_plan_regulation_group_instance.plan_regulation_groups
    )


def test_plan_regulation(
    session: Session,
    text_plan_regulation_instance: models.PlanRegulation,
    preparation_status_instance: codes.LifeCycleStatus,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    type_of_plan_regulation_instance: codes.TypeOfPlanRegulation,
    type_of_verbal_plan_regulation_instance: codes.TypeOfVerbalPlanRegulation,
    plan_theme_instance: codes.PlanTheme,
):
    # non-nullable plan regulation relations
    assert text_plan_regulation_instance.lifecycle_status is preparation_status_instance
    assert preparation_status_instance.plan_regulations == [
        text_plan_regulation_instance
    ]
    assert (
        text_plan_regulation_instance.plan_regulation_group
        is plan_regulation_group_instance
    )
    assert plan_regulation_group_instance.plan_regulations == [
        text_plan_regulation_instance
    ]
    assert (
        text_plan_regulation_instance.type_of_plan_regulation
        is type_of_plan_regulation_instance
    )
    assert type_of_plan_regulation_instance.plan_regulations == [
        text_plan_regulation_instance
    ]
    # nullable plan regulation relations
    assert text_plan_regulation_instance.type_of_verbal_plan_regulation is None
    assert type_of_verbal_plan_regulation_instance.plan_regulations == []
    assert text_plan_regulation_instance.plan_theme is None
    assert plan_theme_instance.plan_regulations == []
    text_plan_regulation_instance.type_of_verbal_plan_regulation = (
        type_of_verbal_plan_regulation_instance
    )
    text_plan_regulation_instance.plan_theme = plan_theme_instance

    assert text_plan_regulation_instance.additional_information == []

    session.flush()

    assert (
        text_plan_regulation_instance.type_of_verbal_plan_regulation
        is type_of_verbal_plan_regulation_instance
    )
    assert type_of_verbal_plan_regulation_instance.plan_regulations == [
        text_plan_regulation_instance
    ]
    assert text_plan_regulation_instance.plan_theme is plan_theme_instance
    assert plan_theme_instance.plan_regulations == [text_plan_regulation_instance]


def test_additional_information(
    main_use_additional_information_instance: models.AdditionalInformation,
    empty_value_plan_regulation_instance: models.PlanRegulation,
    type_of_main_use_additional_information_instance: codes.TypeOfAdditionalInformation,
):
    assert (
        main_use_additional_information_instance.type_of_additional_information
        is type_of_main_use_additional_information_instance
    )
    assert (
        main_use_additional_information_instance.plan_regulation
        is empty_value_plan_regulation_instance
    )

    assert empty_value_plan_regulation_instance.additional_information == [
        main_use_additional_information_instance
    ]


def test_plan_proposition(
    session: Session,
    plan_proposition_instance: models.PlanProposition,
    preparation_status_instance: codes.LifeCycleStatus,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    plan_theme_instance: codes.PlanTheme,
):
    # non-nullable plan proposition relations
    assert plan_proposition_instance.lifecycle_status is preparation_status_instance
    assert preparation_status_instance.plan_propositions == [plan_proposition_instance]
    assert (
        plan_proposition_instance.plan_regulation_group
        is plan_regulation_group_instance
    )
    assert plan_regulation_group_instance.plan_propositions == [
        plan_proposition_instance
    ]
    # nullable plan proposition relations
    assert plan_proposition_instance.plan_theme is None
    assert plan_theme_instance.plan_propositions == []
    plan_proposition_instance.plan_theme = plan_theme_instance

    session.flush()

    assert plan_proposition_instance.plan_theme is plan_theme_instance
    assert plan_theme_instance.plan_propositions == [plan_proposition_instance]


def test_source_data(
    session: Session,
    source_data_instance: models.SourceData,
    type_of_source_data_instance: codes.TypeOfSourceData,
    plan_instance: models.Plan,
):
    # non-nullable source data relations
    assert source_data_instance.plan is plan_instance
    assert plan_instance.source_data == [source_data_instance]
    assert source_data_instance.type_of_source_data is type_of_source_data_instance
    assert type_of_source_data_instance.source_data == [source_data_instance]


def test_organisation(
    session: Session,
    organisation_instance: models.Organisation,
    administrative_region_instance: codes.AdministrativeRegion,
):
    # non-nullable organisation relations
    assert organisation_instance.administrative_region is administrative_region_instance
    assert administrative_region_instance.organisations == [organisation_instance]
    session.flush()


def test_document(
    session: Session,
    plan_map_instance: models.Document,
    type_of_document_plan_map_instance: codes.TypeOfDocument,
    category_of_publicity_public_instance: codes.CategoryOfPublicity,
    personal_data_content_no_personal_data_instance: codes.PersonalDataContent,
    retention_time_permanent_instance: codes.RetentionTime,
    language_finnish_instance: codes.Language,
    plan_instance: models.Plan,
):
    # non-nullable document relations
    assert plan_map_instance.type_of_document is type_of_document_plan_map_instance
    assert type_of_document_plan_map_instance.documents == [plan_map_instance]
    assert plan_map_instance.plan is plan_instance
    assert plan_instance.documents == [plan_map_instance]
    assert (
        plan_map_instance.category_of_publicity is category_of_publicity_public_instance
    )
    assert category_of_publicity_public_instance.documents == [plan_map_instance]
    assert (
        plan_map_instance.personal_data_content
        is personal_data_content_no_personal_data_instance
    )
    assert personal_data_content_no_personal_data_instance.documents == [
        plan_map_instance
    ]
    assert plan_map_instance.retention_time is retention_time_permanent_instance
    assert retention_time_permanent_instance.documents == [plan_map_instance]
    assert plan_map_instance.language is language_finnish_instance
    assert language_finnish_instance.documents == [plan_map_instance]
    session.flush()


def test_lifecycle_date(
    session: Session,
    lifecycle_date_instance: models.LifeCycleDate,
    code_instance: codes.LifeCycleStatus,
    plan_instance: models.Plan,
    text_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
):
    # non-nullable lifecycle date relations
    assert lifecycle_date_instance.lifecycle_status is code_instance
    assert code_instance.lifecycle_dates == [lifecycle_date_instance]
    # nullable lifecycle date relations
    assert lifecycle_date_instance.plan is None
    assert plan_instance.lifecycle_dates == []
    lifecycle_date_instance.plan = plan_instance
    assert lifecycle_date_instance.plan_regulation is None
    assert text_plan_regulation_instance.lifecycle_dates == []
    lifecycle_date_instance.plan_regulation = text_plan_regulation_instance
    assert lifecycle_date_instance.plan_proposition is None
    assert plan_proposition_instance.lifecycle_dates == []
    lifecycle_date_instance.plan_proposition = plan_proposition_instance
    session.flush()

    assert lifecycle_date_instance.plan is plan_instance
    assert lifecycle_date_instance.plan_regulation is text_plan_regulation_instance
    assert lifecycle_date_instance.plan_proposition is plan_proposition_instance
    assert lifecycle_date_instance in plan_instance.lifecycle_dates
    assert lifecycle_date_instance in text_plan_regulation_instance.lifecycle_dates
    assert lifecycle_date_instance in plan_proposition_instance.lifecycle_dates


def test_decision_date(
    session: Session,
    preparation_date_instance: models.LifeCycleDate,
    decision_date_instance: models.EventDate,
    participation_plan_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
):
    # non-nullable decision date relations
    assert decision_date_instance.lifecycle_date is preparation_date_instance
    assert preparation_date_instance.event_dates == [decision_date_instance]

    # nullable decision date relations
    assert (
        decision_date_instance.decision
        == participation_plan_presenting_for_public_decision
    )
    assert participation_plan_presenting_for_public_decision.event_dates == [
        decision_date_instance
    ]


def test_processing_event_date(
    session: Session,
    preparation_date_instance: models.LifeCycleDate,
    processing_event_date_instance: models.EventDate,
    participation_plan_presenting_for_public_event: codes.TypeOfProcessingEvent,
):
    # non-nullable decision date relations
    assert processing_event_date_instance.lifecycle_date is preparation_date_instance
    assert preparation_date_instance.event_dates == [processing_event_date_instance]

    # nullable decision date relations
    assert (
        processing_event_date_instance.processing_event
        == participation_plan_presenting_for_public_event
    )
    assert participation_plan_presenting_for_public_event.event_dates == [
        processing_event_date_instance
    ]


def test_interaction_event_date(
    session: Session,
    preparation_date_instance: models.LifeCycleDate,
    interaction_event_date_instance: models.EventDate,
    presentation_to_the_public_interaction: codes.TypeOfProcessingEvent,
):
    # non-nullable decision date relations
    assert interaction_event_date_instance.lifecycle_date is preparation_date_instance
    assert preparation_date_instance.event_dates == [interaction_event_date_instance]

    # nullable decision date relations
    assert (
        interaction_event_date_instance.interaction_event
        == presentation_to_the_public_interaction
    )
    assert presentation_to_the_public_interaction.event_dates == [
        interaction_event_date_instance
    ]
