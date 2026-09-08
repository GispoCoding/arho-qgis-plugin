"""Tests for the cancellation infos (kumoamistieto) in the Ryhti plan JSON.

The serializer writes the cancellation info rows of a repealing plan into
planCancellationInfos, the deserializer reads them back on import and the
copier clones them. The hand-made rows come from the plan cancellation info
fixtures in test/conftest.py; the trigger-filled rows from the repealing plan
fixtures of the same file.
"""

from __future__ import annotations

import json
import logging
from datetime import date
from typing import TYPE_CHECKING

import pytest
from geoalchemy2.shape import to_shape
from shapely.geometry import box
from sqlalchemy import select

from database import models
from ryhti_client.database_client import DatabaseClient
from ryhti_client.plan_copier import CopyPlanData
from ryhti_client.serializer import to_json_dict

if TYPE_CHECKING:
    from typing import Any

    from sqlalchemy.orm import Session

    from database import codes

RYHTI_URI = "https://uri.rakennetunymparistontietojarjestelma.fi"


@pytest.fixture
def database_client(dba_connection_string: str) -> DatabaseClient:
    return DatabaseClient(dba_connection_string)


@pytest.fixture
def repealing_plan_by_hand(
    session: Session,
    plan_instance: models.Plan,
    valid_status_instance: codes.LifeCycleStatus,
    plan_object_cancellation_info_instance: models.PlanObjectCancellationInfo,  # noqa: ARG001
    cancelled_group_relation_instance: models.CancelledGroupRelation,  # noqa: ARG001
) -> models.Plan:
    """A valid plan with one hand-made cancellation info that repeals a part of
    another plan: one land use area in part, one group relation and one general
    regulation group.
    """
    plan_instance.lifecycle_status = valid_status_instance
    session.commit()
    return plan_instance


def serialized_cancellation_infos(
    database_client: DatabaseClient, plan_id: str
) -> list[dict[str, Any]] | None:
    """The planCancellationInfos of the plan as the Ryhti JSON has them."""
    plan = database_client.get_plan(plan_id)
    return to_json_dict(database_client.serializer.serialize_plan(plan)).get(
        "planCancellationInfos"
    )


# Serializer


def test_serialize_partial_cancellation_info(
    database_client: DatabaseClient,
    repealing_plan_by_hand: models.Plan,
    another_plan_instance: models.Plan,
    plan_cancellation_info_instance: models.PlanCancellationInfo,
    plan_object_cancellation_info_instance: models.PlanObjectCancellationInfo,
    cancelled_land_use_area_instance: models.LandUseArea,
    cancelled_plan_regulation_group_instance: models.PlanRegulationGroup,
    cancelled_general_regulation_group_instance: models.PlanRegulationGroup,
) -> None:
    """The keys are the row ids and the uris are built from the ids of the
    repealed plan and its parts.
    """
    infos = serialized_cancellation_infos(database_client, repealing_plan_by_hand.id)

    assert infos == [
        {
            "planCancellationInfoKey": plan_cancellation_info_instance.id,
            "cancelledPlanUri": f"{RYHTI_URI}/plan/{another_plan_instance.id}",
            "cancelsEntirePlan": False,
            "planObjectCancellationInfos": [
                {
                    "planObjectCancellationInfoKey": (
                        plan_object_cancellation_info_instance.id
                    ),
                    "cancelledPlanObjectUri": (
                        f"{RYHTI_URI}/planobject/{cancelled_land_use_area_instance.id}"
                    ),
                    "cancelsEntirePlanObject": False,
                    "validityGeometry": {
                        "srid": "3067",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [382000.0, 6678000.0],
                                    [382000.0, 6679000.0],
                                    [383000.0, 6679000.0],
                                    [383000.0, 6678000.0],
                                    [382000.0, 6678000.0],
                                ]
                            ],
                        },
                    },
                }
            ],
            "cancelledGroupRelations": [
                {
                    "planRegulationGroupUri": (
                        f"{RYHTI_URI}/planregulationgroup/"
                        f"{cancelled_plan_regulation_group_instance.id}"
                    ),
                    "planObjectUri": (
                        f"{RYHTI_URI}/planobject/{cancelled_land_use_area_instance.id}"
                    ),
                }
            ],
            "cancelledGeneralRegulationGroupUris": [
                f"{RYHTI_URI}/generalregulationgroup/"
                f"{cancelled_general_regulation_group_instance.id}"
            ],
        }
    ]


