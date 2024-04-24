import datetime
import enum
import logging
import os
from typing import Dict, List, Optional, TypedDict

import base
import models
import requests
import simplejson as json  # type: ignore
from codes import LifeCycleStatus
from db_helper import DatabaseHelper, User
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from shapely import to_geojson
from sqlalchemy import create_engine
from sqlalchemy.orm import Query, sessionmaker

"""
Client for validating and POSTing all Maakuntakaava data to Ryhti API
at https://api.ymparisto.fi/ryhti/plan-public/api/

Validation API:
https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Avoin/ryhti-plan-public-validate-api.json

X-Road POST API:
https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Palveluväylä/Kaavoitus%20OpenApi.json
"""

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


class EventType(enum.IntEnum):
    VALIDATE_PLANS = 1
    POST_PLANS = 2


class Response(TypedDict):
    statusCode: int  # noqa N815
    body: str


class Event(TypedDict):
    """
    Support validating or POSTing a desired plan.

    If plan_uuid is empty, all plans in database are processed. However, only
    plans that have their to_be_exported field set to true are actually POSTed.

    If save_json is true, generated JSON as well as Ryhti API response are saved
    as {plan_id}.json and {plan_id}.response.json in the ryhti_debug directory.
    """

    event_type: int  # EventType
    plan_uuid: Optional[str]  # UUID for plan to be used
    save_json: Optional[bool]  # True if we want JSON files to be saved in ryhti_debug


# def get_code_list_url(api_base: str, code_registry: str, code_list: str) -> str:
#     return f"{api_base}/{code_registry}/codeschemes/{code_list}/codes"


