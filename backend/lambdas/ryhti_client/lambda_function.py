from __future__ import annotations

import base64
import enum
import gzip
import logging
import os
import time
import uuid
from collections.abc import Callable
from copy import deepcopy
from functools import wraps
from typing import TYPE_CHECKING, Any, Literal, NotRequired, TypedDict, cast

import boto3
import simplejson as json
from botocore.config import Config
from pydantic import ValidationError

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
from ryhti_client.plan_copier import CopyPlanData
from ryhti_client.ryhti_client import RyhtiClient

if TYPE_CHECKING:
    from ryhti_client.ryhti_client import RyhtiResponse

# All non-request specific initialization should be done *before* the handler
# method is run. It is run with burst CPU, so we will get faster initialization.
# Boto3 and db helper initialization should go here.
LOGGER = logging.getLogger()

if os.environ.get("DEBUGPY") == "1":
    import debugpy  # type: ignore[import-not-found]  # noqa: T100

    debugpy.listen(("0.0.0.0", 5678))  # noqa: S104, T100
    print("debugpy listening on port 5678", flush=True)
    if os.environ.get("DEBUGPY_WAIT") == "1":
        print("Waiting for VS Code debugger to attach...", flush=True)
        debugpy.wait_for_client()  # noqa: T100

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

# Bucket for transferring large plan files (import/export) via presigned URLs.
ryhti_files_bucket = os.environ.get("RYHTI_FILES_BUCKET", "")
if not ryhti_files_bucket:
    raise ValueError(
        "Please set RYHTI_FILES_BUCKET environment variable to run Ryhti client."
    )
presigned_url_expiry_seconds = int(os.environ.get("PRESIGNED_URL_EXPIRY_SECONDS", 3600))
# Presigned URLs require SigV4. In local development AWS_ENDPOINT_URL_S3 points
# the client at MinIO. Against AWS, pin the client to the regional endpoint:
# the global endpoint redirects (307) requests for newly created buckets until
# DNS propagates, and clients cannot follow the redirect because the presigned
# signature covers the Host header.
s3_region = os.environ.get("AWS_REGION_NAME", "") or None
s3_endpoint_url = os.environ.get("AWS_ENDPOINT_URL_S3", "") or (
    f"https://s3.{s3_region}.amazonaws.com" if s3_region else None
)
s3_client = boto3.client(
    "s3",
    region_name=s3_region,
    endpoint_url=s3_endpoint_url,
    config=Config(signature_version="s3v4"),
)