def test_serialize_entire_plan_cancellation_info(
    session: Session,
    database_client: DatabaseClient,
    repealing_plan_by_hand: models.Plan,
    another_plan_instance: models.Plan,
    plan_cancellation_info_instance: models.PlanCancellationInfo,
) -> None:
    """Ryhti allows nothing but the flag when the whole plan is repealed."""
    plan_cancellation_info_instance.cancels_entire_plan = True
    session.commit()

    infos = serialized_cancellation_infos(database_client, repealing_plan_by_hand.id)

    assert infos == [
        {
            "planCancellationInfoKey": plan_cancellation_info_instance.id,
            "cancelledPlanUri": f"{RYHTI_URI}/plan/{another_plan_instance.id}",
            "cancelsEntirePlan": True,
        }
    ]


def test_serialize_entirely_repealed_plan_object_has_no_geometry(
    session: Session,
    database_client: DatabaseClient,
    repealing_plan_by_hand: models.Plan,
    plan_object_cancellation_info_instance: models.PlanObjectCancellationInfo,
) -> None:
    plan_object_cancellation_info_instance.cancels_entire_plan_object = True
    plan_object_cancellation_info_instance.remaining_valid_geom_polygon = None
    session.commit()

    infos = serialized_cancellation_infos(database_client, repealing_plan_by_hand.id)

    assert infos is not None
    assert infos[0]["planObjectCancellationInfos"] == [
        {
            "planObjectCancellationInfoKey": plan_object_cancellation_info_instance.id,
            "cancelledPlanObjectUri": (
                f"{RYHTI_URI}/planobject/"
                f"{plan_object_cancellation_info_instance.land_use_area_id}"
            ),
            "cancelsEntirePlanObject": True,
        }
    ]


def test_serialize_cancellation_infos_in_repealed_status(
    session: Session,
    database_client: DatabaseClient,
    repealing_plan_by_hand: models.Plan,
    repealed_status_instance: codes.LifeCycleStatus,
) -> None:
    """Rule 218 allows the infos in the valid and the repealed status."""
    repealing_plan_by_hand.lifecycle_status = repealed_status_instance
    session.commit()

    infos = serialized_cancellation_infos(database_client, repealing_plan_by_hand.id)

    assert infos is not None
    assert len(infos) == 1


def test_no_cancellation_infos_before_the_plan_is_valid(
    session: Session,
    database_client: DatabaseClient,
    repealing_plan_by_hand: models.Plan,
    plan_proposal_status_instance: codes.LifeCycleStatus,
) -> None:
    """A proposal is sent without the infos, so that it passes rule 218."""
    repealing_plan_by_hand.lifecycle_status = plan_proposal_status_instance
    session.commit()

    assert (
        serialized_cancellation_infos(database_client, repealing_plan_by_hand.id)
        is None
    )


def test_no_cancellation_infos_without_rows(
    session: Session,
    database_client: DatabaseClient,
    plan_instance: models.Plan,
    valid_status_instance: codes.LifeCycleStatus,
) -> None:
    """The field is left out, not sent as an empty list."""
    plan_instance.lifecycle_status = valid_status_instance
    session.commit()

    assert serialized_cancellation_infos(database_client, plan_instance.id) is None


# Import


@pytest.fixture
def extra_data(plan_matter_instance: models.PlanMatter) -> dict[str, Any]:
    return {"name": "imported_plan", "plan_matter_id": plan_matter_instance.id}


def plan_json_with_cancellation_infos(
    plan_json: str, infos: list[dict[str, Any]]
) -> str:
    """The plan JSON with the given planCancellationInfos."""
    plan_dict = json.loads(plan_json)
    plan_dict["planCancellationInfos"] = infos
    return json.dumps(plan_dict)


