import enum
import logging
import os
from typing import TYPE_CHECKING, Dict, Literal, Optional, TypedDict, cast
from uuid import UUID

import boto3
import simplejson as json

from database.db_helper import DatabaseHelper, User
from ryhti_client.ryhti_client import RyhtiClient

if TYPE_CHECKING:
    from ryhti_client.ryhti_client import RyhtiResponse

# All non-request specific initialization should be done *before* the handler
# method is run. It is run with burst CPU, so we will get faster initialization.
# Boto3 and db helper initialization should go here.
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


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


class ResponseBody(TypedDict):
    """
    Data returned in lambda function response.
    """

    title: str
    details: dict[str | UUID, str | None]
    ryhti_responses: dict[UUID, "RyhtiResponse"]


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

    If plan_uuid is empty, all plans in database are processed.

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


class Action(enum.Enum):
    GET_PLANS = "get_plans"
    VALIDATE_PLANS = "validate_plans"
    GET_PERMANENT_IDENTIFIERS = "get_permanent_plan_identifiers"
    GET_PLAN_MATTERS = "get_plan_matters"
    VALIDATE_PLAN_MATTERS = "validate_plan_matters"
    POST_PLAN_MATTERS = "post_plan_matters"


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
    if (
        event_type is Action.GET_PERMANENT_IDENTIFIERS
        or event_type is Action.VALIDATE_PLAN_MATTERS
        or event_type is Action.POST_PLAN_MATTERS
    ) and (
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

    database_client = client.database_client

    if database_client.plans:
        if event_type is Action.GET_PLANS:
            # just return the JSON to the user
            response_title = "Returning serialized plans from database."
            LOGGER.info(response_title)
            lambda_response = Response(
                statusCode=200,
                body=ResponseBody(
                    title=response_title,
                    details=cast(dict, database_client.plan_dictionaries),
                    ryhti_responses={},
                ),
            )

        if event_type is Action.GET_PLAN_MATTERS:
            # just return the JSON to the user
            LOGGER.info("Formatting plan matter data...")
            plan_matters = database_client.get_plan_matters()
            response_title = "Returning serialized plan matters from database."
            LOGGER.info(response_title)
            lambda_response = Response(
                statusCode=200,
                body=ResponseBody(
                    title=response_title,
                    details=cast(dict, plan_matters),
                    ryhti_responses={},
                ),
            )

        if event_type is Action.VALIDATE_PLANS:
            # 1) Validate plans in database with public API
            LOGGER.info("Validating plans...")
            validation_responses = client.validate_plans()
            # 2) Save and return plan validation data
            LOGGER.info("Saving plan validation data...")
            save_details = database_client.save_plan_validation_responses(
                validation_responses
            )
            lambda_response = Response(
                statusCode=200,
                body=ResponseBody(
                    title="Plan validations run.",
                    details=save_details,  # type: ignore[typeddict-item]
                    ryhti_responses=validation_responses,
                ),
            )

        if event_type is Action.GET_PERMANENT_IDENTIFIERS:
            LOGGER.info("Authenticating to X-road Ryhti API...")
            client.xroad_ryhti_authenticate()
            # 1) Check or create permanent plan identifiers, from X-Road API
            LOGGER.info("Getting permanent plan identifiers for plans...")
            plan_identifier_responses = client.get_permanent_plan_identifiers()
            # 2) Save and return permanent plan identifiers
            LOGGER.info("Setting permanent plan identifiers for plans...")
            save_details = database_client.set_permanent_plan_identifiers(
                plan_identifier_responses
            )
            lambda_response = Response(
                statusCode=200,
                body=ResponseBody(
                    title="Possible permanent plan identifiers set.",
                    details=save_details,  # type: ignore[typeddict-item]
                    ryhti_responses=plan_identifier_responses,
                ),
            )

        if event_type is Action.VALIDATE_PLAN_MATTERS:
            LOGGER.info("Authenticating to X-road Ryhti API...")
            client.xroad_ryhti_authenticate()
            # Documents are exported separately from plan matter. Also, they need to be
            # present in Ryhti *before* plan matter is validated or created.
            #
            # Therefore, let's export all the documents right away, and update them to
            # the latest version when needed. Otherwise, the plan matter would never be
            # valid. Only upload documents for those plans that have permanent plan
            # identifiers.
            # 1) If changed documents exist, upload documents
            LOGGER.info("Checking and updating plan documents for plans...")
            plan_documents = client.upload_plan_documents()
            LOGGER.info("Marking documents exported...")
            database_client.set_plan_documents(plan_documents)
            # 2) Validate plan matters with identifiers with X-Road API
            LOGGER.info("Validating plan matters for plans...")
            responses = client.validate_plan_matters()
            # 3) Save and return plan matter validation data
            LOGGER.info("Saving plan matter validation data for plans...")
            save_details = database_client.save_plan_matter_validation_responses(
                responses
            )
            lambda_response = Response(
                statusCode=200,
                body=ResponseBody(
                    title="Plan matter validations run.",
                    details=save_details,  # type: ignore[typeddict-item]
                    ryhti_responses=responses,
                ),
            )

        if event_type is Action.POST_PLAN_MATTERS:
            LOGGER.info("Authenticating to X-road Ryhti API...")
            client.xroad_ryhti_authenticate()
            # 1) If changed documents exist, upload documents
            LOGGER.info("Checking and updating plan documents for plans...")
            plan_documents = client.upload_plan_documents()
            LOGGER.info("Marking documents exported...")
            database_client.set_plan_documents(plan_documents)
            # 2) Create or update Ryhti plan matters
            LOGGER.info("POSTing plan matters...")
            responses = client.post_plan_matters()
            # 3) Save and return plan matter update responses
            LOGGER.info("Saving plan matter POST data for posted plans...")
            save_details = database_client.save_plan_matter_post_responses(responses)
            lambda_response = Response(
                statusCode=200,
                body=ResponseBody(
                    title="Plan matters POSTed.",
                    details=save_details,  # type: ignore[typeddict-item]
                    ryhti_responses=responses,
                ),
            )
    else:
        lambda_response = Response(
            statusCode=200,
            body=ResponseBody(
                title="Plans not found, exiting.",
                details={},
                ryhti_responses={},
            ),
        )

    LOGGER.info(lambda_response["body"]["title"])
    return responsify(lambda_response, using_api_gateway)