class ResponseBody(TypedDict):
    """Data returned in lambda function response."""

    title: str
    # A human-readable message, or a small payload dict such as
    # {"download_url": ..., "key": ...} or {"error": ...}.
    details: str | dict[str, str] | None
    # Response from the Ryhti API, for actions that call the Ryhti API.
    ryhti_response: RyhtiResponse | None


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

    If save_json is true, generated JSON as well as Ryhti API response are saved
    as {plan_id}.json and {plan_id}.response.json in the logs directory.
    """

    action: str  # Action
    plan_uuid: NotRequired[str | None]  # UUID for plan to be used

    # True if we want JSON files to be saved in ryhti_debug
    save_json: NotRequired[bool | None]

    # Additional data to be used in the action, if needed. For import_plan,
    # data must contain "s3_key" (returned by get_upload_url, after the plan
    # file has been uploaded with the presigned URL) and "extra_data".
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
    GET_PLAN = "get_plan"
    VALIDATE_PLAN = "validate_plan"
    GET_PERMANENT_IDENTIFIER = "get_permanent_plan_identifier"
    # Plan matter support has been removed from Arho. The actions are kept so
    # that old clients get a clear 405 response instead of an unknown action.
    GET_PLAN_MATTERS = "get_plan_matters"
    VALIDATE_PLAN_MATTERS = "validate_plan_matters"
    POST_PLAN_MATTERS = "post_plan_matters"
    IMPORT_PLAN = "import_plan"
    COPY_PLAN = "copy_plan"
    GET_UPLOAD_URL = "get_upload_url"


# Actions that operate on a single plan and require a plan_uuid in the event.
PLAN_UUID_REQUIRED_ACTIONS = frozenset(
    {
        Action.GET_PLAN,
        Action.VALIDATE_PLAN,
        Action.GET_PERMANENT_IDENTIFIER,
        Action.COPY_PLAN,
    }
)

REMOVED_PLAN_MATTER_ACTIONS = frozenset(
    {Action.GET_PLAN_MATTERS, Action.VALIDATE_PLAN_MATTERS, Action.POST_PLAN_MATTERS}
)


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


def simple_response(
    status_code: int, title: str, details: str | dict[str, str] | None = None
) -> Response:
    """Build a lambda response that has no Ryhti API response attached."""
    LOGGER.info(title)
    return Response(
        statusCode=status_code,
        body=ResponseBody(title=title, details=details, ryhti_response=None),
    )


def check_action_preconditions(
    event_type: Action, action_name: str, plan_uuid: str | None
) -> Response | None:
    """Check that the action can be run with the given event.

    Returns an error response if the action cannot be run, otherwise None.
    """
    if event_type in REMOVED_PLAN_MATTER_ACTIONS:
        # Plan matter support removed from Arho. See git history for previous
        # implementation.
        return simple_response(
            405,
            "Plan matter actions not supported.",
            {"error": "Plan matter support has been removed from Arho."},
        )

    if event_type is Action.GET_PERMANENT_IDENTIFIER and (
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

    if event_type in PLAN_UUID_REQUIRED_ACTIONS:
        if not plan_uuid:
            return simple_response(
                400,
                "Missing plan_uuid.",
                {"error": f"plan_uuid is required for action {action_name}."},
            )
        try:
            uuid.UUID(plan_uuid)
        except ValueError:
            return simple_response(
                400, "Invalid plan_uuid.", {"error": "plan_uuid must be a valid UUID."}
            )

    return None


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
                        ryhti_response=None,
                    ),
                ),
                is_api_gateway_event(payload),
            )

    return wrapper


def log_action_duration(func: HandlerType) -> HandlerType:
    """Decorator to log a parseable line with the action name and handler
    wall time, for CloudWatch Logs Insights duration queries per action.
    """

    @wraps(func)
    def wrapper(
        payload: ArhoPayload | AWSAPIGatewayPayload, context: dict[str, Any]
    ) -> Response | CompressedResponse | AWSAPIGatewayResponse:
        start = time.perf_counter()
        try:
            return func(payload, context)
        finally:
            action = "unknown"
            try:
                action = str(normalize_payload(payload)["body"].get("action"))
            except Exception:  # noqa: BLE001
                # Timing is best effort; never mask the response.
                LOGGER.warning("Could not resolve action name for timing log.")
            LOGGER.info(
                "arho_timing action=%s duration_ms=%d",
                action,
                round((time.perf_counter() - start) * 1000),
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


@return_500_on_unhandled_exceptions
@log_action_duration
def handler(
    payload: ArhoPayload | AWSAPIGatewayPayload, context: dict[str, Any]
) -> Response | CompressedResponse | AWSAPIGatewayResponse:
    """Handler which is called when accessing the endpoint. We must handle both API
    gateway HTTP requests and regular lambda requests. API gateway requires
    the response body to be stringified.

    If lambda runs successfully, we always return 200 OK. In case a python
    exception occurs, AWS lambda will return the exception.

    We want to return general result message of the lambda run, as well as the
    Ryhti API response for actions that call the Ryhti API.
    """
    LOGGER.info(f"Received payload {payload}...")

    using_api_gateway = is_api_gateway_event(payload)
    normalized_payload = normalize_payload(payload)
    event = normalized_payload["body"]
    compress_response = (
        "gzip"
        in normalized_payload.get("headers", {}).get("Accept-Encoding", "").lower()
    )
    action_name = event.get("action")
    if action_name is None:
        return format_response(
            simple_response(400, "Missing action.", {"error": "action is required."}),
            using_api_gateway,
            compress_response,
        )
    try:
        event_type = Action(action_name)
    except ValueError:
        return format_response(
            simple_response(
                400, "Unknown action.", {"error": f"Unknown action: {action_name}"}
            ),
            using_api_gateway,
            compress_response,
        )
    debug_json = event.get("save_json", False)
    plan_uuid = event.get("plan_uuid", None)

    if event_type is Action.GET_UPLOAD_URL:
        # No database access needed; just return a presigned upload URL that the
        # client can PUT the plan file to before calling import_plan.
        key = f"import/{uuid.uuid4()}.json"
        upload_url = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": ryhti_files_bucket, "Key": key},
            ExpiresIn=presigned_url_expiry_seconds,
        )
        return format_response(
            simple_response(
                200, "Upload URL created.", {"upload_url": upload_url, "key": key}
            ),
            using_api_gateway,
            compress_response,
        )

    precondition_error = check_action_preconditions(event_type, action_name, plan_uuid)
    if precondition_error:
        return format_response(precondition_error, using_api_gateway, compress_response)

    connection_params = get_connection_parameters(user_credentials)
    database_client = DatabaseClient(get_connection_string(**connection_params))
    client = RyhtiClient(
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

    if event_type in (
        Action.GET_PLAN,
        Action.VALIDATE_PLAN,
        Action.GET_PERMANENT_IDENTIFIER,
    ):
        try:
            plan = database_client.get_plan(cast("str", plan_uuid))
        except PlanNotFoundError as e:
            return format_response(
                simple_response(404, "Plan not found.", {"error": str(e)}),
                using_api_gateway,
                compress_response,
            )

        if event_type is Action.GET_PLAN:
            # Upload the JSON to S3 and return a presigned download URL. The
            # serialized plan may exceed the lambda 6 MB response limit, so
            # it is never returned inline. The file contains a single bare
            # plan JSON, the same format that import_plan reads.
            response_title = "Returning serialized plan from database."
            LOGGER.info(response_title)
            plan_dictionary = database_client.get_plan_dictionary(plan)
            plan_bytes = gzip.compress(json.dumps(plan_dictionary).encode("utf-8"))
            key = f"export/{uuid.uuid4()}.json"
            s3_client.put_object(
                Bucket=ryhti_files_bucket,
                Key=key,
                Body=plan_bytes,
                ContentType="application/json",
                ContentEncoding="gzip",
            )
            download_url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": ryhti_files_bucket, "Key": key},
                ExpiresIn=presigned_url_expiry_seconds,
            )
            lambda_response = Response(
                statusCode=200,
                body=ResponseBody(
                    title=response_title,
                    details={"download_url": download_url, "key": key},
                    ryhti_response=None,
                ),
            )

        elif event_type is Action.VALIDATE_PLAN:
            # 1) Validate plan with public API
            LOGGER.info("Validating plan...")
            plan_dictionary = database_client.get_plan_dictionary(plan)
            validation_response = client.validate_plan(plan, plan_dictionary)
            # 2) Save and return plan validation data
            LOGGER.info("Saving plan validation data...")
            save_detail = database_client.save_plan_validation_response(
                plan.id, validation_response
            )
            lambda_response = Response(
                statusCode=200,
                body=ResponseBody(
                    title="Plan validation run.",
                    details=save_detail,
                    ryhti_response=validation_response,
                ),
            )

        elif event_type is Action.GET_PERMANENT_IDENTIFIER:
            LOGGER.info("Authenticating to X-road Ryhti API...")
            client.xroad_ryhti_authenticate()
            # 1) Check or create permanent plan identifier, from X-Road API
            LOGGER.info("Getting permanent plan identifier for plan matter...")
            plan_matter = plan.plan_matter
            identifier_response = client.get_permanent_plan_identifier(plan_matter)
            identifier_detail: str | None
            if identifier_response is None:
                # The plan matter already has a permanent identifier.
                identifier_detail = plan_matter.permanent_plan_identifier
            else:
                # 2) Save and return permanent plan identifier
                LOGGER.info("Setting permanent plan identifier for plan matter...")
                identifier_detail = database_client.set_permanent_plan_identifier(
                    plan_matter, identifier_response
                )
            lambda_response = Response(
                statusCode=200,
                body=ResponseBody(
                    title="Possible permanent plan identifier set.",
                    details=identifier_detail,
                    ryhti_response=identifier_response,
                ),
            )

        else:
            lambda_response = simple_response(400, "No action taken.")

    elif event_type is Action.COPY_PLAN:
        raw_data = event.get("data")
        LOGGER.debug("data: %s", raw_data)
        try:
            copy_data = CopyPlanData.model_validate(raw_data or {})
        except ValidationError as e:
            status_code = 400
            title = "Error in provided data."
            copy_details = {"error": str(e)}

        else:
            LOGGER.info("Copying plan...")
            try:
                copied_plan_id = database_client.copy_plan(
                    cast("str", plan_uuid), copy_data
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
            body=ResponseBody(title=title, details=copy_details, ryhti_response=None),
        )

    elif event_type is Action.IMPORT_PLAN:
        data = event.get("data") or {}
        s3_key = data.get("s3_key")
        extra_data = data.get("extra_data")

        details: dict[str, str]
        if s3_key is None or extra_data is None:
            status_code = 400
            title = "Missing plan file key or extra data."
            details = {}
        elif not isinstance(s3_key, str) or not s3_key.startswith("import/"):
            status_code = 400
            title = "Invalid s3_key."
            details = {"error": "s3_key must point to an uploaded import file."}
        else:
            extra_data = cast("dict[str, Any]", extra_data)
            overwrite = event.get("force") is True

            try:
                plan_object = s3_client.get_object(
                    Bucket=ryhti_files_bucket, Key=s3_key
                )
                plan_json = plan_object["Body"].read().decode("utf-8")
            except s3_client.exceptions.NoSuchKey:
                status_code = 400
                title = "Uploaded plan file not found."
                details = {
                    "error": (
                        "No uploaded file found for the provided s3_key. Request "
                        "an upload URL with the get_upload_url action and upload "
                        "the plan file first."
                    )
                }
            else:
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
            body=ResponseBody(title=title, details=details, ryhti_response=None),
        )

    else:
        lambda_response = simple_response(400, "No action taken.")

    return format_response(lambda_response, using_api_gateway, compress_response)