@pytest.fixture
def valid_plan_json(
    session: Session,
    database_client: DatabaseClient,
    plan_instance: models.Plan,
    valid_status_instance: codes.LifeCycleStatus,
) -> str:
    """The JSON of the valid test plan, without cancellation infos."""
    plan_instance.lifecycle_status = valid_status_instance
    session.commit()
    plan = database_client.get_plan(plan_instance.id)
    return database_client.serializer.serialize_plan(plan).model_dump_json(
        by_alias=True, exclude_none=True
    )


@pytest.fixture
def cancellation_info_json(
    another_plan_instance: models.Plan,
    cancelled_land_use_area_instance: models.LandUseArea,
    cancelled_plan_regulation_group_instance: models.PlanRegulationGroup,
    cancelled_general_regulation_group_instance: models.PlanRegulationGroup,
) -> dict[str, Any]:
    """One cancellation info that repeals a part of another plan."""
    return {
        "planCancellationInfoKey": "4b6d3cc6-5b0e-4a2f-9a6d-4a5b7c8d9e01",
        "cancelledPlanUri": f"{RYHTI_URI}/plan/{another_plan_instance.id}",
        "cancelsEntirePlan": False,
        "planObjectCancellationInfos": [
            {
                "planObjectCancellationInfoKey": (
                    "9d1f2a3b-4c5d-4e6f-8a7b-9c0d1e2f3a02"
                ),
                "cancelledPlanObjectUri": (
                    f"{RYHTI_URI}/planobject/{cancelled_land_use_area_instance.id}"
                ),
                "cancelsEntirePlanObject": False,
                "validityGeometry": {
                    "srid": "3067",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [382000.0, 6678000.0],
                                [382000.0, 6679000.0],
                                [383000.0, 6679000.0],
                                [383000.0, 6678000.0],
                                [382000.0, 6678000.0],
                            ]
                        ],
                    },
                },
            }
        ],
        "cancelledGroupRelations": [
            {
                "planRegulationGroupUri": (
                    f"{RYHTI_URI}/planregulationgroup/"
                    f"{cancelled_plan_regulation_group_instance.id}"
                ),
                "planObjectUri": (
                    f"{RYHTI_URI}/planobject/{cancelled_land_use_area_instance.id}"
                ),
            }
        ],
        "cancelledGeneralRegulationGroupUris": [
            f"{RYHTI_URI}/generalregulationgroup/"
            f"{cancelled_general_regulation_group_instance.id}"
        ],
    }


def cancellation_infos_of(
    session: Session, plan_id: str
) -> list[models.PlanCancellationInfo]:
    """The cancellation infos of the plan, read back from the database."""
    session.expire_all()
    return list(
        session.scalars(
            select(models.PlanCancellationInfo).where(
                models.PlanCancellationInfo.plan_id == plan_id
            )
        )
    )


def test_import_plan_with_cancellation_infos(
    session: Session,
    database_client: DatabaseClient,
    plan_instance: models.Plan,
    plan_matter_instance: models.PlanMatter,
    another_plan_instance: models.Plan,
    cancelled_land_use_area_instance: models.LandUseArea,
    cancelled_plan_regulation_group_instance: models.PlanRegulationGroup,
    cancelled_general_regulation_group_instance: models.PlanRegulationGroup,
    valid_plan_json: str,
    cancellation_info_json: dict[str, Any],
    extra_data: dict[str, Any],
) -> None:
    """The keys and uris of the JSON become the row ids and foreign keys."""
    plan_json = plan_json_with_cancellation_infos(
        valid_plan_json, [cancellation_info_json]
    )

    database_client.import_plan(plan_json, extra_data, overwrite=True)

    infos = cancellation_infos_of(session, plan_instance.id)
    assert len(infos) == 1
    info = infos[0]
    assert info.id == cancellation_info_json["planCancellationInfoKey"]
    assert info.cancelled_plan_id == another_plan_instance.id
    assert info.cancels_entire_plan is False

    assert len(info.plan_object_cancellation_infos) == 1
    row = info.plan_object_cancellation_infos[0]
    assert (
        row.id
        == (
            cancellation_info_json["planObjectCancellationInfos"][0][
                "planObjectCancellationInfoKey"
            ]
        )
    )
    assert row.land_use_area_id == cancelled_land_use_area_instance.id
    assert row.cancels_entire_plan_object is False
    assert row.remaining_valid_geom_polygon is not None
    assert to_shape(row.remaining_valid_geom_polygon).equals(
        box(382000.0, 6678000.0, 383000.0, 6679000.0)
    )

    assert len(info.cancelled_group_relations) == 1
    relation = info.cancelled_group_relations[0]
    assert relation.plan_regulation_group_id == (
        cancelled_plan_regulation_group_instance.id
    )
    assert relation.land_use_area_id == cancelled_land_use_area_instance.id

    assert info.cancelled_general_regulation_groups == [
        cancelled_general_regulation_group_instance
    ]

    session.refresh(plan_matter_instance)
    assert plan_matter_instance.repealing is True


