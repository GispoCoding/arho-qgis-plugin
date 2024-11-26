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
):
    # non-nullable plan object relations
    assert land_use_area_instance.lifecycle_status is preparation_status_instance
    assert preparation_status_instance.land_use_areas == [land_use_area_instance]
    assert land_use_area_instance.type_of_underground is type_of_underground_instance
    assert type_of_underground_instance.land_use_areas == [land_use_area_instance]
    assert land_use_area_instance.plan is plan_instance
    assert plan_instance.land_use_areas == [land_use_area_instance]
    assert land_use_area_instance.plan_regulation_groups == [
        plan_regulation_group_instance
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
    type_of_additional_information_instance: codes.TypeOfAdditionalInformation,
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
    # All eight additional information regulations are nullable
    # Käyttötarkoitus
    assert text_plan_regulation_instance.intended_use is None
    assert type_of_additional_information_instance.intended_use_plan_regulations == []
    text_plan_regulation_instance.intended_use = type_of_additional_information_instance
    # Olemassaolo
    assert text_plan_regulation_instance.existence is None
    assert type_of_additional_information_instance.existence_plan_regulations == []
    text_plan_regulation_instance.existence = type_of_additional_information_instance
    # Tyyppi (lisätiedon laji)
    assert text_plan_regulation_instance.regulation_type_additional_information is None
    assert type_of_additional_information_instance.type_plan_regulations == []
    text_plan_regulation_instance.regulation_type_additional_information = (
        type_of_additional_information_instance
    )
    # Merkittävyys
    assert text_plan_regulation_instance.significance is None
    assert type_of_additional_information_instance.significance_plan_regulations == []
    text_plan_regulation_instance.significance = type_of_additional_information_instance
    # Eri tahojen tarpeisiin varaus
    assert text_plan_regulation_instance.reservation is None
    assert type_of_additional_information_instance.reservation_plan_regulations == []
    text_plan_regulation_instance.reservation = type_of_additional_information_instance
    # Kehittäminen
    assert text_plan_regulation_instance.development is None
    assert type_of_additional_information_instance.development_plan_regulations == []
    text_plan_regulation_instance.development = type_of_additional_information_instance
    # Häiriön torjuntatarve
    assert text_plan_regulation_instance.disturbance_prevention is None
    assert (
        type_of_additional_information_instance.disturbance_prevention_plan_regulations
        == []
    )
    text_plan_regulation_instance.disturbance_prevention = (
        type_of_additional_information_instance
    )
    # Rakentamisen ohjaus
    assert text_plan_regulation_instance.construction_control is None
    assert (
        type_of_additional_information_instance.construction_control_plan_regulations
        == []
    )
    text_plan_regulation_instance.construction_control = (
        type_of_additional_information_instance
    )

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
    # Käyttötarkoitus
    assert (
        text_plan_regulation_instance.intended_use
        is type_of_additional_information_instance
    )
    assert type_of_additional_information_instance.intended_use_plan_regulations == [
        text_plan_regulation_instance
    ]
    # Olemassaolo
    assert (
        text_plan_regulation_instance.existence
        is type_of_additional_information_instance
    )
    assert type_of_additional_information_instance.existence_plan_regulations == [
        text_plan_regulation_instance
    ]
    # Tyyppi (lisätiedon laji)
    assert (
        text_plan_regulation_instance.regulation_type_additional_information
        is type_of_additional_information_instance
    )
    assert type_of_additional_information_instance.type_plan_regulations == [
        text_plan_regulation_instance
    ]
    # Merkittävyys
    assert (
        text_plan_regulation_instance.significance
        is type_of_additional_information_instance
    )
    assert type_of_additional_information_instance.significance_plan_regulations == [
        text_plan_regulation_instance
    ]
    # Eri tahojen tarpeisiin varaus
    assert (
        text_plan_regulation_instance.reservation
        is type_of_additional_information_instance
    )
    assert type_of_additional_information_instance.reservation_plan_regulations == [
        text_plan_regulation_instance
    ]
    # Kehittäminen
    assert (
        text_plan_regulation_instance.development
        is type_of_additional_information_instance
    )
    assert type_of_additional_information_instance.development_plan_regulations == [
        text_plan_regulation_instance
    ]
    # Häiriön torjuntatarve
    assert (
        text_plan_regulation_instance.disturbance_prevention
        is type_of_additional_information_instance
    )
    assert (
        type_of_additional_information_instance.disturbance_prevention_plan_regulations
        == [text_plan_regulation_instance]
    )
    # Rakentamisen ohjaus
    assert (
        text_plan_regulation_instance.construction_control
        is type_of_additional_information_instance
    )
    assert (
        type_of_additional_information_instance.disturbance_prevention_plan_regulations
        == [text_plan_regulation_instance]
    )


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
    document_instance: models.Document,
    type_of_document_instance: codes.TypeOfDocument,
    plan_instance: models.Plan,
):
    # non-nullable document relations
    assert document_instance.type_of_document is type_of_document_instance
    assert type_of_document_instance.documents == [document_instance]
    assert document_instance.plan is plan_instance
    assert plan_instance.documents == [document_instance]
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
