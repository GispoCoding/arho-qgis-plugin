from __future__ import annotations

import base64
import datetime
import enum
import gzip
import logging
import os
from collections.abc import Callable
from copy import deepcopy
from functools import wraps
from typing import TYPE_CHECKING, Any, Literal, NotRequired, TypedDict, cast

import boto3
import simplejson as json
from pydantic import BaseModel, ValidationError

from database.db_helper import (
    DbUser,
    get_connection_parameters,
    get_connection_string,
    get_user_credentials,
)
from ryhti_client.database_client import (
    ApprovalDateRequiredError,
    DatabaseClient,
    LifeCycleStatusNotFoundError,
    PlanAlreadyExistsError,
    PlanMatterNotFoundError,
    PlanNotFoundError,
    StartDateRequiredError,
)
from ryhti_client.ryhti_client import RyhtiClient

if TYPE_CHECKING:
    from database.base import DbId
    from ryhti_client.ryhti_client import RyhtiResponse

# All non-request specific initialization should be done *before* the handler
# method is run. It is run with burst CPU, so we will get faster initialization.
# Boto3 and db helper initialization should go here.
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

user_credentials = get_user_credentials(
    DbUser.DBA
)  # Get DB credentials once at cold start.

# Let's fetch the syke secret from AWS secrets, so it cannot be read in plain
# text when looking at lambda env variables.
if os.environ.get("READ_FROM_AWS") == "1" and (
    client_secret_arn := os.environ.get("XROAD_SYKE_CLIENT_SECRET_ARN")
):
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager", region_name=os.environ.get("AWS_REGION_NAME", "")
    )
    xroad_syke_client_secret = client.get_secret_value(SecretId=client_secret_arn)[
        "SecretString"
    ]
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
    """Data returned in lambda function response."""

    title: str
    details: dict[str | DbId, str | None]
    ryhti_responses: dict[DbId, RyhtiResponse]


class Response(TypedDict):
    """Represents the response of the lambda function to the caller.

    Let's abide by the AWS API Gateway 2.0 response format. If we want to specify
    a custom status code, this means that other data must be embedded in request body.

    https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
    """

    statusCode: int
    body: ResponseBody


class CompressedResponse(TypedDict):
    """Represents a compressed response body."""

    statusCode: int
    encoding: Literal["gzip+base64"]
    body: str


class ArhoPayload(TypedDict):
    """Support validating, POSTing or getting a desired plan. If provided directly to
    lambda, the lambda request needs only contain these keys.

    If plan_uuid is empty, all plans in database are processed.

    If save_json is true, generated JSON as well as Ryhti API response are saved
    as {plan_id}.json and {plan_id}.response.json in the ryhti_debug directory.
    """

    action: str  # Action
    plan_uuid: NotRequired[str | None]  # UUID for plan to be used

    # True if we want JSON files to be saved in ryhti_debug
    save_json: NotRequired[bool | None]

    # Additional data to be used in the action, if needed
    data: NotRequired[dict[str, Any] | None]

    # True if we want to force the action, if needed
    force: NotRequired[bool | None]

    # HTTP headers, if lambda function called directly
    headers: NotRequired[dict[str, str]]


class AWSAPIGatewayPayload(TypedDict):
    """Represents the request coming to Lambda through AWS API Gateway.

    The same request may arrive to lambda either through AWS integrations or API
    Gateway. If arriving through the API Gateway, it will contain all data that
    were contained in the whole HTTPS request, and the event is found in request body.

    https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
    """

    version: Literal["2.0"]
    headers: dict[str, str]
    queryStringParameters: dict[str, str]
    requestContext: dict[str, Any]
    body: str  # The event is stringified json, we have to jsonify it first


class AWSAPIGatewayResponse(TypedDict):
    """Represents the response from Lambda to AWS API Gateway.

    For the API gateway, we just have to stringify the body.
    """

    statusCode: int
    body: str  # Response body must be stringified for API gateway
    headers: NotRequired[dict[str, str]]
    isBase64Encoded: NotRequired[bool]


class Action(enum.Enum):
    GET_PLANS = "get_plans"
    VALIDATE_PLANS = "validate_plans"
    GET_PERMANENT_IDENTIFIERS = "get_permanent_plan_identifiers"
    GET_PLAN_MATTERS = "get_plan_matters"
    VALIDATE_PLAN_MATTERS = "validate_plan_matters"
    POST_PLAN_MATTERS = "post_plan_matters"
    IMPORT_PLAN = "import_plan"
    COPY_PLAN = "copy_plan"


def compress(dict_data: ResponseBody) -> str:
    """Compress and base64 encode JSON data for API Gateway response."""
    json_bytes = json.dumps(dict_data).encode("utf-8")
    gzipped = gzip.compress(json_bytes)
    encoded = base64.b64encode(gzipped).decode("utf-8")
    return encoded


def format_direct_invocation_response(
    response: Response, compress_response: bool = False
) -> Response | CompressedResponse:
    """Convert response to compressed response if needed."""
    if compress_response:
        compressed = compress(response["body"])
        return CompressedResponse(
            statusCode=response["statusCode"], encoding="gzip+base64", body=compressed
        )
    return response