def test_import_plan_without_cancellation_infos_leaves_the_plan_matter_alone(
    session: Session,
    database_client: DatabaseClient,
    plan_matter_instance: models.PlanMatter,
    valid_plan_json: str,
    extra_data: dict[str, Any],
) -> None:
    database_client.import_plan(valid_plan_json, extra_data, overwrite=True)

    session.refresh(plan_matter_instance)
    assert plan_matter_instance.repealing is False


def test_import_skips_a_cancellation_info_of_an_unknown_plan(
    session: Session,
    database_client: DatabaseClient,
    plan_instance: models.Plan,
    valid_plan_json: str,
    cancellation_info_json: dict[str, Any],
    extra_data: dict[str, Any],
    caplog: pytest.LogCaptureFixture,
) -> None:
    unknown_plan_id = "0f0f0f0f-0000-4000-8000-000000000000"
    cancellation_info_json["cancelledPlanUri"] = f"{RYHTI_URI}/plan/{unknown_plan_id}"
    plan_json = plan_json_with_cancellation_infos(
        valid_plan_json, [cancellation_info_json]
    )

    with caplog.at_level(logging.WARNING):
        database_client.import_plan(plan_json, extra_data, overwrite=True)

    assert cancellation_infos_of(session, plan_instance.id) == []
    assert unknown_plan_id in caplog.text
    # The rest of the plan is imported.
    assert session.get(models.Plan, plan_instance.id) is not None


def test_import_skips_a_plan_object_cancellation_info_of_an_unknown_plan_object(
    session: Session,
    database_client: DatabaseClient,
    plan_instance: models.Plan,
    valid_plan_json: str,
    cancellation_info_json: dict[str, Any],
    extra_data: dict[str, Any],
    caplog: pytest.LogCaptureFixture,
) -> None:
    unknown_object_id = "0f0f0f0f-0000-4000-8000-000000000001"
    cancellation_info_json["planObjectCancellationInfos"][0][
        "cancelledPlanObjectUri"
    ] = f"{RYHTI_URI}/planobject/{unknown_object_id}"
    plan_json = plan_json_with_cancellation_infos(
        valid_plan_json, [cancellation_info_json]
    )

    with caplog.at_level(logging.WARNING):
        database_client.import_plan(plan_json, extra_data, overwrite=True)

    infos = cancellation_infos_of(session, plan_instance.id)
    assert len(infos) == 1
    assert infos[0].plan_object_cancellation_infos == []
    assert len(infos[0].cancelled_group_relations) == 1
    assert unknown_object_id in caplog.text


