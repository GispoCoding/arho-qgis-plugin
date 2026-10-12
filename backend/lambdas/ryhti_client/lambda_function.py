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
from datetime import timedelta
from functools import wraps
from typing import TYPE_CHECKING, Any, Literal, NotRequired, Protocol, TypedDict, cast

import boto3
import requests
import simplejson as json
from botocore.config import Config
from owslib.util import ServiceException
from pydantic import ValidationError

from database.db_helper import (
    DbUser,
    get_connection_parameters,
    get_connection_string,
    get_user_credentials,
)
from database.enums import JobStatus
from ryhti_client.database_client import (
    ApprovalDateRequiredError,
    DatabaseClient,
    LifeCycleStatusNotFoundError,
    PlanAlreadyExistsError,
    PlanAlreadyFinalError,
    PlanMatterNotFoundError,
    PlanNotFoundError,
    PlanNotValidError,
    StartDateRequiredError,
    is_valid_plan,
)
from ryhti_client.jobs import (
    JobNotStartedError,
    JobStore,
    is_uuid,
    is_worker_event,
    lambda_job_starter,
)
from ryhti_client.plan_copier import CopyPlanData
from ryhti_client.profiling import log_duration, profile_python
from ryhti_client.ryhti_client import RyhtiClient
from ryhti_client.wfs_importer import (
    AreaGeometryMissingError,
    AreaNotFoundError,
    ImportWfsPlansData,
    WfsPlanClient,
    WfsPlanImporter,
)

if TYPE_CHECKING:
    from database import models
    from ryhti_client.jobs import JobStarter
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

# A job still queued or running this long after it was created or started has
# crashed, see JobStore.get. Terraform sets it to the lambda timeout.
job_time_limit_seconds = os.environ.get("JOB_TIME_LIMIT_SECONDS", "")
if not job_time_limit_seconds:
    raise ValueError(
        "Please set JOB_TIME_LIMIT_SECONDS environment variable to run Ryhti client."
    )
job_time_limit = timedelta(seconds=int(job_time_limit_seconds))

# How a submitted job starts, see choose_job_starter.
job_runner = os.environ.get("JOB_RUNNER", "")
if job_runner not in {"inline", "lambda"}:
    raise ValueError(
        "Please set JOB_RUNNER environment variable to 'inline' or 'lambda' to run "
        f"Ryhti client. It is {job_runner!r}."
    )
# With JOB_RUNNER=lambda, a job runs in a new invocation of this function.
lambda_client = boto3.client(
    "lambda", region_name=os.environ.get("AWS_REGION_NAME", "") or None
)

# WFS service that publishes valid plans as open data, for import_wfs_plans.
ryhti_wfs_url = os.environ.get(
    "RYHTI_WFS_URL", "https://paikkatiedot.ymparisto.fi/geoserver/ryhti_plan/wfs"
)
# Presigned URLs require SigV4. In local development AWS_ENDPOINT_URL_S3 points
# the client at a local S3 gateway. Against AWS, pin the client to the regional
# endpoint: the global endpoint redirects (307) requests for newly created
# buckets until DNS propagates, and clients cannot follow the redirect because
# the presigned signature covers the Host header.
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


class LambdaContext(Protocol):
    """The part of the AWS Lambda context object that the handler reads."""

    # The ARN this invocation was called with, with the alias or version.
    invoked_function_arn: str


class ResponseBody(TypedDict):
    """Data returned in lambda function response."""

    title: str
    # A human-readable message, or a small payload dict such as
    # {"download_url": ..., "key": ...}, {"error": ...} or import counts.
    details: str | dict[str, Any] | None
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

    # True to run the action as a background job. The answer is then 202 with
    # the job_id, and get_job returns the answer of the action when it is done.
    run_as_job: NotRequired[bool | None]

    # The job to read, for get_job.
    job_id: NotRequired[str | None]

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


class Action(enum.StrEnum):
    GET_PLAN = "get_plan"
    VALIDATE_PLAN = "validate_plan"
    GET_PERMANENT_IDENTIFIER = "get_permanent_plan_identifier"
    # Plan matter support has been removed from Arho. The actions are kept so
    # that old clients get a clear 405 response instead of an unknown action.
    GET_PLAN_MATTERS = "get_plan_matters"
    VALIDATE_PLAN_MATTERS = "validate_plan_matters"
    POST_PLAN_MATTERS = "post_plan_matters"
    IMPORT_PLAN = "import_plan"
    IMPORT_WFS_PLANS = "import_wfs_plans"
    COPY_PLAN = "copy_plan"
    FINALIZE_PLAN = "finalize_plan"
    GET_UPLOAD_URL = "get_upload_url"
    GET_JOB = "get_job"


