import json
from typing import Callable

import codes
import models
import pytest
from base import PROJECT_SRID
from ryhti_client.ryhti_client import RyhtiClient
from sqlalchemy.orm import Session


@pytest.fixture(scope="module")
def desired_plan_dict(
    plan_instance: models.Plan,
    land_use_area_instance: models.LandUseArea,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    general_regulation_group_instance: models.PlanRegulationGroup,
    text_plan_regulation_instance: models.PlanRegulation,
    numeric_plan_regulation_instance: models.PlanRegulation,
    verbal_plan_regulation_instance: models.PlanRegulation,
    general_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
) -> dict:
    """
    Plan dict based on https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Avoin/ryhti-plan-public-validate-api.json

    Let's 1) write explicitly the complex fields, and 2) just check that the simple fields have
    the same values as the original plan fixture in the database.
    """

    return {
        "planKey": plan_instance.id,
        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/test",
        "planType": "test",
        "administrativeAreaIdentifiers": ["test"],
        "scale": plan_instance.scale,
        "geographicalArea": {
            "srid": str(PROJECT_SRID),
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [381849.834412134019658, 6677967.973336197435856],
                            [381849.834412134019658, 6680613.389312859624624],
                            [386378.427863708813675, 6680613.389312859624624],
                            [386378.427863708813675, 6677967.973336197435856],
                            [381849.834412134019658, 6677967.973336197435856],
                        ]
                    ]
                ],
            },
        },
        # TODO: plan documents to be added.
        "periodOfValidity": None,
        "approvalDate": None,
        # TODO: dates of validity and approval to be added. These need fixtures with specific codes.
        # TODO: general regulation group to be added. This needs fixture with specific code.
        "generalRegulationGroups": [
            {
                "generalRegulationGroupKey": general_regulation_group_instance.id,
                "titleOfPlanRegulation": general_regulation_group_instance.name,
                "planRegulations": [
                    {
                        "planRegulationKey": general_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/test",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/test",
                        "value": {
                            "dataType": "LocalizedText",
                            "text": general_plan_regulation_instance.text_value,
                        },
                        "subjectIdentifiers": [
                            general_plan_regulation_instance.name[
                                "fin"
                            ]  # TODO: onko asiasana aina yksikielinen??
                        ],
                        "additionalInformations": [
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/test"
                            }
                        ],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/test",
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            general_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None
                        # TODO: dates of validity to be added. These need fixtures with specific codes.
                    },
                ],
                "planRecommendations": [],
            }
        ],
        "planDescription": plan_instance.description[
            "fin"
        ],  # TODO: should this be a single language string? why?
        "planObjects": [
            {
                "planObjectKey": land_use_area_instance.id,
                "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/test",
                "undergroundStatus": "http://uri.suomi.fi/codelist/rytj/RY_MaanalaisuudenLaji/code/test",
                "geometry": {
                    "srid": str(PROJECT_SRID),
                    "geometry": {
                        "type": "MultiPolygon",
                        "coordinates": [
                            [
                                [
                                    [381849.834412134019658, 6677967.973336197435856],
                                    [381849.834412134019658, 6680613.389312859624624],
                                    [386378.427863708813675, 6680613.389312859624624],
                                    [386378.427863708813675, 6677967.973336197435856],
                                    [381849.834412134019658, 6677967.973336197435856],
                                ]
                            ]
                        ],
                    },
                },
                "name": land_use_area_instance.name,
                "description": land_use_area_instance.description,
                "objectNumber": land_use_area_instance.ordering,
                "verticalLimit": {
                    "dataType": "decimalRange",
                    "minimumValue": land_use_area_instance.height_range.lower,
                    "maximumValue": land_use_area_instance.height_range.upper,
                    "unitOfMeasure": land_use_area_instance.height_unit,
                },
                "periodOfValidity": None
                # TODO: dates of validity to be added. These need fixtures with specific codes.
            },
        ],
        "planRegulationGroups": [
            {
                "planRegulationGroupKey": plan_regulation_group_instance.id,
                "titleOfPlanRegulation": plan_regulation_group_instance.name,
                "planRegulations": [
                    {
                        "planRegulationKey": numeric_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/test",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/test",
                        "value": {
                            "dataType": "decimal",
                            "number": numeric_plan_regulation_instance.numeric_value,
                            "unitOfMeasure": numeric_plan_regulation_instance.unit,
                        },
                        "subjectIdentifiers": [
                            numeric_plan_regulation_instance.name[
                                "fin"
                            ]  # TODO: onko asiasana aina yksikielinen??
                        ],
                        "additionalInformations": [
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/test"
                            }
                        ],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/test",
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            numeric_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None
                        # TODO: dates of validity to be added. These need fixtures with specific codes.
                    },
                    {
                        "planRegulationKey": text_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/test",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/test",
                        "value": {
                            "dataType": "LocalizedText",
                            "text": text_plan_regulation_instance.text_value,
                        },
                        "subjectIdentifiers": [
                            text_plan_regulation_instance.name[
                                "fin"
                            ]  # TODO: onko asiasana aina yksikielinen??
                        ],
                        "additionalInformations": [
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/test"
                            }
                        ],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/test",
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(text_plan_regulation_instance.ordering),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None
                        # TODO: dates of validity to be added. These need fixtures with specific codes.
                    },
                    {
                        "planRegulationKey": verbal_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/test",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/test",
                        "value": {
                            "dataType": "LocalizedText",
                            "text": verbal_plan_regulation_instance.text_value,
                        },
                        "subjectIdentifiers": [
                            verbal_plan_regulation_instance.name[
                                "fin"
                            ]  # TODO: onko asiasana aina yksikielinen??
                        ],
                        "verbalRegulations": [
                            "http://uri.suomi.fi/codelist/rytj/RY_Sanallisen_Kaavamaarayksen_Laji/code/test"
                        ],
                        "additionalInformations": [
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/test"
                            }
                        ],
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/test",
                        ],
                        # oh great, integer has to be string here for reasons unknown.
                        "regulationNumber": str(
                            verbal_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None
                        # TODO: dates of validity to be added. These need fixtures with specific codes.
                    },
                ],
                "planRecommendations": [
                    {
                        "planRecommendationKey": plan_proposition_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/test",
                        "value": plan_proposition_instance.text_value,
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/test",
                        ],
                        "recommendationNumber": plan_proposition_instance.ordering,
                        # TODO: plan recommendation documents to be added.
                        "periodOfValidity": None
                        # TODO: dates of validity to be added. These need fixtures with specific codes.
                    },
                ],
                "letterIdentifier": plan_regulation_group_instance.short_name,
                "colorNumber": "#FFFFFF",
            },
        ],
        "planRegulationGroupRelations": [
            {
                "planObjectKey": land_use_area_instance.id,
                "planRegulationGroupKey": plan_regulation_group_instance.id,
            },
        ],
    }


