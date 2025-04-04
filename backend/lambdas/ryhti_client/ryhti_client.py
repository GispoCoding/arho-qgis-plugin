import datetime
import email.utils
import enum
import logging
import os
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Type, TypedDict, cast
from uuid import uuid4
from zoneinfo import ZoneInfo

import boto3
import requests
import simplejson as json  # type: ignore
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from requests_toolbelt import MultipartEncoder
from shapely import to_geojson
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Query, sessionmaker

from database import base, models
from database.codes import (
    NameOfPlanCaseDecision,
    TypeOfDecisionMaker,
    TypeOfInteractionEvent,
    TypeOfProcessingEvent,
    decisionmaker_by_status,
    decisions_by_status,
    get_code_uri,
    interaction_events_by_status,
    processing_events_by_status,
)
from database.db_helper import DatabaseHelper, User
from database.enums import AttributeValueDataType

if TYPE_CHECKING:
    import uuid

"""
Client for validating and POSTing all Maakuntakaava data to Ryhti API
at https://api.ymparisto.fi/ryhti/plan-public/api/

Validation API:
https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Avoin/ryhti-plan-public-validate-api.json

X-Road POST API:
https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Palveluväylä/Kaavoitus%20OpenApi.json
"""

# All non-request specific initialization should be done *before* the handler
# method is run. It is run with burst CPU, so we will get faster initialization.
# Boto3 and db helper initialization should go here.
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOCAL_TZ = ZoneInfo("Europe/Helsinki")

# write access is required to update plan information after
# validating or POSTing data
db_helper = DatabaseHelper(user=User.READ_WRITE)
# Let's fetch the syke secret from AWS secrets, so it cannot be read in plain
# text when looking at lambda env variables.
if os.environ.get("READ_FROM_AWS", "1") == "1":
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=os.environ.get("AWS_REGION_NAME", ""),
    )
    xroad_syke_client_secret = client.get_secret_value(
        SecretId=os.environ.get("XROAD_SYKE_CLIENT_SECRET_ARN", "")
    )["SecretString"]
else:
    xroad_syke_client_secret = os.environ.get("XROAD_SYKE_CLIENT_SECRET", "")
public_api_key = os.environ.get("SYKE_APIKEY", "")
if not public_api_key:
    raise ValueError("Please set SYKE_APIKEY environment variable to run Ryhti client.")
xroad_server_address = os.environ.get("XROAD_SERVER_ADDRESS", "")
xroad_member_code = os.environ.get("XROAD_MEMBER_CODE", "")
xroad_member_client_name = os.environ.get("XROAD_MEMBER_CLIENT_NAME", "")
xroad_port = int(os.environ.get("XROAD_HTTP_PORT", 8080))
xroad_instance = os.environ.get("XROAD_INSTANCE", "FI-TEST")
xroad_member_class = os.environ.get("XROAD_MEMBER_CLASS", "MUN")
xroad_syke_client_id = os.environ.get("XROAD_SYKE_CLIENT_ID", "")


class Action(enum.Enum):
    VALIDATE_PLANS = "validate_plans"
    POST_PLANS = "post_plans"
    GET_PLANS = "get_plans"


class RyhtiResponse(TypedDict):
    """
    Represents the response of the Ryhti API to a single API all.
    """

    status: int | None
    detail: Optional[str]
    errors: Optional[dict]
    warnings: Optional[dict]


class ResponseBody(TypedDict):
    """
    Data returned in lambda function response.
    """

    title: str
    details: Dict[str, str]
    ryhti_responses: Dict[str, RyhtiResponse]


class Response(TypedDict):
    """
    Represents the response of the lambda function to the caller.

    Let's abide by the AWS API Gateway 2.0 response format. If we want to specify
    a custom status code, this means that other data must be embedded in request body.

    https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
    """

    statusCode: int  # noqa N815
    body: ResponseBody


class Event(TypedDict):
    """
    Support validating, POSTing or getting a desired plan. If provided directly to
    lambda, the lambda request needs only contain these keys.

    If plan_uuid is empty, all plans in database are processed. However, only
    plans that have their to_be_exported field set to true are actually POSTed.

    If save_json is true, generated JSON as well as Ryhti API response are saved
    as {plan_id}.json and {plan_id}.response.json in the ryhti_debug directory.
    """

    action: str  # Action
    plan_uuid: Optional[str]  # UUID for plan to be used
    save_json: Optional[bool]  # True if we want JSON files to be saved in ryhti_debug


class AWSAPIGatewayPayload(TypedDict):
    """
    Represents the request coming to Lambda through AWS API Gateway.

    The same request may arrive to lambda either through AWS integrations or API
    Gateway. If arriving through the API Gateway, it will contain all data that
    were contained in the whole HTTPS request, and the event is found in request body.

    https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
    """

    version: Literal["2.0"]
    headers: Dict
    queryStringParameters: Dict
    requestContext: Dict
    body: str  # The event is stringified json, we have to jsonify it first


class AWSAPIGatewayResponse(TypedDict):
    """
    Represents the response from Lambda to AWS API Gateway.

    For the API gateway, we just have to stringify the body.
    """

    statusCode: int
    body: str  # Response body must be stringified for API gateway


class Period(TypedDict):
    begin: str
    end: str | None


# Typing for ryhti dicts
class RyhtiPlan(TypedDict, total=False):
    planKey: str
    lifeCycleStatus: str
    scale: int
    legalEffectOfLocalMasterPlans: List | None
    geographicalArea: Dict
    periodOfValidity: Period | None
    approvalDate: str | None
    planMaps: List
    planAnnexes: List
    otherPlanMaterials: List
    planReport: Dict | None
    generalRegulationGroups: List[Dict]
    planDescription: str | None
    planObjects: List
    planRegulationGroups: List
    planRegulationGroupRelations: List


class RyhtiPlanDecision(TypedDict, total=False):
    planDecisionKey: str
    name: str
    decisionDate: str
    dateOfDecision: str
    typeOfDecisionMaker: str
    plans: List[RyhtiPlan]


class RyhtiHandlingEvent(TypedDict, total=False):
    handlingEventKey: str
    handlingEventType: str
    eventTime: str
    cancelled: bool


class RyhtiInteractionEvent(TypedDict, total=False):
    interactionEventKey: str
    interactionEventType: str
    eventTime: Period


class RyhtiPlanMatterPhase(TypedDict, total=False):
    planMatterPhaseKey: str
    lifeCycleStatus: str
    geographicalArea: Dict
    handlingEvent: RyhtiHandlingEvent | None
    interactionEvents: List[RyhtiInteractionEvent] | None
    planDecision: RyhtiPlanDecision | None


