import codes
import models
import pytest
from ryhti_client.ryhti_client import RyhtiClient
from sqlalchemy.orm import Session


@pytest.fixture(scope="module")
def desired_plan_dict(
    plan_instance: models.Plan,
    land_use_area_instance: models.LandUseArea,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
) -> dict:
    """
    Plan dict based on https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Avoin/Esimerkki-sanomat/Esimerkki_json_kaavasuunnitelma_asemakaava.pdf

    Let's 1) write explicitly the complex fields, and 2) just check that the simple fields have
    the same values as the original plan fixture in the database.
    """

    return {
        "planKey": plan_instance.id,
        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/test",
        "scale": plan_instance.scale,
        "geographicalArea": {
            "srid": "3067",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]],
            },
        },
        # TODO: general regulation group to be added.
        # TODO: plan documents to be added.
        # TODO: dates of validity to be added. These need fixtures with specific codes.
        # TODO: general regulation group to be added. This needs fixture with specific code.
        "planDescription": plan_instance.description,  # TODO: should this be a single language string? why?
        "PlanObjects": [
            {
                "planObjectKey": land_use_area_instance.id,
                "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/test",
                "undergroundStatus": "http://uri.suomi.fi/codelist/rytj/RY_MaanalaisuudenLaji/code/test",
                "geometry": {
                    "srid": "3067",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [[0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]
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
                }
                # TODO: dates of validity to be added. These need fixtures with specific codes.
            },
        ],
        "planRegulationGroups": [
            {
                "planRegulationGroupKey": plan_regulation_group_instance.id,
                "titleOfPlanRegulation": plan_regulation_group_instance.name,
                "planRegulations": [
                    {
                        "planRegulationKey": plan_regulation_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/test",
                        "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayslaji/code/test",
                        "value": {
                            "dataType": "decimal",
                            "number": plan_regulation_instance.numeric_value,
                            "unitOfMeasure": plan_regulation_instance.unit,
                        },
                        "subjectIdentifiers": [
                            {
                                plan_regulation_instance.name[
                                    "fin"
                                ]  # TODO: onko asiasana aina yksikielinen??
                            }
                        ],
                        "verbalRegulations": [
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Sanallisen_Kaavamaarayksen_Laji/code/test"
                            }
                        ],
                        "additionalInformations": [
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/RY_Kaavamaarayksen_Lisatiedonlaji/code/test"
                            }
                        ],
                        "planThemes": [
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/test"
                            }
                        ],
                        "regulationNumber": plan_regulation_instance.ordering
                        # TODO: plan regulation documents to be added.
                        # TODO: dates of validity to be added. These need fixtures with specific codes.
                    },
                ],
                "planRecommendations": [
                    {
                        "planRecommendationKey": plan_proposition_instance.id,
                        "lifeCycleStatus": "http://uri.suomi.fi/codelist/rytj/kaavaelinkaari/code/test",
                        "value": plan_proposition_instance.text_value,
                        "planThemes": [
                            {
                                "type": "http://uri.suomi.fi/codelist/rytj/kaavoitusteema/code/test"
                            }
                        ],
                        "regulationNumber": plan_proposition_instance.ordering
                        # TODO: plan recommendation documents to be added.
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


@pytest.fixture(scope="module")
def client_with_plan_data(
    session: Session,
    connection_string: str,
    plan_instance: models.Plan,
    land_use_area_instance: models.LandUseArea,
    plan_regulation_group_instance: models.PlanRegulationGroup,
    plan_regulation_instance: models.PlanRegulation,
    plan_proposition_instance: models.PlanProposition,
    plan_theme_instance: codes.PlanTheme,
    type_of_additional_information_instance: codes.TypeOfAdditionalInformation,
) -> RyhtiClient:
    """
    Return RyhtiClient that has plan data read in.

    We have to create the plan data in the database before returning the client, because the client
    reads plans from the database when initializing.
    """
    # Add the optional (nullable) relationships. We don't want them to be present in all fixtures.
    plan_regulation_instance.plan_theme = plan_theme_instance
    plan_proposition_instance.intended_use = type_of_additional_information_instance
    session.commit()

    return RyhtiClient(
        connection_string,
        api_url="http://mock.url",
    )


def test_get_plan_dictionaries(
    client_with_plan_data: RyhtiClient,
    plan_instance: models.Plan,
    desired_plan_dict: dict,
):
    """
    Check that correct json structure is generated
    """
    result_plan_dicts = client_with_plan_data.get_plan_dictionaries()
    result_plan_dict = result_plan_dicts[plan_instance.id]
    print(result_plan_dict)
    for key, value in desired_plan_dict.items():
        print(f"checking {key}")
        print(value)
        assert result_plan_dict[key] == value