def format_api_gateway_response(
    response: Response, compress_response: bool = False
) -> AWSAPIGatewayResponse:
    """Convert response to API gateway response.
    If we want to provide status code to API gateway, the JSON body must be string.
    """
    if compress_response:
        compressed = compress(response["body"])
        return AWSAPIGatewayResponse(
            statusCode=response["statusCode"],
            body=compressed,
            headers={"Content-Encoding": "gzip"},
            isBase64Encoded=True,
        )
    return AWSAPIGatewayResponse(
        statusCode=response["statusCode"], body=json.dumps(response["body"])
    )


def format_response(
    response: Response, using_api_gateway: bool, compress_response: bool = False
) -> Response | CompressedResponse | AWSAPIGatewayResponse:
    """Convert response to API gateway response if the request arrived through API gateway.
    If we want to provide status code to API gateway, the JSON body must be string.
    """
    if using_api_gateway:
        return format_api_gateway_response(response, compress_response)
    return format_direct_invocation_response(response, compress_response)


type HandlerType = Callable[
    [ArhoPayload | AWSAPIGatewayPayload, dict[str, Any]],
    Response | CompressedResponse | AWSAPIGatewayResponse,
]


def return_500_on_unhandled_exceptions[**P, R](func: HandlerType) -> HandlerType:
    """Decorator to catch unhandled exceptions and return a 500 response."""

    @wraps(func)
    def wrapper(
        payload: ArhoPayload | AWSAPIGatewayPayload, context: dict[str, Any]
    ) -> Response | CompressedResponse | AWSAPIGatewayResponse:
        try:
            return func(payload, context)
        except Exception:
            LOGGER.exception("Unhandled exception in lambda handler.")
            return format_response(
                Response(
                    statusCode=500,
                    body=ResponseBody(
                        title="Internal Server Error.",
                        details={
                            "error": (
                                "Internal server error. "
                                "Please contact Arho support team."
                            )
                        },
                        ryhti_responses={},
                    ),
                ),
                is_api_gateway_event(payload),
            )

    return wrapper


def is_api_gateway_event(event: Any) -> bool:
    return isinstance(event, dict) and "requestContext" in event


class NormalizedEvent(TypedDict):
    raw_event: ArhoPayload | AWSAPIGatewayPayload
    headers: dict[str, str]
    body: ArhoPayload


def normalize_payload(event: ArhoPayload | AWSAPIGatewayPayload) -> NormalizedEvent:
    raw_event = deepcopy(event)
    if is_api_gateway_event(event):
        event = cast("AWSAPIGatewayPayload", event)
        headers = event.get("headers", {})
        body_string = event["body"]
        if event.get("isBase64Encoded"):
            body_string = base64.b64decode(body_string).decode("utf-8")
        body_dict = json.loads(body_string)
        body = cast("ArhoPayload", body_dict)
    else:
        event = cast("ArhoPayload", event)
        headers = event.get("headers", {})
        body = cast(
            "ArhoPayload",
            {key: value for key, value in event.items() if key != "headers"},
        )
    return {"raw_event": raw_event, "headers": headers, "body": body}


class CopyPlanData(BaseModel):
    lifecycle_status_uuid: str
    plan_name: dict[str, str]
    approval_date: datetime.date | None = None
    period_of_validity_start: datetime.date | None = None