def test_import_skips_a_group_relation_of_an_unknown_group(
    session: Session,
    database_client: DatabaseClient,
    plan_instance: models.Plan,
    valid_plan_json: str,
    cancellation_info_json: dict[str, Any],
    extra_data: dict[str, Any],
    caplog: pytest.LogCaptureFixture,
) -> None:
    unknown_group_id = "0f0f0f0f-0000-4000-8000-000000000002"
    cancellation_info_json["cancelledGroupRelations"][0]["planRegulationGroupUri"] = (
        f"{RYHTI_URI}/planregulationgroup/{unknown_group_id}"
    )
    cancellation_info_json["cancelledGeneralRegulationGroupUris"] = [
        f"{RYHTI_URI}/generalregulationgroup/{unknown_group_id}"
    ]
    plan_json = plan_json_with_cancellation_infos(
        valid_plan_json, [cancellation_info_json]
    )

    with caplog.at_level(logging.WARNING):
        database_client.import_plan(plan_json, extra_data, overwrite=True)

    infos = cancellation_infos_of(session, plan_instance.id)
    assert len(infos) == 1
    assert infos[0].cancelled_group_relations == []
    assert infos[0].cancelled_general_regulation_groups == []
    assert len(infos[0].plan_object_cancellation_infos) == 1
    assert unknown_group_id in caplog.text


def test_import_writes_the_cancellation_infos_of_the_file_over_the_trigger(
    session: Session,
    database_client: DatabaseClient,
    repealing_plan: models.Plan,
    repealing_plan_matter: models.PlanMatter,
    cancelled_plan: models.Plan,
    valid_status_instance: codes.LifeCycleStatus,
) -> None:
    """The JSON is the truth: the geometry-driven trigger does not rewrite the
    imported rows, even when the plan overlaps a valid plan.
    """
    repealing_plan.lifecycle_status = valid_status_instance
    session.commit()
    plan = database_client.get_plan(repealing_plan.id)
    plan_dict = to_json_dict(database_client.serializer.serialize_plan(plan))
    # The trigger says the plan is repealed in part; the file says entirely.
    assert plan_dict["planCancellationInfos"][0]["cancelsEntirePlan"] is False
    plan_dict["planCancellationInfos"][0] = {
        "planCancellationInfoKey": plan_dict["planCancellationInfos"][0][
            "planCancellationInfoKey"
        ],
        "cancelledPlanUri": f"{RYHTI_URI}/plan/{cancelled_plan.id}",
        "cancelsEntirePlan": True,
    }
    extra_data = {"name": "imported_plan", "plan_matter_id": repealing_plan_matter.id}

    database_client.import_plan(json.dumps(plan_dict), extra_data, overwrite=True)

    infos = cancellation_infos_of(session, repealing_plan.id)
    assert len(infos) == 1
    assert infos[0].cancels_entire_plan is True
    assert infos[0].plan_object_cancellation_infos == []


def test_cancellation_infos_survive_an_export_and_import_round_trip(
    database_client: DatabaseClient,
    repealing_plan_by_hand: models.Plan,
    extra_data: dict[str, Any],
) -> None:
    plan = database_client.get_plan(repealing_plan_by_hand.id)
    exported = database_client.serializer.serialize_plan(plan)
    exported_json = exported.model_dump_json(by_alias=True, exclude_none=True)

    database_client.import_plan(exported_json, extra_data, overwrite=True)

    imported = serialized_cancellation_infos(database_client, repealing_plan_by_hand.id)
    assert imported == to_json_dict(exported)["planCancellationInfos"]


# Copy


def copied_cancellation_infos(
    session: Session, copied_plan_id: str
) -> list[models.PlanCancellationInfo]:
    infos = cancellation_infos_of(session, copied_plan_id)
    assert infos, "The copy has no cancellation infos."
    return infos