# Actions that operate on a single plan and require a plan_uuid in the event.
PLAN_UUID_REQUIRED_ACTIONS = frozenset(
    {
        Action.GET_PLAN,
        Action.VALIDATE_PLAN,
        Action.GET_PERMANENT_IDENTIFIER,
        Action.COPY_PLAN,
        Action.FINALIZE_PLAN,
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


def check_request(event: ArhoPayload) -> Response | None:
    """Check that the request names an action that can be run with the event.

    The checks need no database, so they can run before any work starts.
    Returns an error response if the request cannot be run, otherwise None.
    """
    action_name = event.get("action")
    if action_name is None:
        return simple_response(400, "Missing action.", {"error": "action is required."})
    try:
        event_type = Action(action_name)
    except ValueError:
        return simple_response(
            400, "Unknown action.", {"error": f"Unknown action: {action_name}"}
        )
    if event_type is Action.GET_JOB:
        return check_job_id(event.get("job_id"))
    return check_action_preconditions(event_type, action_name, event.get("plan_uuid"))


def check_job_id(job_id: str | None) -> Response | None:
    """Check that get_job names a job by a valid UUID.

    Returns an error response if it does not, otherwise None.
    """
    if not job_id:
        return simple_response(
            400, "Missing job_id.", {"error": "job_id is required for action get_job."}
        )
    if not is_uuid(job_id):
        return simple_response(
            400, "Invalid job_id.", {"error": "job_id must be a valid UUID."}
        )
    return None


def create_upload_url() -> Response:
    """Return a presigned URL that the client can PUT the plan file to before
    calling import_plan. No database access is needed.
    """
    key = f"import/{uuid.uuid4()}.json"
    upload_url = s3_client.generate_presigned_url(
        "put_object",
        Params={"Bucket": ryhti_files_bucket, "Key": key},
        ExpiresIn=presigned_url_expiry_seconds,
    )
    return simple_response(
        200, "Upload URL created.", {"upload_url": upload_url, "key": key}
    )


def finalize_plan_action(
    plan: models.Plan, database_client: DatabaseClient, client: RyhtiClient
) -> Response:
    """Make the plan final, so that it is published through the valid views.

    The plan is only made final when it is valid today.

    TEMPORARY: Ryhti validation is skipped. Normally the plan must also pass
    Ryhti validation, and the validation result is saved to the plan just as
    the validate_plan action saves it. Restore the validation block below when
    the Ryhti API can validate the plans again.
    """
    if plan.final:
        return simple_response(
            409,
            "Plan is already final.",
            {"error": str(PlanAlreadyFinalError(plan.id))},
        )
    if not is_valid_plan(plan):
        return simple_response(
            409, "Plan is not valid.", {"error": str(PlanNotValidError(plan.id))}
        )

    # TEMPORARY: Ryhti validation skipped. Restore this block to enable it:
    #
    # LOGGER.info("Validating plan before making it final...")
    # ryhti_plan = database_client.serializer.serialize_plan(plan)
    # validation_response = client.validate_plan(plan, ryhti_plan)
    # save_detail = database_client.save_plan_validation_response(
    #     plan.id, validation_response
    # )
    # if validation_response.get("status") != 200:
    #     return Response(
    #         statusCode=409,
    #         body=ResponseBody(
    #             title="Plan did not pass Ryhti validation.",
    #             details=save_detail,
    #             ryhti_response=validation_response,
    #         ),
    #     )
    del client
    LOGGER.warning("Skipping Ryhti validation before making plan final (temporary).")

    LOGGER.info("Making plan final...")
    result = database_client.finalize_plan(plan.id)
    return Response(
        statusCode=200,
        body=ResponseBody(
            title="Plan made final.", details=result.to_details(), ryhti_response=None
        ),
    )


type HandlerType = Callable[
    [ArhoPayload | AWSAPIGatewayPayload, LambdaContext],
    Response | CompressedResponse | AWSAPIGatewayResponse,
]


def return_500_on_unhandled_exceptions[**P, R](func: HandlerType) -> HandlerType:
    """Decorator to catch unhandled exceptions and return a 500 response."""

    @wraps(func)
    def wrapper(
        payload: ArhoPayload | AWSAPIGatewayPayload, context: LambdaContext
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


def log_invocation_duration(action: str, start: float) -> None:
    """Log a parseable line with the action name and the handler wall time
    since start, for CloudWatch Logs Insights duration queries per action.
    """
    LOGGER.info(
        "arho_timing action=%s duration_ms=%d",
        action,
        round((time.perf_counter() - start) * 1000),
    )


def is_job_submit(event: ArhoPayload) -> bool:
    """Return True if the request asks to run its action as a job.

    Only the JSON value true turns job mode on. get_upload_url and get_job
    ignore the flag, so that a client may send it on every request.
    """
    return event.get("run_as_job") is True and event.get("action") not in {
        Action.GET_UPLOAD_URL,
        Action.GET_JOB,
    }


def timing_action(event: ArhoPayload) -> str:
    """Return the action name for the duration line of a request.

    A job submit is named submit:<action>, so that submits, job runs
    (job:<action>, see run_job_event) and calls without the job flag are
    separate rows in the per-action duration query.
    """
    action = str(event.get("action"))
    if is_job_submit(event):
        return f"submit:{action}"
    return action


def log_action_duration(func: HandlerType) -> HandlerType:
    """Decorator to log the duration line of a request, see log_invocation_duration."""

    @wraps(func)
    def wrapper(
        payload: ArhoPayload | AWSAPIGatewayPayload, context: LambdaContext
    ) -> Response | CompressedResponse | AWSAPIGatewayResponse:
        start = time.perf_counter()
        try:
            return func(payload, context)
        finally:
            action = "unknown"
            try:
                action = timing_action(normalize_payload(payload)["body"])
            except Exception:  # noqa: BLE001
                # Timing is best effort; never mask the response.
                LOGGER.warning("Could not resolve action name for timing log.")
            log_invocation_duration(action, start)

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


def run_action(event: ArhoPayload) -> Response:
    """Run the action of a request that has passed check_request.

    Every action except get_upload_url runs here, so every caller gets the same
    response to the same request. The event is the normalized request body,
    without headers.
    """
    event_type = Action(event["action"])
    debug_json = event.get("save_json", False)
    plan_uuid = event.get("plan_uuid", None)

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
        Action.FINALIZE_PLAN,
    ):
        if event_type in (Action.VALIDATE_PLAN, Action.FINALIZE_PLAN):
            # The JSON must name the plans that are valid now, so the
            # cancellation info is written again before the plan is read.
            database_client.refresh_plan_cancellation_info(cast("str", plan_uuid))
        try:
            with log_duration("fetch_plan"):
                plan = database_client.get_plan(cast("str", plan_uuid))
        except PlanNotFoundError as e:
            return simple_response(404, "Plan not found.", {"error": str(e)})

        if event_type is Action.GET_PLAN:
            # Upload the JSON to S3 and return a presigned download URL. The
            # serialized plan may exceed the lambda 6 MB response limit, so
            # it is never returned inline. The file contains a single bare
            # plan JSON, the same format that import_plan reads.
            response_title = "Returning serialized plan from database."
            LOGGER.info(response_title)
            with profile_python("serialize_plan"), log_duration("serialize_plan"):
                ryhti_plan = database_client.serializer.serialize_plan(plan)
            with log_duration("json_dumps"):
                # The model prints its JSON faster than dumping a dict first.
                plan_json = ryhti_plan.model_dump_json(
                    by_alias=True, exclude_none=True
                ).encode("utf-8")
            with log_duration("gzip_compress"):
                # Level 6 makes a file the same size as the maximum level 9, in a
                # third of the time.
                plan_bytes = gzip.compress(plan_json, compresslevel=6)
            LOGGER.info(
                "arho_export json_bytes=%d gzip_bytes=%d",
                len(plan_json),
                len(plan_bytes),
            )
            key = f"export/{uuid.uuid4()}.json"
            with log_duration("s3_put"):
                s3_client.put_object(
                    Bucket=ryhti_files_bucket,
                    Key=key,
                    Body=plan_bytes,
                    ContentType="application/json",
                    ContentEncoding="gzip",
                )
            with log_duration("presign"):
                download_url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": ryhti_files_bucket, "Key": key},
                    ExpiresIn=presigned_url_expiry_seconds,
                )
            database_client.log_query_summary()
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
            ryhti_plan = database_client.serializer.serialize_plan(plan)
            validation_response = client.validate_plan(plan, ryhti_plan)
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

        elif event_type is Action.FINALIZE_PLAN:
            lambda_response = finalize_plan_action(plan, database_client, client)

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

    elif event_type is Action.IMPORT_WFS_PLANS:
        raw_data = event.get("data")
        LOGGER.debug("data: %s", raw_data)
        wfs_details: dict[str, Any]
        try:
            wfs_data = ImportWfsPlansData.model_validate(raw_data or {})
        except ValidationError as e:
            status_code = 400
            title = "Error in provided data."
            wfs_details = {"error": str(e)}

        else:
            LOGGER.info("Importing plans from WFS...")
            wfs_importer = WfsPlanImporter(
                database_client.Session, WfsPlanClient(ryhti_wfs_url)
            )
            try:
                import_result = wfs_importer.import_plans(
                    wfs_data, overwrite=event.get("force") is True
                )
                status_code = 200
                title = "WFS plans imported."
                wfs_details = import_result.to_details()

            except AreaNotFoundError as e:
                status_code = 404
                title = "Area not found."
                wfs_details = {"error": str(e)}
            except AreaGeometryMissingError as e:
                status_code = 400
                title = "Area geometry missing."
                wfs_details = {"error": str(e)}
            except (requests.RequestException, ServiceException) as e:
                LOGGER.exception("WFS request failed.")
                status_code = 502
                title = "WFS request failed."
                wfs_details = {"error": str(e)}

        lambda_response = Response(
            statusCode=status_code,
            body=ResponseBody(title=title, details=wfs_details, ryhti_response=None),
        )

    else:
        lambda_response = simple_response(400, "No action taken.")

    return lambda_response


def job_store() -> JobStore:
    return JobStore(
        get_connection_string(**get_connection_parameters(user_credentials)),
        job_time_limit,
    )


def choose_job_starter(store: JobStore, context: LambdaContext) -> JobStarter:
    """Return the job starter that JOB_RUNNER names.

    The starter is the only part of job mode that differs between environments.
    """
    if job_runner == "inline":
        # The local Lambda emulator cannot invoke itself, so the job runs at
        # once, inside the submit call.
        def run_at_once(job_id: str) -> None:
            store.run(job_id, run_action)

        return run_at_once
    if job_runner == "lambda":
        # The worker event of the job comes back to handler, see run_job_event.
        return lambda_job_starter(store, lambda_client, context.invoked_function_arn)
    raise ValueError(f"JOB_RUNNER must be 'inline' or 'lambda', not {job_runner!r}.")


def submit_job(event: ArhoPayload, context: LambdaContext) -> Response:
    """Store the request as a job, start the job and answer with its id."""
    store = job_store()
    start = choose_job_starter(store, context)
    request = {key: value for key, value in event.items() if key != "run_as_job"}
    try:
        job_id = store.submit(request, start)
    except JobNotStartedError:
        return simple_response(
            502,
            "Job could not be started.",
            {"error": "The job could not be started. Please try again later."},
        )
    return simple_response(202, "Job submitted.", {"job_id": job_id})


def run_job_event(job_id: str) -> Response:
    """Run the job of a worker event, which a JOB_RUNNER=lambda submit sends.

    The duration line names the action job:<action>, so that job runs and
    synchronous calls are separate rows in the per-action duration query.
    Nobody reads the answer of an Event invocation, so an unexpected error is
    raised, not answered: AWS then counts the invocation as failed.
    """
    start = time.perf_counter()
    request_error = check_job_id(job_id)
    if request_error is not None:
        return request_error
    action = job_store().run(job_id, run_action)
    if action is None:
        # Not queued (a second delivery of the event), or past the time limit.
        return simple_response(409, "Job not run.", {"job_id": job_id})
    log_invocation_duration(f"job:{action}", start)
    return simple_response(200, "Job run.", {"job_id": job_id})


def get_job(job_id: str) -> Response:
    """Answer with the state of the job, and its answer when it is done.

    The answer is 200 whenever the job is found, so that an error status always
    means that the poll failed, never that the job failed.
    """
    job = job_store().get(job_id)
    if job is None:
        return simple_response(
            404, "Job not found.", {"error": f"Job '{job_id}' does not exist."}
        )
    details: dict[str, Any] = {
        "job_id": job.job_id,
        "status": job.status,
        "result": job.result,
    }
    if job.status is JobStatus.FAILED:
        details["error"] = job.error
    return Response(
        statusCode=200,
        body=ResponseBody(title="Job found.", details=details, ryhti_response=None),
    )


def handler(
    payload: ArhoPayload | AWSAPIGatewayPayload | dict[str, str], context: LambdaContext
) -> Response | CompressedResponse | AWSAPIGatewayResponse:
    """Handler which is called when the function is invoked.

    A worker event runs a job in the background. Every other event is a
    request, see handle_request.
    """
    if is_worker_event(payload):
        return run_job_event(cast("dict[str, str]", payload)["job_id"])
    return handle_request(cast("ArhoPayload | AWSAPIGatewayPayload", payload), context)


@return_500_on_unhandled_exceptions
@log_action_duration
def handle_request(
    payload: ArhoPayload | AWSAPIGatewayPayload, context: LambdaContext
) -> Response | CompressedResponse | AWSAPIGatewayResponse:
    """Answer a request to the endpoint. We must handle both API
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

    request_error = check_request(event)
    if request_error is not None:
        response = request_error
    elif is_job_submit(event):
        response = submit_job(event, context)
    elif event["action"] == Action.GET_UPLOAD_URL:
        response = create_upload_url()
    elif event["action"] == Action.GET_JOB:
        response = get_job(cast("str", event.get("job_id")))
    else:
        response = run_action(event)
    return format_response(response, using_api_gateway, compress_response)
