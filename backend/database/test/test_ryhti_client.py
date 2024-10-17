import json
from copy import deepcopy
from typing import Callable, Iterable, List, Optional

import codes
import models
import pytest
from base import PROJECT_SRID
from requests_mock.request import _RequestObjectProxy
from ryhti_client.ryhti_client import RyhtiClient
from sqlalchemy.orm import Session


@pytest.fixture(scope="function")
def desired_plan_dict(
    plan_instance: models.Plan,
    land_use_area_instance: models.LandUseArea,
    land_use_point_instance: models.LandUsePoint,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    point_plan_regulation_group_instance: models.PlanRegulationGroup,
    general_regulation_group_instance: models.PlanRegulationGroup,
    empty_value_plan_regulation_instance: models.PlanRegulation,
    text_plan_regulation_instance: models.PlanRegulation,
    point_text_plan_regulation_instance: models.PlanRegulation,
    numeric_plan_regulation_instance: models.PlanRegulation,
    verbal_plan_regulation_instance: models.PlanRegulation,
    general_plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    pending_date_instance: models.LifeCycleDate,
) -> dict:
    """
    Plan dict based on https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Avoin/ryhti-plan-public-validate-api.json

    Let's 1) write explicitly the complex fields, and 2) just check that the simple fields have
    the same values as the original plan fixture in the database.
    """

    return {
        "planKey": plan_instance.id,
        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
        "scale": plan_instance.scale,
        "geographicalArea": {
            "srid": str(PROJECT_SRID),
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [381849.834412134019658, 6677967.973336197435856],
                        [381849.834412134019658, 6680613.389312859624624],
                        [386378.427863708813675, 6680613.389312859624624],
                        [386378.427863708813675, 6677967.973336197435856],
                        [381849.834412134019658, 6677967.973336197435856],
                    ]
                ],
            },
        },
        # TODO: plan documents to be added.
        "periodOfValidity": None,
        "approvalDate": None,
        "generalRegulationGroups": [
            {
                "generalRegulationGroupKey": general_regulation_group_instance.id,
                "titleOfPlanRegulation": general_regulation_group_instance.name,
                "planRegulations": [
                    {
                        "planRegulationKey": general_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
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
                        "periodOfValidity": None,
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
                "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                "undergroundStatus": "http://uri.suomi.fi/codelist/rytj/RY_MaanalaisuudenLaji/code/test",
                "geometry": {
                    "srid": str(PROJECT_SRID),
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [381849.834412134019658, 6677967.973336197435856],
                                [381849.834412134019658, 6680613.389312859624624],
                                [386378.427863708813675, 6680613.389312859624624],
                                [386378.427863708813675, 6677967.973336197435856],
                                [381849.834412134019658, 6677967.973336197435856],
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
                "periodOfValidity": None,
            },
            {
                "planObjectKey": land_use_point_instance.id,
                "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                "undergroundStatus": "http://uri.suomi.fi/codelist/rytj/RY_MaanalaisuudenLaji/code/test",
                "geometry": {
                    "srid": str(PROJECT_SRID),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [382000, 6678000],
                    },
                },
                "name": land_use_point_instance.name,
                "description": land_use_point_instance.description,
                "objectNumber": land_use_point_instance.ordering,
                "periodOfValidity": None,
            },
        ],
        "planRegulationGroups": [
            {
                "planRegulationGroupKey": point_plan_regulation_group_instance.id,
                "titleOfPlanRegulation": point_plan_regulation_group_instance.name,
                "planRegulations": [
                    {
                        "planRegulationKey": point_text_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/test",
                        "value": {
                            "dataType": "LocalizedText",
                            "text": point_text_plan_regulation_instance.text_value,
                        },
                        "subjectIdentifiers": [
                            point_text_plan_regulation_instance.name[
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
                            point_text_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    }
                ],
                "planRecommendations": [],
                "letterIdentifier": point_plan_regulation_group_instance.short_name,
                "colorNumber": "#FFFFFF",
            },
            {
                "planRegulationGroupKey": plan_regulation_group_instance.id,
                "titleOfPlanRegulation": plan_regulation_group_instance.name,
                "planRegulations": [
                    {
                        "planRegulationKey": empty_value_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/test",
                        "subjectIdentifiers": [
                            empty_value_plan_regulation_instance.name[
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
                            empty_value_plan_regulation_instance.ordering
                        ),
                        # TODO: plan regulation documents to be added.
                        "periodOfValidity": None,
                    },
                    {
                        "planRegulationKey": numeric_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
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
                        "periodOfValidity": None,
                    },
                    {
                        "planRegulationKey": text_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
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
                        "periodOfValidity": None,
                    },
                    {
                        "planRegulationKey": verbal_plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
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
                        "periodOfValidity": None,
                    },
                ],
                "planRecommendations": [
                    {
                        "planRecommendationKey": plan_proposition_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                        "value": plan_proposition_instance.text_value,
                        "planThemes": [
                            "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/test",
                        ],
                        "recommendationNumber": plan_proposition_instance.ordering,
                        # TODO: plan recommendation documents to be added.
                        "periodOfValidity": None,
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
            {
                "planObjectKey": land_use_point_instance.id,
                "planRegulationGroupKey": point_plan_regulation_group_instance.id,
            },
        ],
    }


@pytest.fixture(scope="function")
def desired_plan_matter_dict(
    session: Session,
    desired_plan_dict: dict,
    plan_instance: models.Plan,
    participation_plan_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
    plan_material_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
    draft_plan_presenting_for_public_decision: codes.NameOfPlanCaseDecision,
    participation_plan_presenting_for_public_event: codes.TypeOfProcessingEvent,
    plan_material_presenting_for_public_event: codes.TypeOfProcessingEvent,
    presentation_to_the_public_interaction: codes.TypeOfInteractionEvent,
    decisionmaker_type: codes.TypeOfDecisionMaker,
) -> dict:
    """
    Plan matter dict based on https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Palveluväylä/Kaavoitus%20OpenApi.json

    Constructing the plan matter requires certain additional codes to be present in the database and set in the plan instance.

    Let's 1) write explicitly the complex fields, and 2) just check that the simple fields have
    the same values as the original plan fixture in the database.
    """

    return {
        "permanentPlanIdentifier": "MK-123456",
        "planType": "http://uri.suomi.fi/codelist/rytj/RY_Kaavalaji/code/test",
        "name": plan_instance.name,
        "timeOfInitiation": "2024-01-01",
        "description": plan_instance.description,
        "producerPlanIdentifier": plan_instance.producers_plan_identifier,
        "caseIdentifiers": [plan_instance.matter_management_identifier],
        "recordNumbers": [plan_instance.record_number],
        "administrativeAreaIdentifiers": ["test"],
        "digitalOrigin": "http://uri.suomi.fi/codelist/rytj/RY_DigitaalinenAlkupera/code/01",
        "planMatterPhases": [
            {
                "planMatterPhaseKey": "whatever",
                "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/03",
                "geographicalArea": desired_plan_dict["geographicalArea"],
                "handlingEvent": {
                    "handlingEventKey": "whatever",
                    "handlingEventType": "http://uri.suomi.fi/codelist/rytj/kaavakastap/code/05",
                    "eventTime": "2024-02-01",
                },
                "interactionEvents": [
                    {
                        "interactionEventKey": "whatever",
                        "interactionEventType": "http://uri.suomi.fi/codelist/rytj/RY_KaavanVuorovaikutustapahtumanLaji/code/01",
                        "eventTime": {"begin": "2024-02-01", "end": None},
                    },
                ],
                "planDecision": {
                    "planDecisionKey": "whatever",
                    "name": "http://uri.suomi.fi/codelist/rytj/kaavpaatnimi/code/04",
                    "decisionDate": "2024-02-01",
                    "dateOfDecision": "2024-02-01",
                    "typeOfDecisionMaker": "http://uri.suomi.fi/codelist/rytj/PaatoksenTekija/code/01",
                    "plans": [desired_plan_dict],
                },
            },
        ],
        # TODO: plan documents, source data etc. non-mandatory fields to be added
    }


mock_rule = "random_rule"
mock_matter_rule = "another_random_rule"
mock_error_string = "There is something wrong with your plan! Good luck!"
mock_matter_error_string = (
    "There is something wrong with your plan matter as well! Have fun!"
)
mock_instance = "some field in your plan"
mock_matter_instance = "some field in your plan matter"


@pytest.fixture()
def mock_public_ryhti_validate_invalid(requests_mock) -> None:
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
def mock_public_ryhti_validate_valid(requests_mock) -> None:
    requests_mock.post(
        "http://mock.url/Plan/validate",
        status_code=200,
    )


@pytest.fixture()
def mock_xroad_ryhti_authenticate(requests_mock) -> None:
    def match_request_body(request: _RequestObjectProxy):
        # Oh great, looks like requests json method will not parse minimal json consisting of just string.
        # Instead, we'll have to match the request text.
        return request.text == '"test-secret"'

    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-Service/planService/api/Authenticate?clientId=test-id",
        json="test-token",
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        additional_matcher=match_request_body,
        status_code=200,
    )


@pytest.fixture()
def mock_xroad_ryhti_permanentidentifier(requests_mock) -> None:
    def match_request_body_with_correct_region(request: _RequestObjectProxy):
        return request.json()["administrativeAreaIdentifier"] == "test"

    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-Service/planService/api/RegionalPlanMatter/PermanentPlanIdentifier",
        json="MK-123456",
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        additional_matcher=match_request_body_with_correct_region,
        status_code=200,
    )

    def match_request_body_with_wrong_region(request: _RequestObjectProxy):
        return request.json()["administrativeAreaIdentifier"] == "other-test"

    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-Service/planService/api/RegionalPlanMatter/PermanentPlanIdentifier",
        json={
            "type": "https://httpstatuses.io/401",
            "title": "Unauthorized",
            "status": 401,
            "traceId": "00-82a0a8d02f7824c2dcda16e481f4d2e8-3797b905d05ed6c3-00",
        },
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        additional_matcher=match_request_body_with_wrong_region,
        status_code=401,
    )


@pytest.fixture()
def mock_xroad_ryhti_validate_invalid(requests_mock) -> None:
    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-Service/planService/api/RegionalPlanMatter/MK-123456/validate",
        json={
            "type": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422",
            "title": "One or more validation errors occurred.",
            "status": 422,
            "detail": "Validation failed: \r\n -- Type: Geometry coordinates do not match with geometry type. Severity: Error",
            "errors": [
                {
                    "ruleId": mock_matter_rule,
                    "message": mock_matter_error_string,
                    "instance": mock_matter_instance,
                }
            ],
            "warnings": [],
            "traceId": "00-f5288710d1eb2265175052028d4b77c4-6ed94a9caece4333-00",
        },
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        status_code=422,
    )


@pytest.fixture()
def mock_xroad_ryhti_validate_valid(requests_mock) -> None:
    requests_mock.post(
        "http://mock2.url:8080/r1/FI/GOV/0996189-5/Ryhti-Syke-Service/planService/api/RegionalPlanMatter/MK-123456/validate",
        request_headers={
            "X-Road-Client": "FI/COM/2455538-5/ryhti-gispo-client",
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
            "Content-type": "application/json",
        },
        status_code=200,
    )


@pytest.fixture(scope="function")
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
    # Let's mock production x-road with gispo organization client here.
    client = RyhtiClient(
        connection_string,
        public_api_url="http://mock.url",
        xroad_server_address="http://mock2.url",
        xroad_instance="FI",
        xroad_member_class="COM",
        xroad_member_code="2455538-5",
        xroad_member_client_name="ryhti-gispo-client",
        xroad_syke_client_id="test-id",
        xroad_syke_client_secret="test-secret",
    )
    client.plan_dictionaries = client.get_plan_dictionaries()
    return client


def assert_lists_equal(list1: list, list2: list, ignore_keys: Optional[List] = []):
    """
    Recursively check that lists have the same items in the same order.

    Optionally, certain keys (e.g. random UUIDs set by the database, our script or
    the remote Ryhti API) can be ignored when comparing dicts in the lists, because
    they are not provided in the incoming data.
    """
    assert len(list1) == len(list2)
    for item1, item2 in zip(list1, list2):
        print(f"comparing values {item1} and {item2}")
        if isinstance(item1, dict):
            assert_dicts_equal(item1, item2, ignore_keys=ignore_keys)
        elif isinstance(item1, list):
            assert_lists_equal(item1, item2, ignore_keys=ignore_keys)
        else:
            assert item1 == item2


def assert_dicts_equal(dict1: dict, dict2: dict, ignore_keys: Optional[List] = []):
    """
    Recursively check that dicts contain the same keys with same values.

    Optionally, certain keys (e.g. random UUIDs set by the database, our script or
    the remote Ryhti API) can be ignored when comparing, because they are not
    provided in the incoming data.
    """
    for key in dict2.keys():
        if not ignore_keys or not key in ignore_keys:
            assert key in dict1
    for key, value in dict1.items():
        if not ignore_keys or not key in ignore_keys:
            print(f"comparing {key} {value} to {dict2[key]}")
            if isinstance(value, dict):
                assert_dicts_equal(dict2[key], value, ignore_keys=ignore_keys)
            elif isinstance(value, list):
                assert_lists_equal(dict2[key], value, ignore_keys=ignore_keys)
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
    mock_public_ryhti_validate_invalid: Callable,
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


def test_save_plan_validation_responses(
    session: Session,
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_ryhti_validate_invalid: Callable,
):
    """
    Check that Ryhti validation error is saved to database.
    """
    responses = client_with_plan_data.validate_plans()
    message = client_with_plan_data.save_plan_validation_responses(responses)
    session.refresh(plan_instance)
    assert plan_instance.validated_at
    assert plan_instance.validation_errors == next(iter(responses.values()))["errors"]


def test_authenticate_to_xroad_ryhti_api(
    session: Session,
    client_with_plan_data: RyhtiClient,
    mock_xroad_ryhti_authenticate: Callable,
):
    """
    Test authenticating to mock X-Road Ryhti API.
    """
    client_with_plan_data.xroad_ryhti_authenticate()
    assert client_with_plan_data.xroad_headers["Authorization"] == "Bearer test-token"


@pytest.fixture()
def authenticated_client_with_valid_plan(
    session: Session,
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    mock_public_ryhti_validate_valid: Callable,
    mock_xroad_ryhti_authenticate: Callable,
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data read in and validated without errors, and
    that is authenticated to our mock X-Road API.
    """
    responses = client_with_plan_data.validate_plans()
    client_with_plan_data.save_plan_validation_responses(responses)
    session.refresh(plan_instance)
    assert plan_instance.validated_at
    assert (
        plan_instance.validation_errors
        == "Kaava on validi. Kaava-asiaa ei ole vielä validoitu."
    )
    client_with_plan_data.xroad_ryhti_authenticate()
    assert client_with_plan_data.xroad_headers["Authorization"] == "Bearer test-token"
    return client_with_plan_data


@pytest.fixture()
def authenticated_client_with_valid_plan_in_wrong_region(
    session: Session,
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    another_organisation_instance: models.Organisation,
    mock_public_ryhti_validate_valid: Callable,
    mock_xroad_ryhti_authenticate: Callable,
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data in the wrong region read in and validated
    without errors, and that is authenticated to our mock X-Road API.
    """
    plan_instance.organisation = another_organisation_instance
    session.commit()

    responses = client_with_plan_data.validate_plans()
    client_with_plan_data.save_plan_validation_responses(responses)
    session.refresh(plan_instance)
    assert plan_instance.validated_at
    assert (
        plan_instance.validation_errors
        == "Kaava on validi. Kaava-asiaa ei ole vielä validoitu."
    )
    client_with_plan_data.xroad_ryhti_authenticate()
    assert client_with_plan_data.xroad_headers["Authorization"] == "Bearer test-token"
    return client_with_plan_data


def test_set_permanent_plan_identifiers_in_wrong_region(
    session: Session,
    authenticated_client_with_valid_plan_in_wrong_region: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_permanentidentifier: Callable,
):
    """
    Check that Ryhti permanent plan identifier is left empty, if Ryhti API reports that
    the organization has no permission to create plans in the region. This requires
    that the client has already marked the plan as valid.
    """
    id_responses = (
        authenticated_client_with_valid_plan_in_wrong_region.get_permanent_plan_identifiers()
    )
    authenticated_client_with_valid_plan_in_wrong_region.set_permanent_plan_identifiers(
        id_responses
    )
    session.refresh(plan_instance)
    assert not plan_instance.permanent_plan_identifier
    assert (
        plan_instance.validation_errors
        == "Kaava on validi, mutta sinulla ei ole oikeuksia luoda kaavaa tälle alueelle."
    )


def test_set_permanent_plan_identifiers(
    session: Session,
    authenticated_client_with_valid_plan: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_permanentidentifier: Callable,
):
    """
    Check that Ryhti permanent plan identifier is received and saved to the database, if
    Ryhti API returns a permanent plan identifier. This requires that the client has already
    marked the plan as valid.
    """

    id_responses = authenticated_client_with_valid_plan.get_permanent_plan_identifiers()
    authenticated_client_with_valid_plan.set_permanent_plan_identifiers(id_responses)
    session.refresh(plan_instance)
    received_plan_identifier = next(iter(id_responses.values()))["detail"]
    assert plan_instance.permanent_plan_identifier
    assert plan_instance.permanent_plan_identifier == received_plan_identifier
    assert (
        plan_instance.validation_errors
        == "Kaava on validi. Pysyvä kaavatunnus tallennettu. Kaava-asiaa ei ole vielä validoitu."
    )


@pytest.fixture()
def client_with_plan_with_permanent_identifier(
    session: Session,
    authenticated_client_with_valid_plan: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_permanentidentifier: Callable,
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data read in, validated and its permanent
    identifier set.
    """
    id_responses = authenticated_client_with_valid_plan.get_permanent_plan_identifiers()
    authenticated_client_with_valid_plan.set_permanent_plan_identifiers(id_responses)
    session.refresh(plan_instance)
    print(id_responses)
    received_plan_identifier = next(iter(id_responses.values()))["detail"]
    assert plan_instance.permanent_plan_identifier
    assert plan_instance.permanent_plan_identifier == received_plan_identifier
    authenticated_client_with_valid_plan.plan_matter_dictionaries = (
        authenticated_client_with_valid_plan.get_plan_matters()
    )
    assert (
        authenticated_client_with_valid_plan.plan_matter_dictionaries[plan_instance.id][
            "permanentPlanIdentifier"
        ]
        == received_plan_identifier
    )
    return authenticated_client_with_valid_plan


def test_get_plan_matters(
    client_with_plan_with_permanent_identifier: RyhtiClient,
    plan_instance: models.Plan,
    desired_plan_matter_dict: dict,
):
    """
    Check that correct JSON structure is generated for plan matter. This requires that
    the client has already marked the plan as valid and fetched a permanent identifer
    for the plan.
    """
    plan_matter = client_with_plan_with_permanent_identifier.plan_matter_dictionaries[
        plan_instance.id
    ]
    assert_dicts_equal(
        plan_matter,
        desired_plan_matter_dict,
        ignore_keys=[
            "planMatterPhaseKey",
            "handlingEventKey",
            "interactionEventKey",
            "planDecisionKey",
        ],
    )


def test_validate_plan_matters(
    client_with_plan_with_permanent_identifier: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_validate_invalid: Callable,
):
    """
    Check that JSON is posted and response received
    """
    responses = client_with_plan_with_permanent_identifier.validate_plan_matters()
    for plan_id, response in responses.items():
        assert plan_id == plan_instance.id
        assert response["errors"] == [
            {
                "ruleId": mock_matter_rule,
                "message": mock_matter_error_string,
                "instance": mock_matter_instance,
            }
        ]


def test_save_plan_matter_validation_responses(
    session: Session,
    client_with_plan_with_permanent_identifier: RyhtiClient,
    plan_instance: models.Plan,
    mock_xroad_ryhti_validate_invalid: Callable,
):
    """
    Check that Ryhti X-Road validation error is saved to database.
    """
    responses = client_with_plan_with_permanent_identifier.validate_plan_matters()
    message = client_with_plan_with_permanent_identifier.save_plan_matter_validation_responses(
        responses
    )
    session.refresh(plan_instance)
    assert plan_instance.validated_at
    assert plan_instance.validation_errors == next(iter(responses.values()))["errors"]
