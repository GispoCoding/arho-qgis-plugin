import codes
import models
from sqlalchemy.orm import Session

"""Tests that check all relationships in sqlalchemy classes are defined correctly.
This caused a lot of trouble with koodistot loader.

Also, flushing all the fixtures catches any fixtures that have null fields that
should be not-null, so we know our fixtures work with the current state of the
database, i.e. our fixtures are not missing any required fields.

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
    session: Session,
    plan_instance: models.Plan,
    code_instance: codes.LifeCycleStatus,
    another_code_instance: codes.LifeCycleStatus,
    organisation_instance: models.Organisation,
):
    # non-nullable plan relations
    assert plan_instance.lifecycle_status is code_instance
    assert code_instance.plans == [plan_instance]
    assert plan_instance.organisation is organisation_instance
    assert organisation_instance.plans == [plan_instance]
    plan_instance.lifecycle_status = another_code_instance
    session.flush()
    assert plan_instance.lifecycle_status is another_code_instance
    assert another_code_instance.plans == [plan_instance]


def test_plan_object(
    session: Session,
    land_use_area_instance: models.LandUseArea,
    code_instance: codes.LifeCycleStatus,
    type_of_underground_instance: codes.TypeOfUnderground,
    plan_instance: models.Plan,
    plan_regulation_group_instance: models.PlanRegulationGroup,
):
    # non-nullable plan object relations
    assert land_use_area_instance.lifecycle_status is code_instance
    assert code_instance.land_use_areas == [land_use_area_instance]
    assert land_use_area_instance.type_of_underground is type_of_underground_instance
    assert type_of_underground_instance.land_use_areas == [land_use_area_instance]
    assert land_use_area_instance.plan is plan_instance
    assert plan_instance.land_use_areas == [land_use_area_instance]
    assert (
        land_use_area_instance.plan_regulation_group is plan_regulation_group_instance
    )
    assert plan_regulation_group_instance.land_use_areas == [land_use_area_instance]
    session.flush()


def test_plan_regulation_group(
    session: Session,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    type_of_plan_regulation_group_instance: codes.TypeOfPlanRegulationGroup,
):
    # non-nullable plan regulation group relations
    assert (
        plan_regulation_group_instance.type_of_plan_regulation_group
        is type_of_plan_regulation_group_instance
    )
    assert type_of_plan_regulation_group_instance.plan_regulation_groups == [
        plan_regulation_group_instance
    ]
    session.flush()


def test_plan_regulation(
    session: Session,
    plan_regulation_instance: models.PlanRegulation,
    code_instance: codes.LifeCycleStatus,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    type_of_plan_regulation_instance: codes.TypeOfPlanRegulation,
    type_of_verbal_plan_regulation_instance: codes.TypeOfVerbalPlanRegulation,
    type_of_additional_information_instance: codes.TypeOfAdditionalInformation,
):
    # non-nullable plan regulation relations
    assert plan_regulation_instance.lifecycle_status is code_instance
    assert code_instance.plan_regulations == [plan_regulation_instance]
    assert (
        plan_regulation_instance.plan_regulation_group is plan_regulation_group_instance
    )
    assert plan_regulation_group_instance.plan_regulations == [plan_regulation_instance]
    assert (
        plan_regulation_instance.type_of_plan_regulation
        is type_of_plan_regulation_instance
    )
    assert type_of_plan_regulation_instance.plan_regulations == [
        plan_regulation_instance
    ]
    # nullable plan regulation relations
    assert plan_regulation_instance.type_of_verbal_plan_regulation is None
    assert type_of_verbal_plan_regulation_instance.plan_regulations == []
    plan_regulation_instance.type_of_verbal_plan_regulation = (
        type_of_verbal_plan_regulation_instance
    )
    # All eight additional information regulations are nullable
    # Käyttötarkoitus
    assert plan_regulation_instance.intended_use is None
    assert type_of_additional_information_instance.intended_use_plan_regulations == []
    plan_regulation_instance.intended_use = type_of_additional_information_instance
    # Olemassaolo
    assert plan_regulation_instance.existence is None
    assert type_of_additional_information_instance.existence_plan_regulations == []
    plan_regulation_instance.existence = type_of_additional_information_instance
    # Tyyppi (lisätiedon laji)
    assert plan_regulation_instance.regulation_type_additional_information is None
    assert type_of_additional_information_instance.type_plan_regulations == []
    plan_regulation_instance.regulation_type_additional_information = (
        type_of_additional_information_instance
    )
    # Merkittävyys
    assert plan_regulation_instance.significance is None
    assert type_of_additional_information_instance.significance_plan_regulations == []
    plan_regulation_instance.significance = type_of_additional_information_instance
    # Eri tahojen tarpeisiin varaus
    assert plan_regulation_instance.reservation is None
    assert type_of_additional_information_instance.reservation_plan_regulations == []
    plan_regulation_instance.reservation = type_of_additional_information_instance
    # Kehittäminen
    assert plan_regulation_instance.development is None
    assert type_of_additional_information_instance.development_plan_regulations == []
    plan_regulation_instance.development = type_of_additional_information_instance
    # Häiriön torjuntatarve
    assert plan_regulation_instance.disturbance_prevention is None
    assert (
        type_of_additional_information_instance.disturbance_prevention_plan_regulations
        == []
    )
    plan_regulation_instance.disturbance_prevention = (
        type_of_additional_information_instance
    )
    # Rakentamisen ohjaus
    assert plan_regulation_instance.construction_control is None
    assert (
        type_of_additional_information_instance.construction_control_plan_regulations
        == []
    )
    plan_regulation_instance.construction_control = (
        type_of_additional_information_instance
    )

    session.flush()

    assert (
        plan_regulation_instance.type_of_verbal_plan_regulation
        is type_of_verbal_plan_regulation_instance
    )
    assert type_of_verbal_plan_regulation_instance.plan_regulations == [
        plan_regulation_instance
    ]
    # Käyttötarkoitus
    assert (
        plan_regulation_instance.intended_use is type_of_additional_information_instance
    )
    assert type_of_additional_information_instance.intended_use_plan_regulations == [
        plan_regulation_instance
    ]
    # Olemassaolo
    assert plan_regulation_instance.existence is type_of_additional_information_instance
    assert type_of_additional_information_instance.existence_plan_regulations == [
        plan_regulation_instance
    ]
    # Tyyppi (lisätiedon laji)
    assert (
        plan_regulation_instance.regulation_type_additional_information
        is type_of_additional_information_instance
    )
    assert type_of_additional_information_instance.type_plan_regulations == [
        plan_regulation_instance
    ]
    # Merkittävyys
    assert (
        plan_regulation_instance.significance is type_of_additional_information_instance
    )
    assert type_of_additional_information_instance.significance_plan_regulations == [
        plan_regulation_instance
    ]
    # Eri tahojen tarpeisiin varaus
    assert (
        plan_regulation_instance.reservation is type_of_additional_information_instance
    )
    assert type_of_additional_information_instance.reservation_plan_regulations == [
        plan_regulation_instance
    ]
    # Kehittäminen
    assert (
        plan_regulation_instance.development is type_of_additional_information_instance
    )
    assert type_of_additional_information_instance.development_plan_regulations == [
        plan_regulation_instance
    ]
    # Häiriön torjuntatarve
    assert (
        plan_regulation_instance.disturbance_prevention
        is type_of_additional_information_instance
    )
    assert (
        type_of_additional_information_instance.disturbance_prevention_plan_regulations
        == [plan_regulation_instance]
    )
    # Rakentamisen ohjaus
    assert (
        plan_regulation_instance.construction_control
        is type_of_additional_information_instance
    )
    assert (
        type_of_additional_information_instance.disturbance_prevention_plan_regulations
        == [plan_regulation_instance]
    )


def test_plan_proposition(
    session: Session,
    plan_proposition_instance: models.PlanProposition,
    code_instance: codes.LifeCycleStatus,
    plan_regulation_group_instance: models.PlanRegulationGroup,
):
    # non-nullable plan proposition relations
    assert plan_proposition_instance.lifecycle_status is code_instance
    assert code_instance.plan_propositions == [plan_proposition_instance]
    assert (
        plan_proposition_instance.plan_regulation_group
        is plan_regulation_group_instance
    )
    assert plan_regulation_group_instance.plan_propositions == [
        plan_proposition_instance
    ]
    session.flush()


def test_source_data(
    session: Session,
    source_data_instance: models.SourceData,
    type_of_source_data_instance: codes.TypeOfSourceData,
):
    # nullable source data relations
    assert source_data_instance.type_of_source_data is None
    assert type_of_source_data_instance.source_data == []
    source_data_instance.type_of_source_data = type_of_source_data_instance
    session.flush()
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
    plan_regulation_instance: models.PlanRegulation,
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
    assert plan_regulation_instance.lifecycle_dates == []
    lifecycle_date_instance.plan_regulation = plan_regulation_instance
    assert lifecycle_date_instance.plan_proposition is None
    assert plan_proposition_instance.lifecycle_dates == []
    lifecycle_date_instance.plan_proposition = plan_proposition_instance
    session.flush()

    assert lifecycle_date_instance.plan is plan_instance
    assert lifecycle_date_instance.plan_regulation is plan_regulation_instance
    assert lifecycle_date_instance.plan_proposition is plan_proposition_instance
    assert lifecycle_date_instance in plan_instance.lifecycle_dates
    assert lifecycle_date_instance in plan_regulation_instance.lifecycle_dates
    assert lifecycle_date_instance in plan_proposition_instance.lifecycle_dates