class RyhtiPlanMatter(TypedDict, total=False):
    permanentPlanIdentifier: str
    planType: str
    name: Dict
    timeOfInitiation: str | None
    description: Dict
    producerPlanIdentifier: str
    caseIdentifiers: List
    recordNumbers: List
    administrativeAreaIdentifiers: List
    digitalOrigin: str
    planMatterPhases: List[RyhtiPlanMatterPhase]


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
        event_type: Action = Action.VALIDATE_PLANS,
        plan_uuid: Optional[str] = None,
        debug_json: Optional[bool] = False,  # save JSON files for debugging
    ) -> None:
        LOGGER.info("Initializing Ryhti client...")
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
        # Cache plans fetched from database
        self.plans: Dict[str, models.Plan] = dict()
        # Cache valid plans after validation, so they can be processed further.
        self.valid_plans: Dict[str, models.Plan] = dict()
        # Cache plan dictionaries
        self.plan_dictionaries: Dict[str, RyhtiPlan] = dict()
        # Cache plan matter dictionaries
        self.plan_matter_dictionaries: Dict[str, RyhtiPlanMatter] = dict()
        # Cache valid plan matters after validation, so they can be processed further.
        self.valid_plan_matters: Dict[str, RyhtiPlanMatter] = dict()

        # We only ever need code uri values, not codes themselves, so let's not bother
        # fetching codes from the database at all. URI is known from class and value.
        # TODO: check that valid status is "13" and approval status is "06" when
        # the lifecycle status code list transitions from DRAFT to VALID.
        #
        # It is exceedingly weird that this, the most important of all codes, is
        # *not* a descriptive string, but a random number that may change, while all
        # the other code lists have descriptive strings that will *not* change.
        self.pending_status_value = "02"
        self.approved_status_value = "06"
        self.valid_status_value = "13"

        # Do some prefetching before starting the run.
        #
        # Do *not* expire on commit, because we want to cache the old data in plan
        # objects throughout the session. If we want up-to date plan data, we will
        # know to explicitly refresh the object from a new session.
        #
        # Otherwise, we may access old plan data without having to create a session
        # and query.
        with self.Session(expire_on_commit=False) as session:
            LOGGER.info("Caching requested plans from database...")
            # Only process specified plans
            plan_query: Query = session.query(models.Plan)
            if plan_uuid:
                LOGGER.info(f"Only fetching plan {plan_uuid}")
                plan_query = plan_query.filter_by(id=plan_uuid)
            self.plans = {plan.id: plan for plan in plan_query.all()}
        if not self.plans:
            LOGGER.info("No plans found in database.")
        else:
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

    def get_plan_matter_api_path(self, plan_type_uri: str) -> str:
        """
        Returns correct plan matter api path depending on the plan type URI.
        """
        api_paths = {
            "1": "RegionalPlanMatter/",
            "2": "LocalMasterPlanMatter/",
            "3": "LocalDetailedPlanMatter/",
        }
        top_level_code = plan_type_uri.split("/")[-1][0]
        return api_paths[top_level_code]

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

    def get_isoformat_value_with_z(self, datetime_value: datetime.datetime) -> str:
        """
        Returns isoformatted datetime in UTC with Z instead of +00:00.
        """
        return datetime_value.isoformat().replace("+00:00", "Z")

    def get_date(self, datetime_value: datetime.datetime) -> str:
        """
        Returns isoformatted date for the given datetime in local timezone.
        """
        return datetime_value.astimezone(LOCAL_TZ).date().isoformat()

    def get_periods(
        self,
        dates_objects: List[models.LifeCycleDate] | List[models.EventDate],
        datetimes: bool = True,
    ) -> List[Period]:
        """
        Returns the time periods of given date objects. Optionally, only dates instead
        of datetimes may be returned.
        """
        return [
            {
                "begin": self.get_isoformat_value_with_z(dates_object.starting_at)
                if datetimes
                else self.get_date(dates_object.starting_at),
                "end": (
                    (
                        self.get_isoformat_value_with_z(dates_object.ending_at)
                        if datetimes
                        else self.get_date(dates_object.ending_at)
                    )
                    if dates_object.ending_at
                    else None
                ),
            }
            for dates_object in dates_objects
        ]

    def get_lifecycle_dates_for_status(
        self, plan_base: base.PlanBase, status_value: str
    ) -> List[models.LifeCycleDate]:
        """
        Returns the plan lifecycle date objects for the desired status.
        """
        return [
            lifecycle_date
            for lifecycle_date in plan_base.lifecycle_dates
            if lifecycle_date.lifecycle_status.value == status_value
        ]

    def get_lifecycle_periods(
        self, plan_base: base.PlanBase, status_value: str, datetimes: bool = True
    ) -> List[Period]:
        """
        Returns the start and end datetimes of lifecycle status for object. Optionally,
        only dates instead of datetimes may be returned.

        Note that for some lifecycle statuses, we may return multiple periods.
        """
        lifecycle_dates = self.get_lifecycle_dates_for_status(plan_base, status_value)
        return self.get_periods(lifecycle_dates, datetimes)

    def get_event_periods(
        self,
        lifecycle_date: models.LifeCycleDate,
        event_class: Type[models.CodeBase],
        event_value: str,
        datetimes: bool = True,
    ) -> List[Period]:
        """
        Returns the start and end datetimes of events with desired class and value
        linked to a lifecycle date object. Optionally, only dates instead of datetimes
        may be returned.

        Note that if the event occurs multiple times, we may return multiple periods.
        """

        def class_and_value_match(event_date: models.EventDate) -> bool:
            return (
                (
                    event_class is NameOfPlanCaseDecision
                    and event_date.decision
                    and event_date.decision.value == event_value
                )
                or (
                    event_class is TypeOfProcessingEvent
                    and event_date.processing_event
                    and event_date.processing_event.value == event_value
                )
                or (
                    event_class is TypeOfInteractionEvent
                    and event_date.interaction_event
                    and event_date.interaction_event.value == event_value
                )
            )

        event_dates = [
            date for date in lifecycle_date.event_dates if class_and_value_match(date)
        ]
        return self.get_periods(event_dates, datetimes)

    def get_last_period(self, periods: List[Period]) -> Optional[Period]:
        """
        Returns the last period in the list, or None if the list is empty.
        """
        return periods[-1] if periods else None

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
        # we should only have one valid period. If there are several, pick last
        recommendation_dict["periodOfValidity"] = self.get_last_period(
            self.get_lifecycle_periods(plan_recommendation, self.valid_status_value)
        )
        recommendation_dict["value"] = plan_recommendation.text_value
        return recommendation_dict

    def get_attribute_value(self, attribute_value: base.AttributeValueMixin) -> Dict:
        value = {"dataType": attribute_value.value_data_type.value}

        def cast_numeric(number: float):
            if attribute_value.value_data_type in (
                AttributeValueDataType.NUMERIC,
                AttributeValueDataType.POSITIVE_NUMERIC,
                AttributeValueDataType.NUMERIC_RANGE,
                AttributeValueDataType.POSITIVE_NUMERIC_RANGE,
                AttributeValueDataType.SPOT_ELEVATION,
            ):
                return int(number)
            else:
                return number

        if attribute_value.value_data_type is AttributeValueDataType.CODE:
            if attribute_value.code_value is not None:
                value["code"] = attribute_value.code_value
            if attribute_value.code_list is not None:
                value["codeList"] = attribute_value.code_list
            if attribute_value.code_title is not None:
                value["title"] = attribute_value.code_title
        elif attribute_value.value_data_type in (
            AttributeValueDataType.NUMERIC,
            AttributeValueDataType.POSITIVE_NUMERIC,
            AttributeValueDataType.DECIMAL,
            AttributeValueDataType.POSITIVE_DECIMAL,
            AttributeValueDataType.SPOT_ELEVATION,
        ):
            if attribute_value.numeric_value is not None:
                value["number"] = cast_numeric(attribute_value.numeric_value)
            if attribute_value.unit:
                value["unitOfMeasure"] = attribute_value.unit
        elif attribute_value.value_data_type in (
            AttributeValueDataType.NUMERIC_RANGE,
            AttributeValueDataType.POSITIVE_NUMERIC_RANGE,
            AttributeValueDataType.DECIMAL_RANGE,
            AttributeValueDataType.POSITIVE_DECIMAL_RANGE,
        ):
            if attribute_value.numeric_range_min is not None:
                value["minimumValue"] = cast_numeric(attribute_value.numeric_range_min)
            if attribute_value.numeric_range_max is not None:
                value["maximumValue"] = cast_numeric(attribute_value.numeric_range_max)
            if attribute_value.unit is not None:
                value["unitOfMeasure"] = attribute_value.unit

        elif attribute_value.value_data_type is AttributeValueDataType.IDENTIFIER:
            pass  # TODO: implement identifier values
        elif attribute_value.value_data_type in (
            AttributeValueDataType.LOCALIZED_TEXT,
            AttributeValueDataType.TEXT,
        ):
            if attribute_value.text_value is not None:
                value["text"] = attribute_value.text_value
            if attribute_value.text_syntax is not None:
                value["syntax"] = attribute_value.text_syntax
        elif attribute_value.value_data_type in (
            AttributeValueDataType.TIME_PERIOD,
            AttributeValueDataType.TIME_PERIOD_DATE_ONLY,
        ):
            pass  # TODO: implement time period and time period date only values

        return value

    def get_additional_information(
        self, additional_information: models.AdditionalInformation
    ) -> Dict:
        additional_information_dict = {
            "type": additional_information.type_of_additional_information.uri
        }
        if additional_information.value_data_type is not None:
            additional_information_dict["value"] = self.get_attribute_value(
                additional_information
            )

        return additional_information_dict

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
        regulation_dict["subjectIdentifiers"] = plan_regulation.subject_identifiers
        regulation_dict["regulationNumber"] = str(plan_regulation.ordering)
        # we should only have one valid period. If there are several, pick last
        regulation_dict["periodOfValidity"] = self.get_last_period(
            self.get_lifecycle_periods(plan_regulation, self.valid_status_value)
        )

        if plan_regulation.types_of_verbal_plan_regulations:
            regulation_dict["verbalRegulations"] = [
                type_code.uri
                for type_code in plan_regulation.types_of_verbal_plan_regulations
            ]

        # Additional informations may contain multiple additional info
        # code values.
        regulation_dict["additionalInformations"] = [
            self.get_additional_information(ai)
            for ai in plan_regulation.additional_information
        ]

        if plan_regulation.value_data_type is not None:
            regulation_dict["value"] = self.get_attribute_value(plan_regulation)

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
        if group.ordering is not None:
            group_dict["groupNumber"] = group.ordering
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
        # we should only have one valid period. If there are several, pick last
        plan_object_dict["periodOfValidity"] = self.get_last_period(
            self.get_lifecycle_periods(plan_object, self.valid_status_value)
        )
        if plan_object.height_min or plan_object.height_max:
            plan_object_dict["verticalLimit"] = {
                "dataType": "DecimalRange",
                # we have to use simplejson because numbers are Decimal
                "minimumValue": plan_object.height_min,
                "maximumValue": plan_object.height_max,
                "unitOfMeasure": plan_object.height_unit,
            }

        # RelatedPlanObjectKeys
        related_plan_object_keys = self._get_related_plan_object_keys(plan_object)
        if related_plan_object_keys:
            plan_object_dict["relatedPlanObjectKeys"] = related_plan_object_keys

        return plan_object_dict

    def _needs_containing_land_use_area(self, plan_object: base.PlanObjectBase) -> bool:
        """
        Returns True if the plan object needs a containing land use area as related plan
        object based on the validation rule
        58 quality/req-spatialplanregulationtype-reference-spatialplanobject.
        """

        return isinstance(plan_object, models.OtherArea) and any(
            regulation.type_of_plan_regulation.value
            in {
                "sitovanTonttijaonMukainenTontti",
                "ohjeellinenrakennusPaikka",
                "rakennusala",
                "rakennuspaikka",
                "rakennusalaJolleSaaSijoittaaTalousrakennuksen",
                "rakennusalaJolleSaaSijoittaaSaunan",
                "korttelialueTaiKorttelialueenOsa",
            }
            for group in plan_object.plan_regulation_groups
            for regulation in cast(models.PlanRegulationGroup, group).plan_regulations
        )

    def _get_containing_land_use_area(
        self, plan_object: base.PlanObjectBase
    ) -> Optional["uuid.UUID"]:
        """
        Returns a land use area id that contains this plan_object.
        If not found, returns None.
        """

        with self.Session(expire_on_commit=False) as session:
            stmt = select(models.LandUseArea.id).where(
                models.LandUseArea.plan_id == plan_object.plan_id,
                models.LandUseArea.geom.ST_Contains(plan_object.geom),
            )
            return session.scalars(stmt).one_or_none()

    def _get_related_plan_object_keys(
        self, plan_object: base.PlanObjectBase
    ) -> List["uuid.UUID"]:
        # TODO: there might be other use cases for related plan objects
        related_plan_object_keys = []

        # Address the validation rule
        # 58: quality/req-spatialplanregulationtype-reference-spatialplanobject
        if self._needs_containing_land_use_area(plan_object):
            containing_land_use_area_id = self._get_containing_land_use_area(
                plan_object
            )
            if containing_land_use_area_id:
                related_plan_object_keys.append(containing_land_use_area_id)

        return related_plan_object_keys

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
            [
                regulation_group.id
                for plan_object in plan_objects
                for regulation_group in plan_object.plan_regulation_groups
            ]
        )
        # Let's fetch all the plan regulation groups for all the objects with a single
        # query. Hoping lazy loading does its trick with all the plan regulations.
        with self.Session(expire_on_commit=False) as session:
            plan_regulation_groups = (
                session.query(models.PlanRegulationGroup)
                .filter(models.PlanRegulationGroup.id.in_(group_ids))
                .order_by(models.PlanRegulationGroup.ordering)
                .all()
            )
            for group in plan_regulation_groups:
                group_dicts.append(self.get_plan_regulation_group(group))
        return group_dicts

    def get_plan_regulation_group_relations(
        self, plan_objects: List[base.PlanObjectBase]
    ) -> List[Dict[str, "uuid.UUID"]]:
        """
        Construct a list of Ryhti compatible plan regulation group relations from plan
        objects in the local database.
        """
        return [
            {
                "planObjectKey": plan_object.id,
                "planRegulationGroupKey": regulation_group.id,
            }
            for plan_object in plan_objects
            for regulation_group in plan_object.plan_regulation_groups
        ]

    def get_plan_dictionary(self, plan: models.Plan) -> RyhtiPlan:
        """
        Construct a dict of single Ryhti compatible plan from plan in the
        local database.
        """
        plan_dictionary = RyhtiPlan()

        # planKey should always be the local uuid, not the permanent plan matter id.
        plan_dictionary["planKey"] = plan.id
        # Let's have all the code values preloaded joined from db.
        # It makes this super easy:
        plan_dictionary["lifeCycleStatus"] = plan.lifecycle_status.uri
        plan_dictionary["legalEffectOfLocalMasterPlans"] = (
            [effect.uri for effect in plan.legal_effects_of_master_plan]
            if plan.legal_effects_of_master_plan
            else None
        )
        plan_dictionary["scale"] = plan.scale
        plan_dictionary["geographicalArea"] = self.get_geojson(plan.geom)
        # For reasons unknown, Ryhti does not allow multilanguage description.
        plan_description = (
            plan.description.get("fin") if isinstance(plan.description, dict) else None
        )
        plan_dictionary["planDescription"] = plan_description

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

        plan_dictionary["generalRegulationGroups"] = [
            self.get_plan_regulation_group(regulation_group, general=True)
            for regulation_group in plan.general_plan_regulation_groups
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

        # we should only have one valid period. If there are several, pick last
        plan_dictionary["periodOfValidity"] = self.get_last_period(
            self.get_lifecycle_periods(plan, self.valid_status_value)
        )
        # we should only have one approved period. If there are several, pick last
        period_of_approval = self.get_last_period(
            self.get_lifecycle_periods(plan, self.approved_status_value)
        )
        plan_dictionary["approvalDate"] = (
            period_of_approval["begin"] if period_of_approval else None
        )

        # Documents are divided into different categories. They may only be added
        # to plan *after* they have been uploaded.
        plan_dictionary["planMaps"] = []
        plan_dictionary["planAnnexes"] = []
        plan_dictionary["otherPlanMaterials"] = []
        plan_dictionary["planReport"] = None

        return plan_dictionary

    def get_plan_dictionaries(self) -> Dict[str, RyhtiPlan]:
        """
        Construct a dict of valid Ryhti compatible plan dictionaries from plans in the
        local database.
        """
        plan_dictionaries = dict()
        for plan_id, plan in self.plans.items():
            plan_dictionaries[plan_id] = self.get_plan_dictionary(plan)
        return plan_dictionaries

    def get_plan_map(self, document: models.Document) -> Dict:
        """
        Construct a dict of single Ryhti compatible plan map.
        """
        plan_map = dict()
        plan_map["planMapKey"] = document.id
        plan_map["name"] = document.name
        plan_map["fileKey"] = document.exported_file_key
        # TODO: Take the coordinate system from the actual file?
        plan_map["coordinateSystem"] = str(base.PROJECT_SRID)
        return plan_map

    def get_plan_attachment_document(self, document: models.Document) -> Dict:
        """
        Construct a dict of single Ryhti compatible plan attachment document.
        """
        attachment_document = dict()
        attachment_document["attachmentDocumentKey"] = document.id
        attachment_document[
            "documentIdentifier"
        ] = document.permanent_document_identifier
        attachment_document["name"] = document.name
        attachment_document["personalDataContent"] = document.personal_data_content.uri
        attachment_document["categoryOfPublicity"] = document.category_of_publicity.uri
        attachment_document["accessibility"] = document.accessibility
        attachment_document["retentionTime"] = document.retention_time.uri
        attachment_document["languages"] = [document.language.uri]
        attachment_document["fileKey"] = document.exported_file_key
        attachment_document["documentDate"] = self.get_date(document.document_date)
        if document.arrival_date:
            attachment_document["arrivedDate"] = self.get_date(document.arrival_date)
        attachment_document["typeOfAttachment"] = document.type_of_document.uri
        return attachment_document

    def get_other_plan_material(self, document: models.Document) -> Dict:
        """
        Construct a dict of single Ryhti compatible other plan material item.
        """
        other_plan_material = dict()
        other_plan_material["otherPlanMaterialKey"] = document.id
        other_plan_material["name"] = document.name
        other_plan_material["fileKey"] = document.exported_file_key
        other_plan_material["personalDataContent"] = document.personal_data_content.uri
        other_plan_material["categoryOfPublicity"] = document.category_of_publicity.uri
        return other_plan_material

    def add_plan_report_to_plan_dict(
        self, document: models.Document, plan_dictionary: RyhtiPlan
    ) -> RyhtiPlan:
        """
        Construct a dict of single Ryhti compatible plan report and add it to the
        provided plan dict. The plan dict may already have existing plan reports.
        """
        if not plan_dictionary["planReport"]:
            plan_dictionary["planReport"] = {
                "planReportKey": str(uuid4()),
                "attachmentDocuments": [self.get_plan_attachment_document(document)],
            }
        else:
            plan_dictionary["planReport"]["attachmentDocuments"].append(
                self.get_plan_attachment_document(document)
            )
        return plan_dictionary

    def add_document_to_plan_dict(
        self, document: models.Document, plan_dictionary: RyhtiPlan
    ) -> RyhtiPlan:
        """
        Construct a dict of single Ryhti compatible plan document and add it to the
        provided plan dict.

        The exact type of the dictionary to be added depends on the document type.
        """
        if document.type_of_document.value == "03":
            # Kaavakartta
            plan_dictionary["planMaps"].append(self.get_plan_map(document))
        elif document.type_of_document.value == "06":
            # Kaavaselostus
            # For some reason, if there are multiple plan reports, they will have to be
            # added inside a single plan report instead of a list of plan reports.
            plan_dictionary = self.add_plan_report_to_plan_dict(
                document, plan_dictionary
            )
        elif document.type_of_document.value == "99":
            # Muu asiakirja
            plan_dictionary["otherPlanMaterials"].append(
                self.get_other_plan_material(document)
            )
        else:
            # Kaavan liite
            plan_dictionary["planAnnexes"].append(
                self.get_plan_attachment_document(document)
            )
        return plan_dictionary

    def get_plan_decisions(self, plan: models.Plan) -> List[RyhtiPlanDecision]:
        """
        Construct a list of Ryhti compatible plan decisions from plan in the local
        database.
        """
        decisions: List[RyhtiPlanDecision] = []
        # Decision name must correspond to the phase the plan is in. This requires
        # mapping from lifecycle statuses to decision names.
        print(decisions_by_status.get(plan.lifecycle_status.value, []))
        for decision_value in decisions_by_status.get(plan.lifecycle_status.value, []):
            entry = RyhtiPlanDecision()
            # TODO: Let's just have random uuid for now, on the assumption that each
            # phase is only POSTed to ryhti once. If planners need to post and repost
            # the same phase, script needs logic to check if the phase exists in Ryhti
            # already before reposting.
            entry["planDecisionKey"] = str(uuid4())
            entry["name"] = get_code_uri(NameOfPlanCaseDecision, decision_value)
            entry["typeOfDecisionMaker"] = get_code_uri(
                TypeOfDecisionMaker,
                decisionmaker_by_status[plan.lifecycle_status.value],
            )
            # Plan must be embedded in decision when POSTing!
            entry["plans"] = [self.plan_dictionaries[plan.id]]

            try:
                lifecycle_date = self.get_lifecycle_dates_for_status(
                    plan, plan.lifecycle_status.value
                )[-1]
            except IndexError:
                # If we have an old plan with no phase data, we cannot add decisions.
                LOGGER.warning(
                    "Error in plan! Current lifecycle status is missing start date."
                )
                continue
            # Decision date will be
            # 1) decision date if found in database or, if not found,
            # 2) start of the current status period is used as backup.
            # TODO: Remove 2) once QGIS makes sure all necessary dates are filled in
            # manually (or automatically).
            period_of_decision = self.get_last_period(
                self.get_event_periods(
                    lifecycle_date,
                    NameOfPlanCaseDecision,
                    decision_value,
                    datetimes=False,
                )
            )
            period_of_current_status = self.get_periods(
                [lifecycle_date], datetimes=False
            )[-1]
            # Decision has no duration:
            entry["decisionDate"] = (
                period_of_decision["begin"]
                if period_of_decision
                else period_of_current_status["begin"]
            )
            entry["dateOfDecision"] = entry["decisionDate"]

            decisions.append(entry)
        return decisions

    def get_plan_handling_events(self, plan: models.Plan) -> List[RyhtiHandlingEvent]:
        """
        Construct a list of Ryhti compatible plan handling events from plan in the local
        database.
        """
        events: List[RyhtiHandlingEvent] = []
        # Decision name must correspond to the phase the plan is in. This requires
        # mapping from lifecycle statuses to decision names.
        for event_value in processing_events_by_status.get(
            plan.lifecycle_status.value, []
        ):
            entry = RyhtiHandlingEvent()
            # TODO: Let's just have random uuid for now, on the assumption that each
            # phase is only POSTed to ryhti once. If planners need to post and repost
            # the same phase, script needs logic to check if the phase exists in Ryhti
            # already before reposting.
            entry["handlingEventKey"] = str(uuid4())
            entry["handlingEventType"] = get_code_uri(
                TypeOfProcessingEvent, event_value
            )

            try:
                lifecycle_date = self.get_lifecycle_dates_for_status(
                    plan, plan.lifecycle_status.value
                )[-1]
            except IndexError:
                # If we have an old plan with no phase data, we cannot add any events.
                LOGGER.warning(
                    "Error in plan! Current lifecycle status is missing start date."
                )
                continue
            # Handling event date will be
            # 1) handling event date if found in database or, if not found,
            # 2) start of the current status period is used as backup.
            # TODO: Remove 2) once QGIS makes sure all necessary dates are filled in
            # manually (or automatically).
            period_of_handling_event = self.get_last_period(
                self.get_event_periods(
                    lifecycle_date,
                    TypeOfProcessingEvent,
                    event_value,
                    datetimes=False,
                )
            )
            period_of_current_status = self.get_periods(
                [lifecycle_date], datetimes=False
            )[-1]
            # Handling event has no duration:
            entry["eventTime"] = (
                period_of_handling_event["begin"]
                if period_of_handling_event
                else period_of_current_status["begin"]
            )
            entry["cancelled"] = False

            events.append(entry)
        return events

    def get_interaction_events(self, plan: models.Plan) -> List[RyhtiInteractionEvent]:
        """
        Construct a list of Ryhti compatible interaction events from plan in the local
        database.
        """
        events: List[RyhtiInteractionEvent] = []
        # Decision name must correspond to the phase the plan is in. This requires
        # mapping from lifecycle statuses to decision names.
        for event_value in interaction_events_by_status.get(
            plan.lifecycle_status.value, []
        ):
            entry = RyhtiInteractionEvent()
            # TODO: Let's just have random uuid for now, on the assumption that each
            # phase is only POSTed to ryhti once. If planners need to post and repost
            # the same phase, script needs logic to check if the phase exists in Ryhti
            # already before reposting.
            entry["interactionEventKey"] = str(uuid4())
            entry["interactionEventType"] = get_code_uri(
                TypeOfInteractionEvent, event_value
            )

            try:
                lifecycle_date = self.get_lifecycle_dates_for_status(
                    plan, plan.lifecycle_status.value
                )[-1]
            except IndexError:
                # If we have an old plan with no phase data, we cannot add any events.
                LOGGER.warning(
                    "Error in plan! Current lifecycle status is missing start date."
                )
                continue
            # Interaction event period will be
            # 1) interaction event period if found in database or, if not found,
            # 2) 30 days at start of the current status period (nähtävilläoloaika) are
            # used as backup.
            # TODO: Remove 2) once QGIS makes sure all necessary dates are filled in
            # manually (or automatically).
            period_of_interaction_event = self.get_last_period(
                self.get_event_periods(
                    lifecycle_date, TypeOfInteractionEvent, event_value
                )
            )
            period_of_current_status = self.get_periods([lifecycle_date])[-1]
            entry["eventTime"] = (
                period_of_interaction_event
                if period_of_interaction_event
                else {
                    "begin": (period_of_current_status["begin"]),
                    "end": (
                        datetime.datetime.fromisoformat(
                            period_of_current_status["begin"]
                        )
                        + datetime.timedelta(days=30)
                    )
                    .isoformat()
                    .replace("+00:00", "Z"),
                }
            )

            events.append(entry)
        return events

    def get_plan_matter_phases(self, plan: models.Plan) -> List[RyhtiPlanMatterPhase]:
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
        phase = RyhtiPlanMatterPhase()
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
        phase["handlingEvent"] = handling_events[0] if handling_events else None
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

    def get_plan_matter(self, plan: models.Plan) -> RyhtiPlanMatter:
        """
        Construct a dict of single Ryhti compatible plan matter from plan in the local
        database.
        """
        plan_matter = RyhtiPlanMatter()
        plan_matter["permanentPlanIdentifier"] = plan.permanent_plan_identifier
        # Plan type has to be proper URI (not just value) here, *unlike* when only
        # validating plan. Go figure.
        plan_matter["planType"] = plan.plan_type.uri
        # For reasons unknown, name is needed for plan matter but not for plan. Plan
        # only contains description, and only in one language.
        plan_matter["name"] = plan.name

        # we should only have one pending period. If there are several, pick last
        dates_of_initiation = self.get_last_period(
            self.get_lifecycle_periods(plan, self.pending_status_value, datetimes=False)
        )
        plan_matter["timeOfInitiation"] = (
            dates_of_initiation["begin"] if dates_of_initiation else None
        )
        # Hooray, unlike plan, the plan *matter* description allows multilanguage data!
        plan_matter["description"] = plan.description
        plan_matter["producerPlanIdentifier"] = plan.producers_plan_identifier
        plan_matter["caseIdentifiers"] = (
            [plan.matter_management_identifier]
            if plan.matter_management_identifier
            else []
        )
        plan_matter["recordNumbers"] = (
            [plan.record_number] if plan.record_number else []
        )
        # Apparently Ryhti plans may cover multiple administrative areas, so the region
        # identifier has to be embedded in a list.
        plan_matter["administrativeAreaIdentifiers"] = [
            plan.organisation.municipality.value
            if plan.organisation.municipality
            else plan.organisation.administrative_region.value
        ]
        # We have no need of importing the digital origin code list as long as we are
        # not digitizing old plans:
        plan_matter[
            "digitalOrigin"
        ] = "http://uri.suomi.fi/codelist/rytj/RY_DigitaalinenAlkupera/code/01"
        # TODO: kaava-asian liitteet
        # are these different from plan annexes? why? how??
        # plan_matter["matterAnnexes"] = self.get_plan_matter_annexes(plan)
        # TODO: lähdeaineistot
        # plan_matter["sourceDatas"] = self.get_source_datas(plan)
        plan_matter["planMatterPhases"] = self.get_plan_matter_phases(plan)
        return plan_matter

    def get_plan_matters(self) -> Dict[str, RyhtiPlanMatter]:
        """
        Construct a dict of valid Ryhti compatible plan matters from valid plans in the
        local database.
        """
        plan_matters = dict()
        for plan in self.valid_plans.values():
            plan_matters[plan.id] = self.get_plan_matter(plan)
        return plan_matters

    def validate_plans(self) -> Dict[str, RyhtiResponse]:
        """
        Validates all plans serialized in client plan dictionaries.
        """
        plan_validation_endpoint = f"{self.public_api_base}/Plan/validate"
        responses: Dict[str, RyhtiResponse] = dict()
        for plan_id, plan_dict in self.plan_dictionaries.items():
            LOGGER.info(f"Validating JSON for plan {plan_id}...")

            # Some plan fields may only be present in plan matter, not in the plan
            # dictionary. In the context of plan validation, they must be provided as
            # query parameters.
            plan = self.plans[plan_id]
            plan_type_parameter = plan.plan_type.value
            # We only support one area id, no need for commas and concat:
            admin_area_id_parameter = (
                plan.organisation.municipality.value
                if plan.organisation.municipality
                else plan.organisation.administrative_region.value
            )
            if self.debug_json:
                with open(f"ryhti_debug/{plan_id}.json", "w") as plan_file:
                    json.dump(plan_dict, plan_file)
            LOGGER.info(f"POSTing JSON: {json.dumps(plan_dict)}")

            # requests apparently uses simplejson automatically if it is installed!
            # A bit too much magic for my taste, but seems to work.
            response = requests.post(
                plan_validation_endpoint,
                json=plan_dict,
                headers=self.public_headers,
                params={
                    "planType": plan_type_parameter,
                    "administrativeAreaIdentifiers": admin_area_id_parameter,
                },
            )
            LOGGER.info(f"Got response {response}")
            if response.status_code == 200:
                # Successful validation does not return any json!
                responses[plan_id] = {
                    "status": 200,
                    "errors": None,
                    "detail": None,
                    "warnings": None,
                }
            else:
                try:
                    # Validation errors always contain JSON
                    responses[plan_id] = response.json()
                except json.JSONDecodeError:
                    # There is something wrong with the API
                    response.raise_for_status()
            if self.debug_json:
                with open(f"ryhti_debug/{plan_id}.response.json", "w") as response_file:
                    json.dump(responses[plan_id], response_file)
            LOGGER.info(responses[plan_id])
        return responses

    def upload_plan_documents(self) -> Dict[str, List[RyhtiResponse]]:
        """
        Upload any changed plan documents. If document has not been modified
        since it was last uploaded, do nothing.
        """
        responses: Dict[str, List[RyhtiResponse]] = dict()
        file_endpoint = self.xroad_server_address + self.xroad_api_path + "File"
        upload_headers = self.xroad_headers.copy()
        # We must *not* provide Content-Type header:
        # https://blog.jetbridge.com/multipart-encoded-python-requests/
        del upload_headers["Content-Type"]
        for plan in self.valid_plans.values():
            responses[plan.id] = []
            municipality = (
                plan.organisation.municipality.value
                if plan.organisation.municipality
                else None
            )
            region = plan.organisation.administrative_region.value
            for document in plan.documents:
                if document.url:
                    # No need to upload if document hasn't changed
                    headers = requests.head(document.url).headers
                    print(headers)
                    etag = headers.get("ETag")
                    last_modified = headers.get("Last-Modified")
                    if (
                        document.exported_file_etag
                        and document.exported_file_etag == etag
                    ) or (
                        document.exported_at
                        and last_modified
                        and document.exported_at
                        > email.utils.parsedate_to_datetime(last_modified)
                    ):
                        LOGGER.info("File unchanged since last upload.")
                        responses[plan.id].append(
                            RyhtiResponse(
                                status=None,
                                detail="File unchanged since last upload.",
                                errors=None,
                                warnings=None,
                            )
                        )
                        continue
                    # Let's try streaming the file instead of downloading
                    # and then uploading:
                    file_request = requests.get(document.url, stream=True)
                    if file_request.status_code == 200:
                        file_request.raw.decode_content = True
                        file_name = document.url.split("/")[-1]
                        file_type = file_request.headers["Content-Type"]
                        # Stream file instead of reading it to memory
                        encoded_data = MultipartEncoder(
                            fields={
                                "file": (file_name, file_request.raw, file_type),
                            }
                        )
                        upload_headers["Content-Type"] = encoded_data.content_type
                        # TODO: get coordinate system from file. Maybe not easy
                        # if just streaming it thru.
                        post_parameters = (
                            {"municipalityId": municipality}
                            if municipality
                            else {"regionId": region}
                        )
                        post_response = requests.post(
                            file_endpoint,
                            data=encoded_data,
                            params=post_parameters,
                            headers=upload_headers,
                        )
                        if post_response.status_code == 201:
                            LOGGER.info(f"Posted file {post_response.json()}")
                            responses[plan.id].append(
                                RyhtiResponse(
                                    status=201,
                                    detail=post_response.json(),
                                    errors=None,
                                    warnings=None,
                                )
                            )
                        else:
                            LOGGER.warning(f"Could not upload file {file_name}!")
                            LOGGER.warning(post_response.json())
                            responses[plan.id].append(
                                RyhtiResponse(
                                    status=post_response.status_code,
                                    detail=f"Could not upload file {file_name}!",
                                    errors=post_response.json(),
                                    warnings=None,
                                )
                            )
                    else:
                        LOGGER.warning("Could not fetch file! Please check file URL.")
                        responses[plan.id].append(
                            RyhtiResponse(
                                status=None,
                                detail="Could not fetch file! Please check file URL.",
                                errors=None,
                                warnings=None,
                            )
                        )
        return responses

    def get_permanent_plan_identifiers(self) -> Dict[str, RyhtiResponse]:
        """
        Get permanent plan identifiers for all plans that are marked
        valid but do not have identifiers set yet.
        """
        responses: Dict[str, RyhtiResponse] = dict()
        for plan in self.valid_plans.values():
            if not plan.permanent_plan_identifier:
                plan_identifier_endpoint = (
                    self.xroad_server_address
                    + self.xroad_api_path
                    + self.get_plan_matter_api_path(plan.plan_type.uri)
                    + "permanentPlanIdentifier"
                )
                LOGGER.info(f"Getting permanent identifier for plan {plan.id}...")
                administrative_area_identifier = (
                    plan.organisation.municipality.value
                    if plan.organisation.municipality
                    else plan.organisation.administrative_region.value
                )
                data = {
                    "administrativeAreaIdentifier": administrative_area_identifier,
                    "projectName": plan.producers_plan_identifier,
                }
                LOGGER.info("Request headers")
                LOGGER.info(self.xroad_headers)
                LOGGER.info("Request URL")
                LOGGER.info(plan_identifier_endpoint)
                LOGGER.info("Request data")
                LOGGER.info(data)
                response = requests.post(
                    plan_identifier_endpoint, json=data, headers=self.xroad_headers
                )
                LOGGER.info("Plan identifier response:")
                LOGGER.info(response.status_code)
                LOGGER.info(response.headers)
                LOGGER.info(response.text)
                if response.status_code == 401:
                    LOGGER.info(
                        "No permission to get plan identifier in this region or municipality!"  # noqa
                    )
                    responses[plan.id] = {
                        "status": 401,
                        "errors": response.json(),
                        "detail": None,
                        "warnings": None,
                    }
                elif response.status_code == 400:
                    LOGGER.info(
                        "Could not get identifier! Most likely producers_plan_identifier is missing."  # noqa
                    )
                    responses[plan.id] = {
                        "status": 400,
                        "errors": response.json(),
                        "detail": None,
                        "warnings": None,
                    }
                else:
                    response.raise_for_status()
                    LOGGER.info(f"Received identifier {response.json()}")
                    responses[plan.id] = {
                        "status": 200,
                        "detail": response.json(),
                        "errors": None,
                        "warnings": None,
                    }
                if self.debug_json:
                    with open(
                        f"ryhti_debug/{plan.id}.identifier.response.json", "w"
                    ) as response_file:
                        response_file.write(str(plan_identifier_endpoint) + "\n")
                        response_file.write(str(self.xroad_headers) + "\n")
                        response_file.write(str(data) + "\n")
                        json.dump(str(responses[plan.id]), response_file)
        return responses

    def validate_plan_matters(self) -> Dict[str, RyhtiResponse]:
        """
        Validates all plan matters serialized in client plan matter dictionaries.
        """
        responses: Dict[str, RyhtiResponse] = dict()
        for plan_id, plan_matter in self.plan_matter_dictionaries.items():
            permanent_id = plan_matter["permanentPlanIdentifier"]
            plan_matter_validation_endpoint = (
                self.xroad_server_address
                + self.xroad_api_path
                + self.get_plan_matter_api_path(plan_matter["planType"])
                + f"{permanent_id}/validate"
            )
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
            LOGGER.info(response.text)
            if response.status_code == 200:
                # Successful validation might return warnings
                responses[plan_id] = {
                    "status": 200,
                    "errors": None,
                    "detail": None,
                    "warnings": response.json()["warnings"],
                }
            else:
                try:
                    # Validation errors always contain JSON
                    responses[plan_id] = response.json()
                except json.JSONDecodeError:
                    # There is something wrong with the API
                    response.raise_for_status()
            if self.debug_json:
                with open(
                    f"ryhti_debug/{permanent_id}.response.json", "w"
                ) as response_file:
                    json.dump(responses[plan_id], response_file)
            LOGGER.info(responses[plan_id])
        return responses

    def create_new_resource(
        self, endpoint: str, resource_dict: RyhtiPlanMatter | RyhtiPlanMatterPhase
    ) -> RyhtiResponse:
        """
        POST new resource to Ryhti API.
        """
        response = requests.post(
            endpoint,
            json=resource_dict,
            headers=self.xroad_headers,
        )
        LOGGER.info(f"Got response {response}")
        LOGGER.info(response.text)
        if response.status_code == 201:
            # POST successful! The API may give warnings when saving.
            ryhti_response = {
                "status": 201,
                "errors": None,
                "warnings": response.json()["warnings"],
                "detail": None,
            }
        else:
            try:
                # API errors always contain JSON
                ryhti_response = response.json()
            except json.JSONDecodeError:
                # There is something wrong with the API
                response.raise_for_status()
        return cast(RyhtiResponse, ryhti_response)

    def update_resource(
        self, endpoint: str, resource_dict: RyhtiPlanMatter | RyhtiPlanMatterPhase
    ) -> RyhtiResponse:
        """
        PUT resource to Ryhti API.
        """
        response = requests.put(
            endpoint,
            json=resource_dict,
            headers=self.xroad_headers,
        )
        LOGGER.info(f"Got response {response}")
        LOGGER.info(response.text)
        if response.status_code == 200:
            # PUT successful! The API may give warnings when saving.
            ryhti_response = {
                "status": 200,
                "errors": None,
                "warnings": response.json()["warnings"],
                "detail": None,
            }
        else:
            try:
                # API errors always contain JSON
                ryhti_response = response.json()
            except json.JSONDecodeError:
                # There is something wrong with the API
                response.raise_for_status()
        return cast(RyhtiResponse, ryhti_response)

    def post_plan_matters(self) -> Dict[str, RyhtiResponse]:
        """
        POST all marked and valid plan matter data in the client to Ryhti.

        This means either creating a new plan matter, updating the plan matter,
        creating a new plan matter phase, or updating the plan matter phase.
        """
        responses: Dict[str, RyhtiResponse] = dict()
        for plan_id, plan_matter in self.valid_plan_matters.items():
            # 0) Check if plan is marked to be exported
            if not self.plans[plan_id].to_be_exported:
                continue

            permanent_id = plan_matter["permanentPlanIdentifier"]
            plan_matter_endpoint = (
                self.xroad_server_address
                + self.xroad_api_path
                + self.get_plan_matter_api_path(plan_matter["planType"])
                + permanent_id
            )
            print(plan_matter_endpoint)

            # 1) Check or create plan matter with the identifier
            LOGGER.info(f"Checking if plan matter for plan {permanent_id} exists...")
            get_response = requests.get(
                plan_matter_endpoint, headers=self.xroad_headers
            )
            if get_response.status_code == 404:
                LOGGER.info(f"Plan matter {permanent_id} not found! Creating...")
                responses[plan_id] = self.create_new_resource(
                    plan_matter_endpoint, plan_matter
                )
                if self.debug_json:
                    with open(
                        f"ryhti_debug/{permanent_id}.plan_matter_post_response.json",
                        "w",
                    ) as response_file:
                        json.dump(responses[plan_id], response_file)
                LOGGER.info(responses[plan_id])
                continue
            # 2) If plan matter existed, check or create plan matter phase instead
            elif get_response.status_code == 200:
                LOGGER.info(
                    f"Plan matter {permanent_id} found! "
                    "Checking if plan matter phase exits..."
                )
                phases: List[RyhtiPlanMatterPhase] = get_response.json()[
                    "planMatterPhases"
                ]
                local_phase = plan_matter["planMatterPhases"][0]
                local_lifecycle_status = local_phase["lifeCycleStatus"]
                print(phases)
                print(local_phase)
                try:
                    current_phase = [
                        phase
                        for phase in phases
                        if phase["lifeCycleStatus"] == local_lifecycle_status
                    ][0]
                except IndexError:
                    LOGGER.info(
                        f"Phase {local_lifecycle_status} not found! Creating..."
                    )
                    # Create new phase with locally generated id:
                    plan_matter_phase_endpoint = (
                        plan_matter_endpoint
                        + "/phase/"
                        + local_phase["planMatterPhaseKey"]
                    )
                    print(plan_matter_phase_endpoint)
                    responses[plan_id] = self.create_new_resource(
                        plan_matter_phase_endpoint, local_phase
                    )
                    if self.debug_json:
                        with open(
                            "ryhti_debug/"
                            + permanent_id
                            + ".plan_matter_phase_post_response.json",
                            "w",
                        ) as response_file:
                            json.dump(responses[plan_id], response_file)
                    LOGGER.info(responses[plan_id])
                    continue
                # 3) If plan matter phase existed, update plan matter phase instead
                LOGGER.info(
                    f"Plan matter phase {local_lifecycle_status} found! "
                    "Updating phase..."
                )
                # Use existing phase id:
                plan_matter_phase_endpoint = (
                    plan_matter_endpoint
                    + "/phase/"
                    + current_phase["planMatterPhaseKey"]
                )
                responses[plan_id] = self.update_resource(
                    plan_matter_phase_endpoint, local_phase
                )
                if self.debug_json:
                    with open(
                        "ryhti_debug/"
                        + permanent_id
                        + ".plan_matter_phase_put_response.json",
                        "w",
                    ) as response_file:
                        json.dump(responses[plan_id], response_file)
                LOGGER.info(responses[plan_id])
            else:
                try:
                    # API errors always contain JSON
                    responses[plan_id] = get_response.json()
                    LOGGER.info(responses[plan_id])
                except json.JSONDecodeError:
                    # There is something wrong with the API
                    get_response.raise_for_status()
        return responses

    def save_plan_validation_responses(
        self, responses: Dict[str, RyhtiResponse]
    ) -> Response:
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
        with self.Session(expire_on_commit=False) as session:
            for plan_id, response in responses.items():
                # TODO: do we have to fetch plan from db again? Can we use valid_plans
                # dict?
                plan = session.get(models.Plan, plan_id)
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
                    LOGGER.info(details[plan_id])
                    LOGGER.info(f"Ryhti response: {json.dumps(response)}")
                    continue
                elif response["status"] == 200:
                    details[plan_id] = f"Validation successful for {plan_id}!"
                    plan.validation_errors = (
                        "Kaava on validi. Kaava-asiaa ei ole vielä validoitu."
                    )
                    self.valid_plans[plan_id] = plan
                else:
                    details[plan_id] = f"Validation FAILED for {plan_id}."
                    plan.validation_errors = response["errors"]

                LOGGER.info(details[plan_id])
                LOGGER.info(f"Ryhti response: {json.dumps(response)}")
                plan.validated_at = datetime.datetime.now(tz=LOCAL_TZ)
            session.commit()
        return Response(
            statusCode=200,
            body=ResponseBody(
                title="Plan validations run.",
                details=details,
                ryhti_responses=responses,
            ),
        )

    def set_plan_documents(self, responses: Dict[str, List[RyhtiResponse]]):
        """
        Save uploaded plan document keys and export times to the database. Also,
        append document data to the plan dictionaries.
        """
        with self.Session(expire_on_commit=False) as session:
            for plan_id, response in responses.items():
                # Make sure that the plan in the valid plans dict stays up to date
                plan = self.valid_plans[plan_id]
                session.add(plan)
                for document, document_response in zip(
                    plan.documents, response, strict=True
                ):
                    session.add(document)
                    if document_response["status"] == 201:
                        document.exported_file_key = document_response["detail"]
                        document.exported_at = datetime.datetime.now(tz=LOCAL_TZ)
                    # We can only serialize the document after it has been uploaded
                    self.add_document_to_plan_dict(
                        document, self.plan_dictionaries[plan_id]
                    )
                session.commit()

    def set_permanent_plan_identifiers(self, responses: Dict[str, RyhtiResponse]):
        """
        Save permanent plan identifiers returned by RYHTI API to the database.
        """
        with self.Session(expire_on_commit=False) as session:
            for plan_id, response in responses.items():
                # Make sure that the plan in the valid plans dict stays up to date
                plan = self.valid_plans[plan_id]
                session.add(plan)
                if response["status"] == 200:
                    plan.permanent_plan_identifier = response["detail"]
                    plan.validation_errors = (
                        "Kaava on validi. Pysyvä kaavatunnus tallennettu. Kaava-"
                        "asiaa ei ole vielä validoitu."
                    )
                elif response["status"] == 401:
                    plan.validation_errors = (
                        "Kaava on validi, mutta sinulla ei ole oikeuksia luoda "
                        "kaavaa tälle alueelle."
                    )
            session.commit()

    def save_plan_matter_validation_responses(
        self, responses: Dict[str, RyhtiResponse]
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
        with self.Session(expire_on_commit=False) as session:
            for plan_id, response in responses.items():
                plan: Optional[models.Plan] = session.get(models.Plan, plan_id)
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
                    LOGGER.info(details[plan_id])
                    LOGGER.info(f"Ryhti response: {json.dumps(response)}")
                    continue
                elif response["status"] == 200:
                    details[
                        plan_id
                    ] = f"Plan matter validation successful for {plan_id}!"
                    plan.validation_errors = (
                        "Kaava-asia on validi ja sen voi viedä Ryhtiin."
                    )
                    self.valid_plan_matters[plan_id] = self.plan_matter_dictionaries[
                        plan_id
                    ]
                else:
                    details[plan_id] = f"Plan matter validation FAILED for {plan_id}."
                    plan.validation_errors = response["errors"]

                LOGGER.info(details[plan_id])
                LOGGER.info(f"Ryhti response: {json.dumps(response)}")
                plan.validated_at = datetime.datetime.now(tz=LOCAL_TZ)
            session.commit()
        return Response(
            statusCode=200,
            body=ResponseBody(
                title="Plan and plan matter validations run.",
                details=details,
                ryhti_responses=responses,
            ),
        )

    def save_plan_matter_post_responses(
        self, responses: Dict[str, RyhtiResponse]
    ) -> Response:
        """
        Save X-Road API POST response data to the database and return lambda response.

        If POST is successful, update exported_at field.

        If POST is unsuccessful, save the error JSON in plan
        validation_errors json field (in addition to saving it to AWS logs and
        returning them in lambda return value).

        If Ryhti request fails unexpectedly, save the returned error.
        """
        details: Dict[str, str] = {}
        with self.Session(expire_on_commit=False) as session:
            for plan_id, response in responses.items():
                plan: Optional[models.Plan] = session.get(models.Plan, plan_id)
                if not plan:
                    # Plan has been deleted in the middle of POST. Nothing
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
                    ] = f"Plan matter phase PUT successful for {plan_id}!"
                    plan.validation_errors = "Kaava-asian vaihe on päivitetty Ryhtiin."
                    plan.exported_at = datetime.datetime.now(tz=LOCAL_TZ)
                    plan.to_be_exported = False
                elif response["status"] == 201:
                    details[plan_id] = (
                        "Plan matter or plan matter phase POST successful for "
                        + plan_id
                        + "!"
                    )
                    plan.validation_errors = "Uusi kaava-asian vaihe on viety Ryhtiin."
                    plan.exported_at = datetime.datetime.now(tz=LOCAL_TZ)
                    plan.to_be_exported = False
                else:
                    details[plan_id] = f"Plan matter POST FAILED for {plan_id}."
                    plan.validation_errors = response["errors"]

                LOGGER.info(details[plan_id])
                LOGGER.info(f"Ryhti response: {json.dumps(response)}")
            session.commit()
        return Response(
            statusCode=200,
            body=ResponseBody(
                title=(
                    "Plan and plan matter validations run. "
                    "Valid marked plan matters POSTed."
                ),
                details=details,
                ryhti_responses=responses,
            ),
        )


def responsify(
    response: Response, using_api_gateway: bool = False
) -> Response | AWSAPIGatewayResponse:
    """
    Convert response to API gateway response if the request arrived through API gateway.
    If we want to provide status code to API gateway, the JSON body must be string.
    """
    return (
        AWSAPIGatewayResponse(
            statusCode=response["statusCode"], body=json.dumps(response["body"])
        )
        if using_api_gateway
        else response
    )


def handler(
    payload: Event | AWSAPIGatewayPayload, _
) -> Response | AWSAPIGatewayResponse:
    """
    Handler which is called when accessing the endpoint. We must handle both API
    gateway HTTP requests and regular lambda requests. API gateway requires
    the response body to be stringified.

    If lambda runs successfully, we always return 200 OK. In case a python
    exception occurs, AWS lambda will return the exception.

    We want to return general result message of the lambda run, as well as all the
    Ryhti API results and errors, separated by plan id.
    """
    LOGGER.info(f"Received {payload}...")

    using_api_gateway = False
    # The payload may contain only the event dict *or* all possible data coming from an
    # API Gateway HTTP request. We kinda have to infer which one is the case here.
    try:
        # API Gateway request. The JSON body has to be converted to python object.
        event = cast(Event, json.loads(cast(AWSAPIGatewayPayload, payload)["body"]))
        using_api_gateway = True
    except KeyError:
        # Direct lambda request
        event = cast(Event, payload)

    try:
        event_type = Action(event["action"])
    except KeyError:
        event_type = Action.VALIDATE_PLANS
    except ValueError:
        response_title = "Unknown action."
        LOGGER.info(response_title)
        return responsify(
            Response(
                statusCode=400,
                body=ResponseBody(
                    title=response_title,
                    details={event["action"]: "Unknown action."},
                    ryhti_responses={},
                ),
            ),
            using_api_gateway,
        )
    debug_json = event.get("save_json", False)
    plan_uuid = event.get("plan_uuid", None)
    if event_type is Action.POST_PLANS and (
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
        if event_type is Action.GET_PLANS:
            # just return the JSON to the user
            response_title = "Returning serialized plans from database."
            LOGGER.info(response_title)
            return responsify(
                Response(
                    statusCode=200,
                    body=ResponseBody(
                        title=response_title,
                        details=cast(dict, client.plan_dictionaries),
                        ryhti_responses={},
                    ),
                ),
                using_api_gateway,
            )

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

            # Documents are exported separately from plan matter. Also, they need to be
            # present in Ryhti *before* plan matter is created.
            #
            # Therefore, let's export all the documents right away, and update them to
            # the latest version when needed. Otherwise, the plan matter would never be
            # valid. Only upload documents for those plans that are valid.
            # 4) If changed documents exist, upload documents
            LOGGER.info("Checking and updating plan documents for valid plans...")
            plan_documents = client.upload_plan_documents()

            LOGGER.info("Marking documents exported...")
            client.set_plan_documents(plan_documents)

            # Only get identifiers for those plans that are valid.
            # 5) Check or create permanent plan identifier for valid plans, from X-Road
            # API
            LOGGER.info("Getting permanent plan identifiers for valid plans...")
            plan_identifiers = client.get_permanent_plan_identifiers()

            LOGGER.info("Setting permanent plan identifiers for valid plans...")
            client.set_permanent_plan_identifiers(plan_identifiers)

            # 6) Validate plan matters with identifiers with X-Road API
            LOGGER.info("Formatting plan matter data for valid plans...")
            client.plan_matter_dictionaries = client.get_plan_matters()

            LOGGER.info("Validating plan matters for valid plans...")
            responses = client.validate_plan_matters()

            # 7) Save plan matter validation data
            LOGGER.info("Saving plan matter validation data for valid plans...")
            # Merge details and ryhti_responses for valid and invalid plans. Invalid
            # plans will have plan validation responses, valid plans will have plan
            # matter validation responses.
            plan_matter_validation_response = (
                client.save_plan_matter_validation_responses(responses)
            )
            lambda_response["body"]["title"] = plan_matter_validation_response["body"][
                "title"
            ]
            lambda_response["body"]["details"] |= plan_matter_validation_response[
                "body"
            ]["details"]
            lambda_response["body"][
                "ryhti_responses"
            ] |= plan_matter_validation_response["body"]["ryhti_responses"]
            if event_type is Action.POST_PLANS:
                # 8) Update Ryhti plan matters
                LOGGER.info("POSTing marked and valid plan matters:")
                responses = client.post_plan_matters()

                # 9) Save plan matter update responses
                LOGGER.info("Saving plan matter POST data for posted plans...")
                # Merge details and ryhti_responses for valid and invalid plan matters.
                # Invalid plans will have plan validation responses, invalid plan
                # matters will have plan matter validation responses, and valid plan
                # matters will have plan POST responses.
                plan_matter_post_response = client.save_plan_matter_post_responses(
                    responses
                )
                lambda_response["body"]["title"] = plan_matter_post_response["body"][
                    "title"
                ]
                lambda_response["body"]["details"] |= plan_matter_post_response["body"][
                    "details"
                ]
                lambda_response["body"]["ryhti_responses"] |= plan_matter_post_response[
                    "body"
                ]["ryhti_responses"]
        else:
            LOGGER.info(
                "Local XROAD_SERVER_ADDRESS, your organization XROAD_MEMBER_CODE, your "
                "XROAD_SYKE_CLIENT_ID or your XROAD_SYKE_CLIENT_SECRET "
                "not set. Cannot fetch permanent id or validate or post plan matters."
            )
    else:
        lambda_response = Response(
            statusCode=200,
            body=ResponseBody(
                title="Plans not found in database, exiting.",
                details={},
                ryhti_responses={},
            ),
        )

    LOGGER.info(lambda_response["body"]["title"])
    return responsify(lambda_response, using_api_gateway)