class RyhtiClient:
    HEADERS = {"User-Agent": "HAME - Ryhti compatible Maakuntakaava database"}
    api_base = "https://api.ymparisto.fi/ryhti/plan-public/api/"

    def __init__(
        self,
        connection_string: str,
        api_url: Optional[str] = None,
        event_type: int = EventType.VALIDATE_PLANS,
        plan_uuid: Optional[str] = None,
        debug_json: Optional[bool] = False,  # save JSON files for debugging
    ) -> None:
        self.event_type = event_type
        self.debug_json = debug_json

        if api_url:
            self.api_base = api_url
        api_key = os.environ.get("SYKE_APIKEY")
        if not api_key:
            raise ValueError(
                "Please set SYKE_APIKEY environment variable to run Ryhti client."
            )
        self.api_key = api_key

        engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=engine)
        self.plans: List[models.Plan] = []
        self.valid_status: Optional[LifeCycleStatus] = None
        self.approved_status: Optional[LifeCycleStatus] = None

        # do some prefetching before starting the run:
        with self.Session() as session:
            # Lifecycle status "valid" is used everywhere, so let's fetch it ready.
            # TODO: check that valid status is "13" and approval status is "06" when
            # the lifecycle status code list transitions from DRAFT to VALID.
            #
            # It is exceedingly weird that this, the most important of all statuses, is
            # *not* a descriptive string, but a random number that may change, while all
            # the other code lists have descriptive strings that will *not* change.
            self.valid_status = (
                session.query(LifeCycleStatus).filter_by(value="13").first()
            )
            self.approved_status = (
                session.query(LifeCycleStatus).filter_by(value="06").first()
            )
            # Only process specified plans
            plan_query: Query = session.query(models.Plan)
            if plan_uuid:
                plan_query = plan_query.filter_by(id=plan_uuid)
            self.plans = plan_query.all()
            print(plan_query.all())
        if not self.plans:
            print("no plans")
            LOGGER.info("No plans found in database.")
        else:
            print("got plans")
            LOGGER.info("Client initialized with plans to process:")
            LOGGER.info(self.plans)

    def get_geojson(self, geometry: Geometry) -> dict:
        """
        Returns geojson format dict with the correct SRID set.
        """
        # We cannot use postgis geojson functions here, because the data has already
        # been fetched from the database. So let's create geojson the python way, it's
        # probably faster than doing extra database queries for the conversion.
        # However, it seems that to_shape forgets to add the SRID information from the
        # EWKB (https://github.com/geoalchemy/geoalchemy2/issues/235), so we have to
        # paste the SRID back manually :/
        # Also, we don't want to serialize the geojson quite yet. Looks like the only
        # way to do get python dict to actually convert the json back to dict until we
        # are ready to reserialize it :/
        return {
            "srid": str(base.PROJECT_SRID),
            "geometry": json.loads(to_geojson(to_shape(geometry))),
        }

    def get_approval_date(
        self, plan_base: base.PlanBase
    ) -> Optional[datetime.datetime]:
        """
        Returns the approval date for any object that has lifecycle dates.
        They should be preloaded, so there's no need to fetch anything from db.
        """
        if self.approved_status:
            # we have to loop over the list, but it won't have that many dates
            # to begin with.
            for lifecycle_date in plan_base.lifecycle_dates:
                if lifecycle_date.lifecycle_status is self.approved_status:
                    # This will return the first valid dates. Here we assume that
                    # there cannot be several approved periods.
                    return lifecycle_date.starting_at
        return None

    def get_period_of_validity(self, plan_base: base.PlanBase) -> Optional[dict]:
        """
        Returns the period of validity for any object that has lifecycle dates.
        They should be preloaded, so there's no need to fetch anything from db.
        """
        if self.valid_status:
            # we have to loop over the list, but it won't have that many dates
            # to begin with.
            for lifecycle_date in plan_base.lifecycle_dates:
                if lifecycle_date.lifecycle_status is self.valid_status:
                    # This will return the first valid dates. Here we assume that
                    # there cannot be several valid periods.
                    return {
                        "begin": lifecycle_date.starting_at,
                        "end": lifecycle_date.ending_at,
                    }
        return None

    def get_plan_recommendation(
        self, plan_recommendation: models.PlanProposition
    ) -> Dict:
        """
        Construct a dict of Ryhti compatible plan recommendation.
        """
        recommendation_dict = dict()
        recommendation_dict["planRecommendationKey"] = plan_recommendation.id
        recommendation_dict[
            "lifeCycleStatus"
        ] = plan_recommendation.lifecycle_status.uri
        if plan_recommendation.plan_theme:
            recommendation_dict["planThemes"] = [
                {"type": plan_recommendation.plan_theme.uri}
            ]
        recommendation_dict["recommendationNumber"] = plan_recommendation.ordering
        recommendation_dict["periodOfValidity"] = self.get_period_of_validity(
            plan_recommendation
        )
        recommendation_dict["value"] = plan_recommendation.text_value
        return recommendation_dict

    def get_plan_regulation(self, plan_regulation: models.PlanRegulation) -> Dict:
        """
        Construct a dict of Ryhti compatible plan regulation.
        """
        regulation_dict = dict()
        regulation_dict["planRegulationKey"] = plan_regulation.id
        regulation_dict["lifeCycleStatus"] = plan_regulation.lifecycle_status.uri
        regulation_dict["type"] = plan_regulation.type_of_plan_regulation.uri
        if plan_regulation.plan_theme:
            regulation_dict["planThemes"] = [{"type": plan_regulation.plan_theme.uri}]
        if plan_regulation.name["fin"]:
            regulation_dict["subjectIdentifiers"] = [plan_regulation.name["fin"]]
        regulation_dict["regulationNumber"] = plan_regulation.ordering
        regulation_dict["periodOfValidity"] = self.get_period_of_validity(
            plan_regulation
        )
        if plan_regulation.type_of_verbal_plan_regulation:
            regulation_dict["verbalRegulations"] = [
                {"type": plan_regulation.type_of_verbal_plan_regulation.uri}
            ]
        regulation_dict["additionalInformations"] = []
        for code_value in [
            plan_regulation.intended_use,
            plan_regulation.existence,
            plan_regulation.regulation_type_additional_information,
            plan_regulation.significance,
            plan_regulation.reservation,
            plan_regulation.development,
            plan_regulation.disturbance_prevention,
            plan_regulation.construction_control,
        ]:
            if code_value:
                regulation_dict["additionalInformations"].append(
                    {"type": code_value.uri}
                )
        if plan_regulation.numeric_value:
            regulation_dict["value"] = {
                "dataType": "decimal",
                # we have to use simplejson because numbers are Decimal
                "number": plan_regulation.numeric_value,
                "unitOfMeasure": plan_regulation.unit,
            }
        elif plan_regulation.text_value:
            regulation_dict["value"] = {
                "dataType": "text",
                **plan_regulation.text_value,
            }
        return regulation_dict

    def get_plan_regulation_group(self, group: models.PlanRegulationGroup) -> Dict:
        """
        Construct a dict of Ryhti compatible plan regulation group.
        """
        group_dict = dict()
        group_dict["planRegulationGroupKey"] = group.id
        group_dict["titleOfPlanRegulation"] = group.name
        #  group_dict["groupNumber"] = 1  # not needed if we only have one group
        group_dict["letterIdentifier"] = group.short_name
        #  group_dict["localId"] = "blah"  # TODO: this is probably not needed?
        group_dict["colorNumber"] = "#FFFFFF"
        group_dict["planRecommendations"] = []
        for recommendation in group.plan_propositions:
            group_dict["planRecommendations"].append(
                self.get_plan_recommendation(recommendation)
            )
        group_dict["planRegulations"] = []
        for regulation in group.plan_regulations:
            group_dict["planRegulations"].append(self.get_plan_regulation(regulation))
        return group_dict

    def get_plan_object(self, plan_object: base.PlanObjectBase) -> Dict:
        """
        Construct a dict of Ryhti compatible plan object.
        """
        plan_object_dict = dict()
        plan_object_dict["planObjectKey"] = plan_object.id
        plan_object_dict["lifeCycleStatus"] = plan_object.lifecycle_status.uri
        plan_object_dict["undergroundStatus"] = plan_object.type_of_underground.uri
        plan_object_dict["geometry"] = self.get_geojson(plan_object.geom)
        plan_object_dict["name"] = plan_object.name
        plan_object_dict["description"] = plan_object.description
        plan_object_dict["objectNumber"] = plan_object.ordering
        plan_object_dict["periodOfValidity"] = self.get_period_of_validity(plan_object)
        if plan_object.height_range:
            plan_object_dict["verticalLimit"] = {
                "dataType": "decimalRange",
                # we have to use simplejson because numbers are Decimal
                "minimumValue": plan_object.height_range.lower,
                "maximumValue": plan_object.height_range.upper,
                "unitOfMeasure": plan_object.height_unit,
            }
        return plan_object_dict

    def get_plan_object_dicts(self, plan_objects: List[base.PlanObjectBase]) -> List:
        """
        Construct a list of Ryhti compatible plan object dicts from plan objects
        in the local database.
        """
        plan_object_dicts = []
        for plan_object in plan_objects:
            plan_object_dicts.append(self.get_plan_object(plan_object))
        return plan_object_dicts

    def get_plan_regulation_groups(
        self, plan_objects: List[base.PlanObjectBase]
    ) -> List:
        """
        Construct a list of Ryhti compatible plan regulation groups from plan objects
        in the local database.
        """
        group_dicts = []
        group_ids = set(
            [plan_object.plan_regulation_group_id for plan_object in plan_objects]
        )
        # Let's fetch all the plan regulation groups for all the objects with a single
        # query. Hoping lazy loading does its trick with all the plan regulations.
        with self.Session() as session:
            plan_regulation_groups = (
                session.query(models.PlanRegulationGroup)
                .filter(models.PlanRegulationGroup.id.in_(group_ids))
                .all()
            )
            for group in plan_regulation_groups:
                group_dicts.append(self.get_plan_regulation_group(group))
        return group_dicts

    def get_plan_regulation_group_relations(
        self, plan_objects: List[base.PlanObjectBase]
    ) -> List:
        """
        Construct a list of Ryhti compatible plan regulation group relations from plan
        objects in the local database.
        """
        relation_dicts = []
        for plan_object in plan_objects:
            relation_dicts.append(
                {
                    "planObjectKey": plan_object.id,
                    "planRegulationGroupKey": plan_object.plan_regulation_group_id,
                }
            )
        return relation_dicts

    # TODO: plan documents not implemented yet!

    def get_plan_dictionary(self, plan: models.Plan) -> Dict:
        """
        Construct a dict of single Ryhti compatible plan from plan in the
        local database.
        """
        plan_dictionary = dict()

        if plan.permanent_plan_identifier:
            # When uploading plans, the plan key needs to be obtained from Ryhti
            # and saved to the database. When we are only validating, it is OK to use
            # our database uuid, in case the plan has no Ryhti identifier yet.
            plan_dictionary["planKey"] = plan.permanent_plan_identifier
        else:
            plan_dictionary["planKey"] = plan.id
        # Let's have all the code values preloaded joined from db.
        # It makes this super easy:
        plan_dictionary["planType"] = plan.plan_type.uri
        plan_dictionary["lifeCycleStatus"] = plan.lifecycle_status.uri
        plan_dictionary["scale"] = plan.scale
        plan_dictionary["geographicalArea"] = self.get_geojson(plan.geom)
        plan_dictionary["planDescription"] = plan.description
        # Apparently Ryhti plans may cover multiple administrative areas, so the region
        # identifier has to be embedded in a list.
        plan_dictionary["administrativeAreaIdentifiers"] = [
            plan.organisation.administrative_region.value
        ]

        # Here come the dependent objects. They are related to the plan directly or
        # via the plan objects, so we better fetch the objects first and then move on.
        plan_objects: List[base.PlanObjectBase] = []
        with self.Session() as session:
            session.add(plan)
            plan_objects += plan.land_use_areas
            plan_objects += plan.other_areas
            plan_objects += plan.lines
            plan_objects += plan.land_use_points
            plan_objects += plan.other_points
        # Our plans may only have one general regulation group.
        if plan.plan_regulation_group:
            plan_dictionary["generalRegulationGroups"] = [
                self.get_plan_regulation_group(plan.plan_regulation_group)
            ]
        # Our plans have lots of different plan objects, each of which has one plan
        # regulation group.
        plan_dictionary["planObjects"] = self.get_plan_object_dicts(plan_objects)
        plan_dictionary["planRegulationGroups"] = self.get_plan_regulation_groups(
            plan_objects
        )
        plan_dictionary[
            "planRegulationGroupRelations"
        ] = self.get_plan_regulation_group_relations(plan_objects)
        # Dates come from plan lifecycle dates.
        plan_dictionary["periodOfValidity"] = self.get_period_of_validity(plan)
        plan_dictionary["approvalDate"] = self.get_approval_date(plan)

        return plan_dictionary

    def get_plan_dictionaries(self) -> Dict[str, Dict]:
        """
        Construct a dict of valid Ryhti compatible plan dictionaries from plans in the
        local database.
        """
        plan_dictionaries = dict()
        for plan in self.plans:
            plan_dictionaries[plan.id] = self.get_plan_dictionary(plan)
        return plan_dictionaries

    def validate_plans(self, plan_objects: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Validates all specified plans in list.
        """
        responses: Dict[str, Dict] = dict()
        for plan_id, plan in plan_objects.items():
            LOGGER.info(f"Validating JSON for plan {plan_id}...")
            if self.debug_json:
                with open(f"ryhti_debug/{plan_id}.json", "w") as plan_file:
                    json.dump(plan, plan_file)
            # requests apparently uses simplejson automatically if it is installed!
            # A bit too much magic for my taste, but seems to work.
            responses[plan_id] = requests.post(
                f"{self.api_base}/Plan/validate",
                json=plan,
                headers={
                    **self.HEADERS,
                    "Content-Type": "application/json",
                    "Ocp-Apim-Subscription-Key": self.api_key,
                },
                # For some reason (no idea why) some plan data has to be provided
                # as query params, not as inline json. Shrug.
                params={
                    "planType": plan["planType"],
                    # we only support one area id, no need for commas and concat:
                    "administrativeAreaIdentifiers": plan[
                        "administrativeAreaIdentifiers"
                    ][0],
                },
            ).json()
            LOGGER.info(f"Got response {responses[plan_id]}")
            if self.debug_json:
                with open(f"ryhti_debug/{plan_id}.response.json", "w") as response_file:
                    json.dump(responses[plan_id], response_file)
        return responses

    def save_responses(self, responses: Dict[str, Dict]) -> str:
        """
        Save RYHTI API response data to the database.

        If validation is successful, just update validated_at field.

        If POST is successful, update exported_at, to_be_exported and
        any ids received from the Ryhti API.

        If validation/post is unsuccessful, save the error JSON in plan
        validation_errors json field (in addition to saving it to AWS logs).
        """
        msg = ""
        with self.Session() as session:
            for plan_id, response in responses.items():
                plan: models.Plan = session.get(models.Plan, plan_id)
                if "errors" in response.keys():
                    msg += f"Validation FAILED for {plan_id}. Errors:"
                    msg += response["errors"]
                    plan.validation_errors = response["errors"]
                else:
                    msg += f"Validation successful for {plan_id}!"
                    plan.validation_errors = None
                plan.validated_at = datetime.datetime.now()
            session.commit()
        LOGGER.info(msg)
        return msg


def handler(event: Event, _) -> Response:
    """Handler which is called when accessing the endpoint."""
    response: Response = {"statusCode": 200, "body": json.dumps("")}
    # write access is required to update plan information after
    # validating or POSTing data
    db_helper = DatabaseHelper(user=User.READ_WRITE)
    event_type = event.get("event_type", EventType.VALIDATE_PLANS)
    debug_json = event.get("save_json", False)
    plan_uuid = event.get("plan_uuid", None)

    client = RyhtiClient(
        db_helper.get_connection_string(),
        event_type=event_type,
        plan_uuid=plan_uuid,
        debug_json=debug_json,
    )
    if client.plans:
        LOGGER.info("Formatting plan data...")
        plan_dictionaries = client.get_plan_dictionaries()

        # TODO: when we want to upload plans, we need to embed plan objects
        # further, to create kaava-asiat etc. With uploading, therefore, the
        # JSON to be POSTed is more complex, but it has plan_object embedded.
        LOGGER.info("Validating plans...")
        responses = client.validate_plans(plan_dictionaries)

        LOGGER.info("Saving response data...")
        msg = client.save_responses(responses)
    else:
        msg = "Plans not found in database, exiting."

    LOGGER.info(msg)
    response["body"] = json.dumps(msg)
    return response