@pytest.mark.parametrize("deep_copy", [True, False])
def test_copy_plan_copies_the_cancellation_infos(
    session: Session,
    database_client: DatabaseClient,
    repealing_plan_by_hand: models.Plan,
    plan_cancellation_info_instance: models.PlanCancellationInfo,
    plan_object_cancellation_info_instance: models.PlanObjectCancellationInfo,
    cancelled_group_relation_instance: models.CancelledGroupRelation,
    cancelled_general_regulation_group_instance: models.PlanRegulationGroup,
    valid_status_instance: codes.LifeCycleStatus,
    deep_copy: bool,
) -> None:
    """The copy repeals the same plan, plan objects and groups as the source,
    in rows of its own.
    """
    copy_data = CopyPlanData(
        plan_name={"fin": "Copied plan"},
        deep_copy=deep_copy,
        lifecycle_status_id=valid_status_instance.id,
        approval_date=date(2026, 1, 1),
        period_of_validity_start=date(2026, 2, 1),
    )

    copied_plan_id = database_client.copy_plan(repealing_plan_by_hand.id, copy_data)

    assert copied_plan_id is not None
    infos = copied_cancellation_infos(session, copied_plan_id)
    assert len(infos) == 1
    info = infos[0]
    assert info.id != plan_cancellation_info_instance.id
    assert info.cancelled_plan_id == plan_cancellation_info_instance.cancelled_plan_id
    assert info.cancels_entire_plan is False

    assert len(info.plan_object_cancellation_infos) == 1
    row = info.plan_object_cancellation_infos[0]
    assert row.id != plan_object_cancellation_info_instance.id
    assert row.land_use_area_id == (
        plan_object_cancellation_info_instance.land_use_area_id
    )
    assert row.cancels_entire_plan_object is False
    source_geom = plan_object_cancellation_info_instance.remaining_valid_geom_polygon
    assert row.remaining_valid_geom_polygon is not None
    assert source_geom is not None
    assert to_shape(row.remaining_valid_geom_polygon).equals(to_shape(source_geom))

    assert len(info.cancelled_group_relations) == 1
    relation = info.cancelled_group_relations[0]
    assert relation.id != cancelled_group_relation_instance.id
    assert relation.plan_regulation_group_id == (
        cancelled_group_relation_instance.plan_regulation_group_id
    )
    assert (
        relation.land_use_area_id == cancelled_group_relation_instance.land_use_area_id
    )

    assert info.cancelled_general_regulation_groups == [
        cancelled_general_regulation_group_instance
    ]
    # The source keeps its own rows.
    assert len(cancellation_infos_of(session, repealing_plan_by_hand.id)) == 1


def test_copy_plan_copies_the_trigger_filled_cancellation_infos(
    session: Session,
    database_client: DatabaseClient,
    repealing_plan: models.Plan,
    cancelled_plan: models.Plan,
) -> None:
    """A copy of a plan whose rows the trigger filled gets the same rows, even
    though the trigger would fill them again for the copy.
    """
    copy_data = CopyPlanData(plan_name={"fin": "Copied plan"}, deep_copy=True)

    copied_plan_id = database_client.copy_plan(repealing_plan.id, copy_data)

    assert copied_plan_id is not None
    infos = copied_cancellation_infos(session, copied_plan_id)
    assert len(infos) == 1
    assert infos[0].cancelled_plan_id == cancelled_plan.id
    assert len(infos[0].plan_object_cancellation_infos) == 4


# Refresh


def test_refresh_plan_cancellation_info_writes_the_rows_again(
    session: Session,
    database_client: DatabaseClient,
    repealing_plan: models.Plan,
    cancelled_plan: models.Plan,
    valid_status_instance: codes.LifeCycleStatus,
) -> None:
    """The rows of a plan may be older than the plans they name. The refresh
    brings them in step with the plans that are valid now, so the JSON of the
    validate and finalize actions matches.
    """
    repealing_plan.lifecycle_status = valid_status_instance
    session.commit()
    # A plan that is no longer final leaves hame.plan_valid, but the rows of
    # the repealing plan stay as they were, because its geometry did not change.
    cancelled_plan.final = False
    session.commit()
    assert serialized_cancellation_infos(database_client, repealing_plan.id)

    database_client.refresh_plan_cancellation_info(repealing_plan.id)

    assert serialized_cancellation_infos(database_client, repealing_plan.id) is None

    cancelled_plan.final = True
    session.commit()
    database_client.refresh_plan_cancellation_info(repealing_plan.id)

    infos = serialized_cancellation_infos(database_client, repealing_plan.id)
    assert infos is not None
    assert infos[0]["cancelledPlanUri"] == f"{RYHTI_URI}/plan/{cancelled_plan.id}"
    assert len(infos[0]["planObjectCancellationInfos"]) == 4