mock_rule = "random_rule"
mock_error_string = "There is something wrong with your plan! Good luck!"
mock_instance = "some field in your plan"


@pytest.fixture()
def mock_public_ryhti_validate(requests_mock) -> None:
    requests_mock.post(
        "http://mock.url/Plan/validate",
        text=json.dumps(
            {
                "type": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422",
                "title": "One or more validation errors occurred.",
                "status": 422,
                "detail": "Validation failed: \r\n -- Type: Geometry coordinates do not match with geometry type. Severity: Error",
                "errors": [
                    {
                        "ruleId": mock_rule,
                        "message": mock_error_string,
                        "instance": mock_instance,
                    }
                ],
                "warnings": [],
                "traceId": "00-f5288710d1eb2265175052028d4b77c4-6ed94a9caece4333-00",
            }
        ),
        status_code=422,
    )


@pytest.fixture()
def mock_xroad_ryhti_permanentidentifier(requests_mock) -> None:
    requests_mock.post(
        "http://mock2.url/r1/FI/GOV/0996189-5/Ryhti-Syke-Service/api/RegionalPlanMatter/PermanentPlanIdentifier",
        text="MK-123456",
        request_headers={"X-Road-Client": "FI/MUN/2455538-5"},
        status_code=200,
    )


@pytest.fixture(scope="module")
def client_with_plan_data(
    connection_string: str, complete_test_plan: models.Plan
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data read in.

    We have to create the plan data in the database before returning the client, because the client
    reads plans from the database when initializing. Also, let's cache plan dictionaries in the
    client like done in handler method, so all methods depending on data being serialized already
    will work as expected.
    """
    client = RyhtiClient(
        connection_string,
        public_api_url="http://mock.url",
        xroad_server_address="http://mock2.url",
        xroad_member_code="2455538-5",
    )
    client.plan_dictionaries = client.get_plan_dictionaries()
    return client


def assert_lists_equal(list1: list, list2: list):
    """
    Recursively check that lists have the same items in the same order.
    """
    assert len(list1) == len(list2)
    for item1, item2 in zip(list1, list2):
        print(f"comparing values {item1} and {item2}")
        if isinstance(item1, dict):
            assert_dicts_equal(item1, item2)
        elif isinstance(item1, list):
            assert_lists_equal(item1, item2)
        else:
            assert item1 == item2


def assert_dicts_equal(dict1: dict, dict2: dict):
    """
    Recursively check that dicts contain the same keys with same values.
    """
    for key in dict2.keys():
        assert key in dict1
    for key, value in dict1.items():
        print(f"comparing {key} {value} to {dict2[key]}")
        if isinstance(value, dict):
            assert_dicts_equal(dict2[key], value)
        elif isinstance(value, list):
            assert_lists_equal(dict2[key], value)
        else:
            assert dict2[key] == value


def test_get_plan_dictionaries(
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    desired_plan_dict: dict,
):
    """
    Check that correct JSON structure is generated
    """
    result_plan_dict = client_with_plan_data.plan_dictionaries[plan_instance.id]
    assert_dicts_equal(result_plan_dict, desired_plan_dict)


def test_validate_plans(
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_ryhti_validate: Callable,
):
    """
    Check that JSON is posted and response received
    """
    responses = client_with_plan_data.validate_plans()
    for plan_id, response in responses.items():
        assert plan_id == plan_instance.id
        assert response["errors"] == [
            {
                "ruleId": mock_rule,
                "message": mock_error_string,
                "instance": mock_instance,
            }
        ]


def test_save_responses(
    session: Session,
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_ryhti_validate: Callable,
):
    """
    Check that Ryhti response is saved to database
    """
    responses = client_with_plan_data.validate_plans()
    message = client_with_plan_data.save_responses(responses)
    session.refresh(plan_instance)
    assert plan_instance.validated_at
    assert plan_instance.validation_errors == next(iter(responses.values()))["errors"]


def test_set_permanent_plan_identifiers(
    session: Session,
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_permanentidentifier: Callable,
):
    """
    Check that Ryhti permanent plan identifier is received and saved to the database
    """
    responses = client_with_plan_data.get_permanent_plan_identifiers()
    client_with_plan_data.set_permanent_plan_identifiers(responses)
    session.refresh(plan_instance)
    received_plan_identifier = next(iter(responses.values()))
    assert plan_instance.permanent_plan_identifier
    assert plan_instance.permanent_plan_identifier == received_plan_identifier
    assert (
        client_with_plan_data.plan_dictionaries[plan_instance.id]["planKey"]
        == received_plan_identifier
    )