@return_500_on_unhandled_exceptions
def handler(
    payload: ArhoPayload | AWSAPIGatewayPayload, context: dict[str, Any]
) -> Response | CompressedResponse | AWSAPIGatewayResponse:
    """Handler which is called when accessing the endpoint. We must handle both API
    gateway HTTP requests and regular lambda requests. API gateway requires
    the response body to be stringified.

    If lambda runs successfully, we always return 200 OK. In case a python
    exception occurs, AWS lambda will return the exception.

    We want to return general result message of the lambda run, as well as all the
    Ryhti API results and errors, separated by plan id.
    """
    LOGGER.info(f"Received payload {payload}...")

    using_api_gateway = is_api_gateway_event(payload)
    normalized_payload = normalize_payload(payload)
    event = normalized_payload["body"]
    compress_response = (
        "gzip"
        in normalized_payload.get("headers", {}).get("Accept-Encoding", "").lower()
    )
    try:
        event_type = Action(event["action"])
    except KeyError:
        event_type = Action.VALIDATE_PLANS
    except ValueError:
        response_title = "Unknown action."
        LOGGER.info(response_title)
        return format_response(
            Response(
                statusCode=400,
                body=ResponseBody(
                    title=response_title,
                    details={event["action"]: "Unknown action."},
                    ryhti_responses={},
                ),
            ),
            using_api_gateway,
            compress_response,
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
            "Please set your local XROAD_SERVER_ADDRESS and your organization "
            "XROAD_MEMBER_CODE and XROAD_MEMBER_CLIENT_NAME to make API requests "
            "to X-Road endpoints. Also, set XROAD_SYKE_CLIENT_ID and "
            "XROAD_SYKE_CLIENT_SECRET that you have received when registering to "
            "access SYKE X-Road API. To use production X-Road instead of test "
            "X-road, you must also set XROAD_INSTANCE to FI. By default, it "
            "is set to FI-TEST."
        )
    connection_params = get_connection_parameters(user_credentials)
    database_client = DatabaseClient(
        get_connection_string(**connection_params), plan_uuid=plan_uuid
    )
    client = RyhtiClient(
        database_client=database_client,
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

    if database_client.plans:
        if event_type is Action.GET_PLANS:
            # just return the JSON to the user
            response_title = "Returning serialized plans from database."
            LOGGER.info(response_title)
            lambda_response = Response(
                statusCode=200,
                body=ResponseBody(
                    title=response_title,
                    details=cast("dict", database_client.plan_dictionaries),
                    ryhti_responses={},
                ),
            )

        elif event_type is Action.GET_PLAN_MATTERS:
            # just return the JSON to the user
            LOGGER.info("Formatting plan matter data...")
            plan_matters = database_client.get_plan_matters()
            response_title = "Returning serialized plan matters from database."
            LOGGER.info(response_title)
            lambda_response = Response(
                statusCode=200,
                body=ResponseBody(
                    title=response_title,
                    details=cast("dict", plan_matters),
                    ryhti_responses={},
                ),
            )

        elif event_type is Action.VALIDATE_PLANS:
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

        elif event_type is Action.GET_PERMANENT_IDENTIFIERS:
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

        elif event_type is Action.VALIDATE_PLAN_MATTERS:
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

        elif event_type is Action.POST_PLAN_MATTERS:
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
        elif event_type is Action.COPY_PLAN:
            raw_data = event.get("data")
            LOGGER.debug("data: %s", raw_data)
            try:
                copy_data = CopyPlanData.model_validate(raw_data or {})
            except ValidationError as e:
                status_code = 400
                title = "Error in provided data."
                details = {"error": str(e)}

            else:
                if plan_uuid is None:
                    LOGGER.warning("Copying plan failed. Required parameters missing.")
                    status_code = 400
                    title = "Error in provided data."
                    copy_details = {
                        "error": "plan_uuid parameter is required for copying a plan."
                    }

                else:
                    LOGGER.info("Copying plan...")
                    try:
                        copied_plan_id = database_client.copy_plan(
                            plan_uuid,
                            copy_data.lifecycle_status_uuid,
                            copy_data.plan_name,
                            approval_date=copy_data.approval_date,
                            period_of_validity_start=copy_data.period_of_validity_start,
                        )
                        status_code = 200
                        title = "Plan copied."
                        copy_details = {"copied_plan_id": str(copied_plan_id)}

                    except (ApprovalDateRequiredError, StartDateRequiredError) as e:
                        title = "Error copying plan."
                        status_code = 400
                        copy_details = {"error": str(e)}
                    except (PlanNotFoundError, LifeCycleStatusNotFoundError) as e:
                        title = "Error copying plan."
                        status_code = 404
                        copy_details = {"error": str(e)}

            lambda_response = Response(
                statusCode=status_code,
                body=ResponseBody(
                    title=title,
                    details=copy_details,  # type: ignore[typeddict-item]
                    ryhti_responses={},
                ),
            )

        else:
            lambda_response = Response(
                statusCode=400,
                body=ResponseBody(
                    title="No action taken.", details={}, ryhti_responses={}
                ),
            )

    elif event_type is Action.IMPORT_PLAN:
        data = event.get("data") or {}
        plan_json = data.get("plan_json")
        extra_data = data.get("extra_data")

        if plan_json is None or extra_data is None:
            status_code = 400
            title = "Missing plan data or extra data."
            details = {}
        else:
            plan_json = cast("str", plan_json)
            extra_data = cast("dict[str, Any]", extra_data)
            overwrite = event.get("force") is True

            try:
                imported_id = database_client.import_plan(
                    plan_json, extra_data, overwrite
                )
                status_code = 200
                title = "Plan imported."
                details = {"plan_id": str(imported_id)}
            except PlanAlreadyExistsError as e:
                status_code = 200  # TODO change to to 409 after plugin fixed.
                title = "Plan already exists."
                details = {"plan_id": str(e.plan_id)}
            except PlanMatterNotFoundError as e:
                status_code = 400
                title = "Plan matter not found."
                details = {"plan_matter_id": str(e.plan_matter_id)}
            except ValueError as e:
                status_code = 400
                title = "Error in provided data."
                details = {"error": str(e)}
            except Exception as e:
                LOGGER.exception("Error importing plan.")
                status_code = 500
                title = "Error importing plan."
                details = {"error": str(e)}

        lambda_response = Response(
            statusCode=status_code,
            body=ResponseBody(
                title=title,
                details=details,  # type: ignore[typeddict-item]
                ryhti_responses={},
            ),
        )

    else:
        lambda_response = Response(
            statusCode=200,
            body=ResponseBody(
                title="Plans not found, exiting.", details={}, ryhti_responses={}
            ),
        )

    return format_response(lambda_response, using_api_gateway, compress_response)
