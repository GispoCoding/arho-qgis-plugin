import datetime
import enum
import logging
import os
from copy import deepcopy
from typing import Any, Dict, List, Optional, TypedDict
from uuid import uuid4

import base
import boto3
import models
import requests
import simplejson as json  # type: ignore
from codes import (
    LifeCycleStatus,
    NameOfPlanCaseDecision,
    TypeOfDecisionMaker,
    TypeOfInteractionEvent,
    TypeOfProcessingEvent,
    decisionmaker_by_status,
    decisions_by_status,
    get_code,
    interaction_events_by_status,
    processing_events_by_status,
)
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
    title: str
    details: Dict[str, str]
    ryhti_responses: Dict[str, Dict]


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


class Period(TypedDict):
    begin: str
    end: str


class RyhtiClient:
    HEADERS = {
        "User-Agent": "ARHO - Open source Ryhti compatible database",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    public_api_base = "https://api.ymparisto.fi/ryhti/plan-public/api/"
    xroad_server_address = ""
    xroad_api_path = "/GOV/0996189-5/Ryhti-Syke-service/planService/api/"
    public_headers = HEADERS.copy()
    xroad_headers = HEADERS.copy()

    def __init__(
        self,
        connection_string: str,
        public_api_url: Optional[str] = None,
        public_api_key: str = "",
        xroad_syke_client_id: Optional[str] = "",
        xroad_syke_client_secret: Optional[str] = "",
        xroad_server_address: Optional[str] = None,
        xroad_instance: str = "FI-TEST",
        xroad_member_class: Optional[str] = "MUN",
        xroad_member_code: Optional[str] = None,
        xroad_member_client_name: Optional[str] = None,
        xroad_port: Optional[int] = 8080,
        event_type: int = EventType.VALIDATE_PLANS,
        plan_uuid: Optional[str] = None,
        debug_json: Optional[bool] = False,  # save JSON files for debugging
    ) -> None:
        self.event_type = event_type
        self.debug_json = debug_json

        # Public API only needs an API key and URL
        if public_api_url:
            self.public_api_base = public_api_url
        self.public_api_key = public_api_key
        self.public_headers |= {"Ocp-Apim-Subscription-Key": self.public_api_key}

        # X-Road API needs path and headers configured
        if xroad_server_address:
            self.xroad_server_address = xroad_server_address
            # do not require http in front of local dns record
            if not (
                xroad_server_address.startswith("http://")
                or xroad_server_address.startswith("https://")
            ):
                self.xroad_server_address = "http://" + self.xroad_server_address
        if xroad_port:
            self.xroad_server_address += ":" + str(xroad_port)
        # X-Road API requires specifying X-Road instance in path
        self.xroad_api_path = "/r1/" + xroad_instance + self.xroad_api_path
        # X-Road API requires headers according to the X-Road REST API spec
        # https://docs.x-road.global/Protocols/pr-rest_x-road_message_protocol_for_rest.html#4-message-format
        if xroad_member_code and xroad_member_client_name:
            self.xroad_headers |= {
                "X-Road-Client": f"{xroad_instance}/{xroad_member_class}/{xroad_member_code}/{xroad_member_client_name}"  # noqa
            }
        # In addition, X-Road Ryhti API will require authentication token that
        # will be set later based on these:
        self.xroad_syke_client_id = xroad_syke_client_id
        self.xroad_syke_client_secret = xroad_syke_client_secret

        engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=engine)
        self.plans: List[models.Plan] = []
        # Save valid plans after validation, so they can be processed further.
        self.valid_plans: List[models.Plan] = []
        # Cache plan dictionaries
        self.plan_dictionaries: Dict[str, Dict] = dict()
        # Cache plan matter dictionaries
        self.plan_matter_dictionaries: Dict[str, Dict] = dict()

        self.initiated_status: LifeCycleStatus
        self.approved_status: LifeCycleStatus
        self.valid_status: LifeCycleStatus

        # Do some prefetching before starting the run.
        #
        # Do *not* expire on commit, because we want to cache the old data in plan
        # objects throughout the session. If we want up-to date plan data, we will
        # know to explicitly refresh the object from a new session.
        #
        # Otherwise, we may access old plan data without having to create a session
        # and query.
        with self.Session(expire_on_commit=False) as session:
            # Lifecycle status "valid" is used everywhere, so let's fetch it ready.
            # TODO: check that valid status is "13" and approval status is "06" when
            # the lifecycle status code list transitions from DRAFT to VALID.
            #
            # It is exceedingly weird that this, the most important of all statuses, is
            # *not* a descriptive string, but a random number that may change, while all
            # the other code lists have descriptive strings that will *not* change.
            self.pending_status = get_code(session, LifeCycleStatus, "02")
            self.approved_status = get_code(session, LifeCycleStatus, "06")
            self.valid_status = get_code(session, LifeCycleStatus, "13")
            # Plan decisions, processing events and interaction events are best
            # prefetched, they will depend on the status of each plan:
            self.decisions_by_status = {
                status_code: (
                    [
                        get_code(session, NameOfPlanCaseDecision, decision_code)
                        for decision_code in decisions
                    ]
                    if decisions
                    else []
                )
                for status_code, decisions in decisions_by_status.items()
            }
            self.processing_events_by_status = {
                status_code: (
                    [
                        get_code(session, TypeOfProcessingEvent, processing_code)
                        for processing_code in processing_events
                    ]
                    if processing_events
                    else []
                )
                for status_code, processing_events in processing_events_by_status.items()  # noqa
            }
            self.interaction_events_by_status = {
                status_code: (
                    [
                        get_code(session, TypeOfInteractionEvent, interaction_code)
                        for interaction_code in interactions
                    ]
                    if interactions
                    else []
                )
                for status_code, interactions in interaction_events_by_status.items()
            }
            self.decisionmaker_by_status = {
                status_code: get_code(session, TypeOfDecisionMaker, decisionmaker)
                for status_code, decisionmaker in decisionmaker_by_status.items()
            }

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

    def xroad_ryhti_authenticate(self):
        # Seems that Ryhti API does not use the standard OAuth2 client credentials
        # clientId:secret Bearer header in token endpoint. Instead, there is a custom
        # authentication endpoint /api/Authenticate that wishes us to deliver the
        # client secret as a *single JSON string*, which is not compatible with
        # RFC 4627, but *is* compatible with newer RFC 8259.
        authentication_data = json.dumps(self.xroad_syke_client_secret)
        authentication_url = (
            self.xroad_server_address + self.xroad_api_path + "Authenticate"
        )
        url_params = {"clientId": self.xroad_syke_client_id}
        LOGGER.info("Authentication headers")
        LOGGER.info(self.xroad_headers)
        LOGGER.info("Authentication URL")
        LOGGER.info(authentication_url)
        LOGGER.info("Authentication data")
        LOGGER.info(authentication_data)
        LOGGER.info("URL parameters")
        LOGGER.info(url_params)
        response = requests.post(
            url=authentication_url,
            headers=self.xroad_headers,
            data=authentication_data,
            params=url_params,
        )
        LOGGER.info("Authentication response:")
        LOGGER.info(response.status_code)
        LOGGER.info(response.headers)
        LOGGER.info(response.text)
        response.raise_for_status()
        # The returned token is a jsonified string, so json() will return the bare
        # string.
        bearer_token = response.json()
        self.xroad_headers["Authorization"] = f"Bearer {bearer_token}"

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
        shape = to_shape(geometry)
        if len(shape.geoms) == 1:
            # Ryhti API may not allow single geometries in multigeometries in all cases.
            # Let's make them into single geometries instead:
            shape = shape.geoms[0]
        # Also, we don't want to serialize the geojson quite yet. Looks like the only
        # way to do get python dict to actually convert the json back to dict until we
        # are ready to reserialize it :/
        return {
            "srid": str(base.PROJECT_SRID),
            "geometry": json.loads(to_geojson(shape)),
        }

    def get_lifecycle_dates(
        self, plan_base: base.PlanBase, status: Optional[LifeCycleStatus]
    ) -> Optional[Period]:
        """
        Returns the start and end dates of a lifecycle status for object, or
        None if no dates are found.
        """
        if not status:
            # it is possible for tests etc. to look for a status that
            # is actually not present in the database at all.
            return None
        for lifecycle_date in plan_base.lifecycle_dates:
            # Note that the lifecycle status fetched from database
            # and the one in the plan are not the same sqlalchemy object,
            # because they are fetched in different sessions!
            if lifecycle_date.lifecycle_status.value == status.value:
                return {
                    "begin": (
                        lifecycle_date.starting_at.date().isoformat()
                        if lifecycle_date.starting_at
                        else None
                    ),
                    "end": (
                        lifecycle_date.ending_at.date().isoformat()
                        if lifecycle_date.ending_at
                        else None
                    ),
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
            recommendation_dict["planThemes"] = [plan_recommendation.plan_theme.uri]
        recommendation_dict["recommendationNumber"] = plan_recommendation.ordering
        recommendation_dict["periodOfValidity"] = self.get_lifecycle_dates(
            plan_recommendation, self.valid_status
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
            regulation_dict["planThemes"] = [plan_regulation.plan_theme.uri]
        if plan_regulation.name["fin"]:
            regulation_dict["subjectIdentifiers"] = [plan_regulation.name["fin"]]
        regulation_dict["regulationNumber"] = str(plan_regulation.ordering)
        regulation_dict["periodOfValidity"] = self.get_lifecycle_dates(
            plan_regulation, self.valid_status
        )
        if plan_regulation.type_of_verbal_plan_regulation:
            regulation_dict["verbalRegulations"] = [
                plan_regulation.type_of_verbal_plan_regulation.uri
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
                "dataType": "LocalizedText",
                "text": plan_regulation.text_value,
            }
        return regulation_dict

    def get_plan_regulation_group(
        self, group: models.PlanRegulationGroup, general: bool = False
    ) -> Dict:
        """
        Construct a dict of Ryhti compatible plan regulation group.

        Plan regulation groups and general regulation groups have some minor
        differences, so you can specify if you want to create a general
        regulation group.
        """
        group_dict = dict()
        if general:
            group_dict["generalRegulationGroupKey"] = group.id
        else:
            group_dict["planRegulationGroupKey"] = group.id
        group_dict["titleOfPlanRegulation"] = group.name
        #  group_dict["groupNumber"] = 1  # not needed if we only have one group
        if not general:
            group_dict["letterIdentifier"] = group.short_name
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
        plan_object_dict["periodOfValidity"] = self.get_lifecycle_dates(
            plan_object, self.valid_status
        )
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
        with self.Session(expire_on_commit=False) as session:
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
        plan_dictionary["lifeCycleStatus"] = plan.lifecycle_status.uri
        # For some reason, plan type should *not* be the full URI, but just the plan
        # type code value. It is inserted in querystring, for reasons unknown.
        plan_dictionary["planType"] = plan.plan_type.value
        plan_dictionary["scale"] = plan.scale
        plan_dictionary["geographicalArea"] = self.get_geojson(plan.geom)
        # For reasons unknown, Ryhti does not allow multilanguage description.
        plan_dictionary["planDescription"] = plan.description["fin"]
        # Apparently Ryhti plans may cover multiple administrative areas, so the region
        # identifier has to be embedded in a list.
        plan_dictionary["administrativeAreaIdentifiers"] = [
            plan.organisation.administrative_region.value
        ]

        # Here come the dependent objects. They are related to the plan directly or
        # via the plan objects, so we better fetch the objects first and then move on.
        plan_objects: List[base.PlanObjectBase] = []
        with self.Session(expire_on_commit=False) as session:
            session.add(plan)
            plan_objects += plan.land_use_areas
            plan_objects += plan.other_areas
            plan_objects += plan.lines
            plan_objects += plan.land_use_points
            plan_objects += plan.other_points
        # Our plans may only have one general regulation group.
        if plan.plan_regulation_group:
            plan_dictionary["generalRegulationGroups"] = [
                self.get_plan_regulation_group(plan.plan_regulation_group, general=True)
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
        plan_dictionary["periodOfValidity"] = self.get_lifecycle_dates(
            plan, self.valid_status
        )
        period_of_approval = self.get_lifecycle_dates(plan, self.approved_status)
        plan_dictionary["approvalDate"] = (
            period_of_approval["begin"] if period_of_approval else None
        )

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

    def get_plan_decisions(self, plan: models.Plan) -> List[Dict]:
        """
        Construct a list of Ryhti compatible plan decisions from plan in the local
        database.
        """
        decisions: List[Dict] = []
        # Decision name must correspond to the phase the plan is in. This requires
        # mapping from lifecycle statuses to decision names.
        for decision in self.decisions_by_status.get(plan.lifecycle_status.value, []):
            entry: Dict[str, Any] = dict()
            # TODO: Let's just have random uuid for now, on the assumption that each
            # phase is only POSTed to ryhti once. If planners need to post and repost
            # the same phase, script needs logic to check if the phase exists in Ryhti
            # already before reposting.
            entry["planDecisionKey"] = str(uuid4())
            entry["name"] = decision.uri
            entry["typeOfDecisionMaker"] = self.decisionmaker_by_status[
                plan.lifecycle_status.value
            ].uri
            # Plan must be embedded in decision when POSTing!
            entry["plans"] = [self.plan_dictionaries[plan.id]]

            period_of_current_status = self.get_lifecycle_dates(
                plan, plan.lifecycle_status
            )
            entry["decisionDate"] = (
                period_of_current_status["begin"] if period_of_current_status else None
            )
            entry["dateOfDecision"] = entry["decisionDate"]

            decisions.append(entry)
        return decisions

    def get_plan_handling_events(self, plan: models.Plan) -> List[Dict]:
        """
        Construct a list of Ryhti compatible plan handling events from plan in the local
        database.
        """
        events: List[Dict] = []
        # Decision name must correspond to the phase the plan is in. This requires
        # mapping from lifecycle statuses to decision names.
        for event in self.processing_events_by_status.get(
            plan.lifecycle_status.value, []
        ):
            entry: Dict[str, Any] = dict()
            # TODO: Let's just have random uuid for now, on the assumption that each
            # phase is only POSTed to ryhti once. If planners need to post and repost
            # the same phase, script needs logic to check if the phase exists in Ryhti
            # already before reposting.
            entry["handlingEventKey"] = str(uuid4())
            entry["handlingEventType"] = event.uri

            period_of_current_status = self.get_lifecycle_dates(
                plan, plan.lifecycle_status
            )
            entry["eventTime"] = (
                period_of_current_status["begin"] if period_of_current_status else None
            )

            events.append(entry)
        return events

    def get_interaction_events(self, plan: models.Plan) -> List[Dict]:
        """
        Construct a list of Ryhti compatible interaction events from plan in the local
        database.
        """
        events: List[Dict] = []
        # Decision name must correspond to the phase the plan is in. This requires
        # mapping from lifecycle statuses to decision names.
        for event in self.interaction_events_by_status.get(
            plan.lifecycle_status.value, []
        ):
            entry: Dict[str, Any] = dict()
            # TODO: Let's just have random uuid for now, on the assumption that each
            # phase is only POSTed to ryhti once. If planners need to post and repost
            # the same phase, script needs logic to check if the phase exists in Ryhti
            # already before reposting.
            entry["interactionEventKey"] = str(uuid4())
            entry["interactionEventType"] = event.uri

            period_of_current_status = self.get_lifecycle_dates(
                plan, plan.lifecycle_status
            )
            entry["eventTime"] = (
                period_of_current_status["begin"] if period_of_current_status else None
            )

            events.append(entry)
        return events

    def get_plan_matter_phases(self, plan: models.Plan) -> List[Dict]:
        """
        Construct a list of Ryhti compatible plan matter phases from plan in the local
        database.

        Currently, we only return the *current* phase, because our database does *not*
        save plan history between phases. However, we could return multiple phases or
        multiple decisions in the future, if there is a need to POST all the dates
        saved in the lifecycle_dates table.

        TODO: perhaps we will have to return multiple phases, if there may be multiple
        decision or multiple processing events in this phase. However, if we are only
        returning one phase per phase, then let's just return one phase. Simple, isn't
        it?
        """
        phase: Dict[str, Any] = dict()
        # TODO: Let's just have random uuid for now, on the assumption that each phase
        # is only POSTed to ryhti once. If planners need to post and repost the same
        # phase, script needs logic to check if the phase exists in Ryhti already before
        # reposting.
        #
        # However, such logic may not be forthcoming, if multiple phases with
        # the same lifecycle status are allowed??
        phase["planMatterPhaseKey"] = str(uuid4())
        # Always post phase and plan with the same status.
        phase["lifeCycleStatus"] = self.plan_dictionaries[plan.id]["lifeCycleStatus"]
        phase["geographicalArea"] = self.plan_dictionaries[plan.id]["geographicalArea"]

        # TODO: currently, the API spec only allows for one plan decision per phase,
        # for reasons unknown. Therefore, let's pick the first possible decision in
        # each phase.
        plan_decisions = self.get_plan_decisions(plan)
        phase["planDecision"] = plan_decisions[0] if plan_decisions else None
        # TODO: currently, the API spec only allows for one plan handling event per
        # phase, for reasons unknown. Therefore, let's pick the first possible event in
        # each phase.
        handling_events = self.get_plan_handling_events(plan)
        phase["planHandlingEvent"] = handling_events[0] if handling_events else None
        interaction_events = self.get_interaction_events(plan)
        phase["interactionEvents"] = interaction_events if interaction_events else None

        return [phase]

    def get_source_datas(self, plan: models.Plan) -> List[Dict]:
        """
        Construct a list of Ryhti compatible source datas from plan in the local
        database.
        """
        # TODO
        return []

    def get_plan_matter(self, plan: models.Plan) -> Dict:
        """
        Construct a dict of single Ryhti compatible plan matter from plan in the local
        database.
        """
        plan_dictionary = self.plan_dictionaries[plan.id]
        plan_matter = dict()
        plan_matter["permanentPlanIdentifier"] = plan_dictionary["planKey"]
        # Plan type has to be proper URI (not just value) here, *unlike* when only
        # validating plan. Go figure.
        plan_matter["planType"] = plan.plan_type.uri
        # For reasons unknown, name is needed for plan matter but not for plan. Plan
        # only contains description, and only in one language.
        plan_matter["name"] = plan.name

        period_of_initiation = self.get_lifecycle_dates(plan, self.pending_status)
        plan_matter["timeOfInitiation"] = (
            period_of_initiation["begin"] if period_of_initiation else None
        )
        # Hooray, unlike plan, the plan *matter* description allows multilanguage data!
        plan_matter["description"] = plan.description
        plan_matter["producerPlanIdentifier"] = plan.producers_plan_identifier
        plan_matter["caseIdentifiers"] = [plan.matter_management_identifier]
        plan_matter["recordNumbers"] = [plan.record_number]
        plan_matter["administrativeAreaIdentifiers"] = plan_dictionary[
            "administrativeAreaIdentifiers"
        ]
        # We have no need of importing the digital origin code list as long as we are
        # not digitizing old plans:
        plan_matter[
            "digitalOrigin"
        ] = "http://uri.suomi.fi/codelist/rytj/RY_DigitaalinenAlkupera/code/01"
        # TODO: kaava-asian liitteet
        # plan_matter["matterAnnexes"] = self.get_plan_matter_annexes(plan)
        # TODO: lähdeaineistot
        # plan_matter["sourceDatas"] = self.get_source_datas(plan)
        plan_matter["planMatterPhases"] = self.get_plan_matter_phases(plan)
        return plan_matter

    def get_plan_matters(self) -> Dict[str, Dict]:
        """
        Construct a dict of valid Ryhti compatible plan matters from valid plans in the
        local database.
        """
        plan_matters = dict()
        for plan in self.valid_plans:
            plan_matters[plan.id] = self.get_plan_matter(plan)
        return plan_matters

    def validate_plans(self) -> Dict[str, Dict]:
        """
        Validates all plans serialized in client plan dictionaries.
        """
        plan_validation_endpoint = f"{self.public_api_base}/Plan/validate"
        responses: Dict[str, Dict] = dict()
        for plan_id, plan in self.plan_dictionaries.items():
            LOGGER.info(f"Validating JSON for plan {plan_id}...")

            # For some reason (no idea why) some plan fields have to be provided
            # as query parameters, not as inline json. Shrug.
            #
            # Also, the data is *not* allowed to be in the posted plan, se we must
            # pop them out, go figure.
            plan_to_be_posted = deepcopy(plan)
            plan_type_parameter = plan_to_be_posted.pop("planType")
            # we only support one area id, no need for commas and concat:
            admin_area_id_parameter = plan_to_be_posted.pop(
                "administrativeAreaIdentifiers"
            )[0]
            if self.debug_json:
                with open(f"ryhti_debug/{plan_id}.json", "w") as plan_file:
                    json.dump(plan_to_be_posted, plan_file)
            LOGGER.info(f"POSTing JSON: {json.dumps(plan)}")

            # requests apparently uses simplejson automatically if it is installed!
            # A bit too much magic for my taste, but seems to work.
            response = requests.post(
                plan_validation_endpoint,
                json=plan_to_be_posted,
                headers=self.public_headers,
                params={
                    "planType": plan_type_parameter,
                    "administrativeAreaIdentifiers": admin_area_id_parameter,
                },
            )
            LOGGER.info(f"Got response {response}")
            if response.status_code == 200:
                # Successful validation does not return any json!
                responses[plan_id] = {"status": 200, "errors": None}
            else:
                responses[plan_id] = response.json()
            if self.debug_json:
                with open(f"ryhti_debug/{plan_id}.response.json", "w") as response_file:
                    json.dump(responses[plan_id], response_file)
            LOGGER.info(responses[plan_id])
        return responses

    def validate_plan_matters(self) -> Dict[str, Dict]:
        """
        Validates all plan matters serialized in client plan matter dictionaries.
        """
        responses: Dict[str, Dict] = dict()
        for plan_id, plan_matter in self.plan_matter_dictionaries.items():
            permanent_id = plan_matter["permanentPlanIdentifier"]
            plan_matter_validation_endpoint = (
                self.xroad_server_address
                + self.xroad_api_path
                + f"RegionalPlanMatter/{permanent_id}/validate"
            )  # TODO: Set the endpoint address to depend on plan type!
            LOGGER.info(f"Validating JSON for plan matter {permanent_id}...")

            if self.debug_json:
                with open(f"ryhti_debug/{permanent_id}.json", "w") as plan_file:
                    json.dump(plan_matter, plan_file)
            LOGGER.info(f"POSTing JSON: {json.dumps(plan_matter)}")

            # requests apparently uses simplejson automatically if it is installed!
            # A bit too much magic for my taste, but seems to work.
            response = requests.post(
                plan_matter_validation_endpoint,
                json=plan_matter,
                headers=self.xroad_headers,
            )
            LOGGER.info(f"Got response {response}")
            if response.status_code == 200:
                # Successful validation does not return any json!
                responses[plan_id] = {"status": 200, "errors": None}
            else:
                responses[plan_id] = response.json()
            if self.debug_json:
                with open(
                    f"ryhti_debug/{permanent_id}.response.json", "w"
                ) as response_file:
                    json.dump(responses[plan_id], response_file)
            LOGGER.info(responses[plan_id])
        return responses

    def get_permanent_plan_identifiers(self) -> Dict[str, str | Dict]:
        """
        Get permanent plan identifiers for all plans that are marked
        valid but do not have identifiers set yet.
        """
        plan_identifier_endpoint = (
            self.xroad_server_address
            + self.xroad_api_path
            + "RegionalPlanMatter/permanentPlanIdentifier"
        )  # TODO: Set the endpoint address to depend on plan type!
        responses: Dict[str, str | Dict] = dict()
        for plan in self.valid_plans:
            if plan.to_be_exported and not plan.permanent_plan_identifier:
                LOGGER.info(f"Getting permanent identifier for plan {plan.id}...")
                data = {
                    "administrativeAreaIdentifier": plan.organisation.administrative_region.value,  # noqa
                    "projectName": plan.producers_plan_identifier,
                }
                response = requests.post(
                    plan_identifier_endpoint, json=data, headers=self.xroad_headers
                )
                LOGGER.info(f"Got response {response}")
                if response.status_code == 200:
                    responses[plan.id] = response.json()
                else:
                    responses[plan.id] = str(response)
                if self.debug_json:
                    with open(
                        f"ryhti_debug/{plan.id}.identifier.response.json", "w"
                    ) as response_file:
                        response_file.write(str(plan_identifier_endpoint) + "\n")
                        response_file.write(str(self.xroad_headers) + "\n")
                        response_file.write(str(data) + "\n")
                        json.dump(str(responses[plan.id]), response_file)
        return responses

    def set_permanent_plan_identifiers(self, responses: Dict[str, str | Dict]):
        """
        Save permanent plan identifiers returned by RYHTI API to the database and the
        serialized plan dictionaries.
        """
        with self.Session(expire_on_commit=False) as session:
            for plan_id, response in responses.items():
                plan: models.Plan = session.get(models.Plan, plan_id)
                if isinstance(response, str):
                    plan.permanent_plan_identifier = response
                    # also update the identifier in the serialized plan!
                    self.plan_dictionaries[plan_id]["planKey"] = response
                    plan.validation_errors = (
                        "Kaava on validi. Pysyvä kaavatunnus tallennettu. Kaava-"
                        "asiaa ei ole vielä validoitu."
                    )
                else:
                    plan.validation_errors = (
                        "Kaava on validi. Ei saatu yhteyttä Palveluväylään "
                        "pysyvän kaavatunnuksen luomiseksi, joten kaava-asiaa "
                        "ei voida validoida."
                    )
            session.commit()

    def save_plan_validation_responses(self, responses: Dict[str, Dict]) -> Response:
        """
        Save open validation API response data to the database and return lambda
        response.

        If validation is successful, update validated_at field and validation_errors
        field. Also add all valid plans to client valid_plans, to be processed further.

        If validation/post is unsuccessful, save the error JSON in plan
        validation_errors json field (in addition to saving it to AWS logs and
        returning them in lambda return value).

        If Ryhti request fails unexpectedly, save the returned error.
        """
        details: Dict[str, str] = {}
        ryhti_responses: Dict[str, Dict] = {}
        with self.Session(expire_on_commit=False) as session:
            for plan_id, response in responses.items():
                plan: models.Plan = session.get(models.Plan, plan_id)
                if not plan:
                    # Plan has been deleted in the middle of validation. Nothing
                    # to see here, move on
                    LOGGER.info(
                        f"Plan {plan_id} no longer found in database! Moving on"
                    )
                    continue
                LOGGER.info(f"Saving response for plan {plan_id}...")
                LOGGER.info(response)
                # In case Ryhti API does not respond in the expected manner,
                # save the response for debugging.
                if "status" not in response or "errors" not in response:
                    details[
                        plan_id
                    ] = f"RYHTI API returned unexpected response: {response}"
                    plan.validation_errors = f"RYHTI API ERROR: {response}"
                elif response["status"] == 200:
                    details[plan_id] = f"Validation successful for {plan_id}!"
                    plan.validation_errors = (
                        "Kaava on validi. Kaava-asiaa ei ole vielä validoitu."
                    )
                    self.valid_plans.append(plan)
                else:
                    details[plan_id] = f"Validation FAILED for {plan_id}."
                    plan.validation_errors = response["errors"]

                ryhti_responses[plan_id] = response
                LOGGER.info(details[plan_id])
                LOGGER.info(f"Ryhti response: {json.dumps(response)}")
                plan.validated_at = datetime.datetime.now()
            session.commit()
        return {
            "statusCode": 200,
            "title": "Plan validations run.",
            "details": details,
            "ryhti_responses": ryhti_responses,
        }

    def save_plan_matter_validation_responses(
        self, responses: Dict[str, Dict]
    ) -> Response:
        """
        Save X-Road validation API response data to the database and return lambda
        response.

        If validation is successful, update validated_at field and validation_errors
        field. Also add all valid plan matters to client valid_plan_matters,
        to be processed further.

        If validation/post is unsuccessful, save the error JSON in plan
        validation_errors json field (in addition to saving it to AWS logs and
        returning them in lambda return value).

        If Ryhti request fails unexpectedly, save the returned error.
        """
        details: Dict[str, str] = {}
        ryhti_responses: Dict[str, Dict] = {}
        with self.Session(expire_on_commit=False) as session:
            for plan_id, response in responses.items():
                plan: models.Plan = session.get(models.Plan, plan_id)
                if not plan:
                    # Plan has been deleted in the middle of validation. Nothing
                    # to see here, move on
                    LOGGER.info(
                        f"Plan {plan_id} no longer found in database! Moving on"
                    )
                    continue
                LOGGER.info(f"Saving response for plan matter {plan_id}...")
                LOGGER.info(response)
                # In case Ryhti API does not respond in the expected manner,
                # save the response for debugging.
                if "status" not in response or "errors" not in response:
                    details[
                        plan_id
                    ] = f"RYHTI API returned unexpected response: {response}"
                    plan.validation_errors = f"RYHTI API ERROR: {response}"
                elif response["status"] == 200:
                    details[
                        plan_id
                    ] = f"Plan matter validation successful for {plan_id}!"
                    plan.validation_errors = (
                        "Kaava-asia on validi ja sen voi viedä Ryhtiin."
                    )
                    self.valid_plans.append(plan)
                else:
                    details[plan_id] = f"Plan matter validation FAILED for {plan_id}."
                    plan.validation_errors = response["errors"]

                ryhti_responses[plan_id] = response
                LOGGER.info(details[plan_id])
                LOGGER.info(f"Ryhti response: {json.dumps(response)}")
                plan.validated_at = datetime.datetime.now()
            session.commit()
        return {
            "statusCode": 200,
            "title": "Plan and plan matter validations run.",
            "details": details,
            "ryhti_responses": ryhti_responses,
        }


def handler(event: Event, _) -> Response:
    """Handler which is called when accessing the endpoint.

    If lambda runs successfully, we always return 200 OK. In case a python
    exception occurs, AWS lambda will return the exception.

    We want to return general result message of the lambda run, as well as all the
    Ryhti API results and errors, separated by plan id.
    """
    # write access is required to update plan information after
    # validating or POSTing data
    db_helper = DatabaseHelper(user=User.READ_WRITE)
    event_type = event.get("event_type", EventType.VALIDATE_PLANS)
    debug_json = event.get("save_json", False)
    plan_uuid = event.get("plan_uuid", None)
    public_api_key = os.environ.get("SYKE_APIKEY")
    if not public_api_key:
        raise ValueError(
            "Please set SYKE_APIKEY environment variable to run Ryhti client."
        )
    xroad_server_address = os.environ.get("XROAD_SERVER_ADDRESS")
    xroad_member_code = os.environ.get("XROAD_MEMBER_CODE")
    xroad_member_client_name = os.environ.get("XROAD_MEMBER_CLIENT_NAME")
    xroad_port = int(os.environ.get("XROAD_HTTP_PORT", 8080))
    xroad_instance = os.environ.get("XROAD_INSTANCE", "FI-TEST")
    xroad_member_class = os.environ.get("XROAD_MEMBER_CLASS", "MUN")
    xroad_syke_client_id = os.environ.get("XROAD_SYKE_CLIENT_ID")
    # Let's fetch the syke secret from AWS secrets, so it cannot be read in plain
    # text when looking at lambda env variables.
    if os.environ.get("READ_FROM_AWS", "1") == "1":
        session = boto3.session.Session()
        client = session.client(
            service_name="secretsmanager",
            region_name=os.environ.get("AWS_REGION_NAME"),
        )
        xroad_syke_client_secret = client.get_secret_value(
            SecretId=os.environ.get("XROAD_SYKE_CLIENT_SECRET_ARN")
        )["SecretString"]
    else:
        xroad_syke_client_secret = os.environ.get("XROAD_SYKE_CLIENT_SECRET")
    if event_type is EventType.POST_PLANS and (
        not xroad_server_address
        or not xroad_member_code
        or not xroad_member_client_name
        or not xroad_syke_client_id
        or not xroad_syke_client_secret
    ):
        raise ValueError(
            (
                "Please set your local XROAD_SERVER_ADDRESS and your organization "
                "XROAD_MEMBER_CODE and XROAD_MEMBER_CLIENT_NAME to make API requests "
                "to X-Road endpoints. Also, set XROAD_SYKE_CLIENT_ID and "
                "XROAD_SYKE_CLIENT_SECRET that you have received when registering to "
                "access SYKE X-Road API. To use production X-Road instead of test "
                "X-road, you must also set XROAD_INSTANCE to FI. By default, it "
                "is set to FI-TEST."
            )
        )

    client = RyhtiClient(
        db_helper.get_connection_string(),
        event_type=event_type,
        plan_uuid=plan_uuid,
        debug_json=debug_json,
        public_api_key=public_api_key,
        xroad_syke_client_id=xroad_syke_client_id,
        xroad_syke_client_secret=xroad_syke_client_secret,
        xroad_instance=xroad_instance,
        xroad_server_address=xroad_server_address,
        xroad_port=xroad_port,
        xroad_member_class=xroad_member_class,
        xroad_member_code=xroad_member_code,
        xroad_member_client_name=xroad_member_client_name,
    )
    if client.plans:
        # 1) Serialize plans in database
        LOGGER.info("Formatting plan data...")
        client.plan_dictionaries = client.get_plan_dictionaries()

        # 2) Validate plans in database with public API
        LOGGER.info("Validating plans...")
        responses = client.validate_plans()

        # 3) Save plan validation data
        LOGGER.info("Saving plan validation data...")
        lambda_response = client.save_plan_validation_responses(responses)

        # *Also* validate plan matter if plans are already valid.
        #
        # This can be done *without* POSTing plans, but it *will* give the plan a
        # permanent plan identifier the moment the plan itself is valid. Does this make
        # sense?
        # When we want to upload plans, we need to embed plan objects
        # further, to create kaava-asiat etc. With uploading, therefore, the
        # JSON to be POSTed is more complex, but it has plan_dictionary embedded.

        if (
            xroad_server_address
            and xroad_member_code
            and xroad_syke_client_id
            and xroad_syke_client_secret
        ):
            # Set authentication header first.
            LOGGER.info("Authenticating to X-road Ryhti API...")
            client.xroad_ryhti_authenticate()

            # Only get identifiers for those plans that are valid.
            # 4) Check or create permanent plan identifier for valid plans, from X-Road
            # API
            LOGGER.info("Getting permanent plan identifiers for valid plans...")
            plan_identifiers = client.get_permanent_plan_identifiers()

            LOGGER.info("Setting permanent plan identifiers for valid plans...")
            client.set_permanent_plan_identifiers(plan_identifiers)

            # 5) Validate plan matters with identifiers with X-Road API
            LOGGER.info("Formatting plan matter data for valid plans...")
            client.plan_matter_dictionaries = client.get_plan_matters()

            LOGGER.info("Validating plan matters for valid plans...")
            responses = client.validate_plan_matters()

            # 6) Save plan matter validation data
            LOGGER.info("Saving plan matter validation data for valid plans...")
            # Merge details and ryhti_responses for valid and invalid plans. Invalid
            # plans will have plan validation responses, valid plans will have plan
            # matter validation responses.
            plan_matter_validation_response = (
                client.save_plan_matter_validation_responses(responses)
            )
            lambda_response["title"] = plan_matter_validation_response["title"]
            lambda_response["details"] |= plan_matter_validation_response["details"]
            lambda_response["ryhti_responses"] |= plan_matter_validation_response[
                "ryhti_responses"
            ]
            if event_type is EventType.POST_PLANS:
                pass
                # 3) TODO: Check or create plan matter with the identifier
                #
                # 4) TODO: If plan matter existed, check or create plan phase instead
                #
                # 5) TODO: If plan phase existed, update plan phase instead
                #
                # 6) TODO: If documents exist, upload documents
        else:
            LOGGER.info(
                "Local XROAD_SERVER_ADDRESS, your organization XROAD_MEMBER_CODE, your "
                "XROAD_SYKE_CLIENT_ID or your XROAD_SYKE_CLIENT_SECRET "
                "not set. Cannot fetch permanent id or validate plan matters."
            )
    else:
        lambda_response = {
            "statusCode": 200,
            "title": "Plans not found in database, exiting.",
            "details": {},
            "ryhti_responses": {},
        }

    LOGGER.info(lambda_response["title"])
    return lambda_response
