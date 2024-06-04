import datetime
import enum
import logging
import os
from typing import Any, Dict, List, Optional, TypedDict
from uuid import uuid4

import base
import models
import requests
import simplejson as json  # type: ignore
from codes import (
    LifeCycleStatus,
    NameOfPlanCaseDecision,
    TypeOfInteractionEvent,
    TypeOfProcessingEvent,
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
    begin: datetime.date
    end: datetime.date


class RyhtiClient:
    HEADERS = {"User-Agent": "HAME - Ryhti compatible Maakuntakaava database"}
    public_api_base = "https://api.ymparisto.fi/ryhti/plan-public/api/"
    xroad_api_path = "/r1/FI/GOV/0996189-5/Ryhti-Syke-Service/api/"
    xroad_server_address = ""
    xroad_client_id_base = "FI/MUN/"
    xroad_member_code = ""

    def __init__(
        self,
        connection_string: str,
        public_api_url: Optional[str] = None,
        public_api_key: str = "",
        xroad_server_address: Optional[str] = None,
        xroad_member_code: Optional[str] = None,
        event_type: int = EventType.VALIDATE_PLANS,
        plan_uuid: Optional[str] = None,
        debug_json: Optional[bool] = False,  # save JSON files for debugging
    ) -> None:
        self.event_type = event_type
        self.debug_json = debug_json

        # Public API only needs an API key
        if public_api_url:
            self.public_api_base = public_api_url
        self.public_api_key = public_api_key
        self.public_headers = {
            **self.HEADERS,
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.public_api_key,
        }

        # X-Road API requires headers according to the X-Road REST API spec
        # https://docs.x-road.global/Protocols/pr-rest_x-road_message_protocol_for_rest.html#4-message-format
        if xroad_server_address:
            self.xroad_server_address = xroad_server_address
        if xroad_member_code:
            self.xroad_member_code = xroad_member_code
        self.xroad_headers = {
            **self.HEADERS,
            "Content-Type": "application/json",
            "X-Road-Client": self.xroad_client_id_base + self.xroad_member_code,
        }

        engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=engine)
        self.plans: List[models.Plan] = []
        # Cache plan dictionaries in case we want to POST them after validation
        self.plan_dictionaries: Dict[str, Dict] = dict()
        self.initiated_status: LifeCycleStatus
        self.approved_status: LifeCycleStatus
        self.valid_status: LifeCycleStatus

        # do some prefetching before starting the run:
        with self.Session() as session:
            # Lifecycle status "valid" is used everywhere, so let's fetch it ready.
            # TODO: check that valid status is "13" and approval status is "06" when
            # the lifecycle status code list transitions from DRAFT to VALID.
            #
            # It is exceedingly weird that this, the most important of all statuses, is
            # *not* a descriptive string, but a random number that may change, while all
            # the other code lists have descriptive strings that will *not* change.
            self.initiated_status = get_code(session, LifeCycleStatus, "01")
            self.approved_status = get_code(session, LifeCycleStatus, "06")
            self.valid_status = get_code(session, LifeCycleStatus, "13")
            # Plan decisions, processing events and interaction events are best
            # prefetched, they will depend on the status of each plan:
            self.decisions_by_status = {
                status_code: [
                    get_code(session, NameOfPlanCaseDecision, decision_code)
                    for decision_code in decisions
                ]
                if decisions
                else []
                for status_code, decisions in decisions_by_status.items()
            }
            self.processing_events_by_status = {
                status_code: [
                    get_code(session, TypeOfProcessingEvent, processing_code)
                    for processing_code in processing_events
                ]
                if processing_events
                else []
                for status_code, processing_events in processing_events_by_status.items()  # noqa
            }
            self.interaction_events_by_status = {
                status_code: [
                    get_code(session, TypeOfInteractionEvent, interaction_code)
                    for interaction_code in interactions
                ]
                if interactions
                else []
                for status_code, interactions in interaction_events_by_status.items()
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

    def get_lifecycle_dates(
        self, plan_base: base.PlanBase, status: LifeCycleStatus
    ) -> Optional[Period]:
        """
        Returns the start and end dates of a lifecycle status for object, or
        None if no dates are found.
        """
        for lifecycle_date in plan_base.lifecycle_dates:
            if lifecycle_date.lifecycle_status is status:
                return {
                    "begin": lifecycle_date.starting_at.date()
                    if lifecycle_date.starting_at
                    else None,
                    "end": lifecycle_date.ending_at.date()
                    if lifecycle_date.ending_at
                    else None,
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
            entry["planDecisionKey"] = uuid4()
            entry["name"] = decision.url

            period_of_current_status = self.get_lifecycle_dates(
                plan, plan.lifecycle_status.value
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
            entry["handlingEventKey"] = uuid4()
            entry["handlingEventType"] = event.url

            period_of_current_status = self.get_lifecycle_dates(
                plan, plan.lifecycle_status.value
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
            entry["interactionEventKey"] = uuid4()
            entry["interactionEventType"] = event.url

            period_of_current_status = self.get_lifecycle_dates(
                plan, plan.lifecycle_status.value
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
        phase["planMatterPhaseKey"] = uuid4()
        # Always post phase and plan with the same status.
        phase["lifeCycleStatus"] = self.plan_dictionaries["lifeCycleStatus"]
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
        plan_matter["planType"] = plan_dictionary["planType"]

        period_of_initiation = self.get_lifecycle_dates(plan, self.initiated_status)
        plan_matter["timeOfInitiation"] = (
            period_of_initiation["begin"] if period_of_initiation else None
        )
        # Hooray, unlike plan, the plan *matter* description allows multilanguage data!
        plan_matter["description"] = plan.description
        plan_matter["producerPlanIdentifier"] = plan.producers_plan_identifier
        plan_matter["caseIdentifiers"] = [plan.matter_management_identifier]
        plan_matter["recordNumbers"] = [plan.record_number]
        # Oh great, now plan matter *needs* the administrative area identifiers that
        # are *forbidden* to be present in plan dictionary and had to be removed
        plan_matter["administrativeAreaIdentifiers"] = [
            plan.organisation.administrative_region.value
        ]
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
        Construct a dict of valid Ryhti compatible plan matters from plans in the local
        database.
        """
        plan_matters = dict()
        for plan in self.plans:
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
            # Also, the data is *not* allowed to be in the actual plan, se we must
            # pop them out, go figure.
            plan_type_parameter = plan.pop("planType")
            # we only support one area id, no need for commas and concat:
            admin_area_id_parameter = plan.pop("administrativeAreaIdentifiers")[0]
            if self.debug_json:
                with open(f"ryhti_debug/{plan_id}.json", "w") as plan_file:
                    json.dump(plan, plan_file)
            LOGGER.info(f"POSTing JSON: {json.dumps(plan)}")

            # requests apparently uses simplejson automatically if it is installed!
            # A bit too much magic for my taste, but seems to work.
            response = requests.post(
                plan_validation_endpoint,
                json=plan,
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

    def get_permanent_plan_identifiers(self) -> Dict[str, str | Dict]:
        """
        Get permanent plan identifiers for all plans that are marked
        ready to be exported to Ryhti but do not have identifiers set yet.
        """
        plan_identifier_endpoint = (
            self.xroad_server_address
            + self.xroad_api_path
            + "RegionalPlanMatter/permanentPlanIdentifier"
        )
        responses: Dict[str, str | Dict] = dict()
        print(self.plans)
        for plan in self.plans:
            print(plan)
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
                    responses[plan.id] = response.text
                else:
                    responses[plan.id] = response.json()
                if self.debug_json:
                    with open(
                        f"ryhti_debug/{plan.id}.identifier.response.json", "w"
                    ) as response_file:
                        json.dump(responses[plan.id], response_file)
        return responses

    def set_permanent_plan_identifiers(self, responses: Dict[str, str | Dict]):
        """
        Save permanent plan identifiers returned by RYHTI API to the database and the
        serialized plan dictionaries.
        """
        with self.Session() as session:
            for plan_id, response in responses.items():
                if type(response) is str:
                    plan: models.Plan = session.get(models.Plan, plan_id)
                    plan.permanent_plan_identifier = response
                    # also update the identifier in the serialized plan!
                    self.plan_dictionaries[plan_id]["planKey"] = response
                else:
                    raise ValueError(
                        (
                            "Ryhti API returned error when asking for plan identifier: "
                            "{response}"
                        )
                    )
            session.commit()

    def save_responses(self, responses: Dict[str, Dict]) -> Response:
        """
        Save RYHTI API response data to the database and return lambda response.

        If validation is successful, just update validated_at field.

        If POST is successful, update exported_at, to_be_exported and
        any ids received from the Ryhti API.

        If validation/post is unsuccessful, save the error JSON in plan
        validation_errors json field (in addition to saving it to AWS logs and
        returning them in lambda return value).

        If Ryhti request fails unexpectedly, save the returned error.
        """
        details: Dict[str, str] = {}
        ryhti_responses: Dict[str, Dict] = {}
        with self.Session() as session:
            for plan_id, response in responses.items():
                plan: models.Plan = session.get(models.Plan, plan_id)
                print(response)
                # In case Ryhti API does not respond in the expected manner,
                # save the response for debugging.
                if "status" not in response:
                    details[
                        plan_id
                    ] = f"RYHTI API returned unexpected response: {response}"
                    plan.validation_errors = f"RYHTI API ERROR: {response}"
                elif response["status"] == 200:
                    details[plan_id] = f"Validation successful for {plan_id}!"
                    plan.validation_errors = None
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
    if event_type is EventType.POST_PLANS and (
        not xroad_server_address or not xroad_member_code
    ):
        raise ValueError(
            (
                "Please set your local XROAD_SERVER_ADDRESS and your organization"
                "XROAD_MEMBER_CODE to make API requests to X-Road endpoints."
            )
        )

    client = RyhtiClient(
        db_helper.get_connection_string(),
        event_type=event_type,
        plan_uuid=plan_uuid,
        debug_json=debug_json,
        public_api_key=public_api_key,
        xroad_server_address=xroad_server_address,
        xroad_member_code=xroad_member_code,
    )
    if client.plans:
        LOGGER.info("Formatting plan data...")
        client.plan_dictionaries = client.get_plan_dictionaries()

        LOGGER.info("Validating plans...")
        responses = client.validate_plans()

        LOGGER.info("Saving validation data...")
        lambda_response = client.save_responses(responses)

        # TODO: Add logic to *also* validate plan matter if plans are already valid.
        #
        # This can be done *without* POSTing plans, but it *will* give the plan a
        # permanent plan identifier the moment the plan itself is valid. Does this make
        # sense?
        if event_type is EventType.POST_PLANS:
            # When we want to upload plans, we need to embed plan objects
            # further, to create kaava-asiat etc. With uploading, therefore, the
            # JSON to be POSTed is more complex, but it has plan_dictionary embedded.

            # 1) Check or create permanent plan identifier
            LOGGER.info("Getting permanent plan identifiers...")
            plan_identifiers = client.get_permanent_plan_identifiers()

            LOGGER.info("Setting permanent plan identifiers...")
            client.set_permanent_plan_identifiers(plan_identifiers)

            # 2) TODO: Validate plan matter with the identifier
            LOGGER.info("Formatting plan matter data...")
            client.get_plan_matters()

            # LOGGER.info("Validating plan matters...")
            # responses = client.validate_plan_matters(plan_matter_dictionaries)
            #
            # 3) TODO: Check or create plan matter with the identifier
            #
            # 4) TODO: If plan matter existed, check or create plan phase instead
            #
            # 5) TODO: If plan phase existed, update plan phase instead
            #
            # 6) TODO: If documents exist, upload documents
    else:
        lambda_response = {
            "statusCode": 200,
            "title": "Plans not found in database, exiting.",
            "details": {},
            "ryhti_responses": {},
        }

    LOGGER.info(lambda_response["title"])
    return lambda_response
