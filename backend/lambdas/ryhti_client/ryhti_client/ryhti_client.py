from __future__ import annotations

import email.utils
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast

import requests
import simplejson as json

if TYPE_CHECKING:
    from uuid import UUID

    from ryhti_client.database_client import DatabaseClient
    from ryhti_client.ryhti_schema import RyhtiPlanMatter, RyhtiPlanMatterPhase

"""
Client for validating and POSTing all Maakuntakaava data to Ryhti API
at https://api.ymparisto.fi/ryhti/plan-public/api/

Validation API:
https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Avoin/ryhti-plan-public-validate-api.json

X-Road POST API:
https://github.com/sykefi/Ryhti-rajapintakuvaukset/blob/main/OpenApi/Kaavoitus/Palveluväylä/Kaavoitus%20OpenApi.json
"""

LOGGER = logging.getLogger(__name__)


class RyhtiResponse(TypedDict):
    """Represents the response of the Ryhti API to a single API all."""

    status: int | None
    detail: str | None
    errors: dict | None
    warnings: dict | None


def save_debug_json(filename: str, data: Any) -> None:
    with Path("ryhti_debug", filename).open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


class RyhtiClient:
    HEADERS = {
        "User-Agent": "ARHO - Open source Ryhti compatible database",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Language": "fi-FI",
    }
    public_api_base = "https://api.ymparisto.fi/ryhti/plan-public/api/"
    xroad_server_address = ""
    xroad_api_path = "/GOV/0996189-5/Ryhti-Syke-service/planService/api/"
    public_headers = HEADERS.copy()
    xroad_headers = HEADERS.copy()

    def __init__(
        self,
        database_client: DatabaseClient,
        public_api_url: str | None = None,
        public_api_key: str = "",
        xroad_syke_client_id: str | None = "",
        xroad_syke_client_secret: str | None = "",
        xroad_server_address: str | None = None,
        xroad_instance: str = "FI-TEST",
        xroad_member_class: str | None = "MUN",
        xroad_member_code: str | None = None,
        xroad_member_client_name: str | None = None,
        xroad_port: int | None = 8080,
        debug_json: bool | None = False,  # save JSON files for debugging
    ) -> None:
        LOGGER.info("Initializing Ryhti client...")
        self.debug_json = debug_json

        self.database_client = database_client

        # Public API only needs an API key and URL
        if public_api_url:
            self.public_api_base = public_api_url
        self.public_api_key = public_api_key
        self.public_headers |= {"Ocp-Apim-Subscription-Key": self.public_api_key}

        # X-Road API needs path and headers configured
        if xroad_server_address:
            self.xroad_server_address = xroad_server_address
            # do not require http in front of local dns record
            if not xroad_server_address.startswith(("http://", "https://")):
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

    def xroad_ryhti_authenticate(self) -> None:
        """Set the client authentication header for making X-Road API requests."""
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
        """Returns correct plan matter api path depending on the plan type URI."""
        api_paths = {
            "1": "RegionalPlanMatter/",
            "2": "LocalMasterPlanMatter/",
            "3": "LocalDetailedPlanMatter/",
        }
        top_level_code = plan_type_uri.split("/")[-1][0]
        return api_paths[top_level_code]

    def validate_plans(self) -> dict[UUID, RyhtiResponse]:
        """Validates all plans serialized in client plan dictionaries."""
        plan_validation_endpoint = f"{self.public_api_base}/Plan/validate"
        responses: dict[UUID, RyhtiResponse] = {}
        for plan_id, plan_dict in self.database_client.plan_dictionaries.items():
            LOGGER.info(f"Validating JSON for plan {plan_id}...")

            # Some plan fields may only be present in plan matter, not in the plan
            # dictionary. In the context of plan validation, they must be provided as
            # query parameters.
            plan = self.database_client.plans[plan_id]
            plan_type_parameter = plan.plan_type.value
            # We only support one area id, no need for commas and concat:
            admin_area_id_parameter = (
                plan.organisation.municipality.value
                if plan.organisation.municipality
                else plan.organisation.administrative_region.value
            )
            if self.debug_json:
                save_debug_json(f"{plan_id}.json", plan_dict)
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
                save_debug_json(f"{plan_id}.response.json", responses[plan_id])
            LOGGER.info(responses[plan_id])
        return responses

    def upload_plan_documents(self) -> dict[UUID, list[RyhtiResponse]]:
        """Upload any changed plan documents. If document has not been modified
        since it was last uploaded, do nothing.
        """
        responses: dict[UUID, list[RyhtiResponse]] = {}
        file_endpoint = self.xroad_server_address + self.xroad_api_path + "File"
        upload_headers = self.xroad_headers.copy()
        # We must *not* provide Content-Type header:
        # https://blog.jetbridge.com/multipart-encoded-python-requests/
        del upload_headers["Content-Type"]
        for plan in self.database_client.plans.values():
            # Only upload documents for plans that are actually going to Ryhti
            if not plan.permanent_plan_identifier:
                continue
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
                                # Let's just piggyback the etag in the response.
                                warnings={"ETag": etag},
                            )
                        )
                        continue
                    # Let's try streaming the file instead of downloading
                    # and then uploading:
                    file_request = requests.get(document.url, stream=True)
                    if file_request.status_code == 200:
                        file_name = document.url.split("/")[-1]
                        file_type = file_request.headers["Content-Type"]
                        # Just read the whole file to memory when sending it.
                        # That might require increasing lambda memory for big
                        # files, but could not get streaming upload to work :(
                        files = {"file": (file_name, file_request.raw, file_type)}
                        # TODO: get coordinate system from file. Maybe not easy
                        # if just streaming it thru.
                        post_parameters = (
                            {"municipalityId": municipality}
                            if municipality
                            else {"regionId": region}
                        )
                        post_response = requests.post(
                            file_endpoint,
                            files=files,
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
                                    # Let's just piggyback the etag in the response.
                                    warnings={"ETag": etag},
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

    def get_permanent_plan_identifiers(self) -> dict[UUID, RyhtiResponse]:
        """Get permanent plan identifiers for all plans that do not have identifiers set."""
        responses: dict[UUID, RyhtiResponse] = {}
        for plan in self.database_client.plans.values():
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
                    detail = "No permission to get plan identifier in this region or municipality!"  # noqa
                    LOGGER.info(detail)
                    responses[plan.id] = {
                        "status": 401,
                        "errors": response.json(),
                        "detail": detail,
                        "warnings": None,
                    }
                elif response.status_code == 400:
                    detail = "Could not get identifier! Most likely producers_plan_identifier is missing."  # noqa
                    LOGGER.info(detail)
                    responses[plan.id] = {
                        "status": 400,
                        "errors": response.json(),
                        "detail": detail,
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
                        f"ryhti_debug/{plan.id}.identifier.response.json",
                        "w",
                        encoding="utf-8",
                    ) as response_file:
                        response_file.write(str(plan_identifier_endpoint) + "\n")
                        response_file.write(str(self.xroad_headers) + "\n")
                        response_file.write(str(data) + "\n")
                        json.dump(
                            responses[plan.id],
                            response_file,
                            indent=4,
                            ensure_ascii=False,
                        )
        return responses

    def validate_plan_matters(self) -> dict[UUID, RyhtiResponse]:
        """Validates all plan matters that have their permanent identifiers set."""
        responses: dict[UUID, RyhtiResponse] = {}
        plan_matter_dictionaries = self.database_client.get_plan_matters()
        for plan_id, plan_matter in plan_matter_dictionaries.items():
            permanent_id = plan_matter["permanentPlanIdentifier"]
            if not permanent_id:
                LOGGER.info("Plan has no permanent id, cannot validate plan matter.")
                continue
            plan_matter_validation_endpoint = (
                self.xroad_server_address
                + self.xroad_api_path
                + self.get_plan_matter_api_path(plan_matter["planType"])
                + f"{permanent_id}/validate"
            )
            LOGGER.info(f"Validating JSON for plan matter {permanent_id}...")

            if self.debug_json:
                save_debug_json(f"{permanent_id}.json", plan_matter)
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
                save_debug_json(f"{permanent_id}.response.json", responses[plan_id])
            LOGGER.info(responses[plan_id])
        return responses

    def create_new_resource(
        self, endpoint: str, resource_dict: RyhtiPlanMatter | RyhtiPlanMatterPhase
    ) -> RyhtiResponse:
        """POST new resource to Ryhti API."""
        response = requests.post(
            endpoint, json=resource_dict, headers=self.xroad_headers
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
        return cast("RyhtiResponse", ryhti_response)

    def update_resource(
        self, endpoint: str, resource_dict: RyhtiPlanMatter | RyhtiPlanMatterPhase
    ) -> RyhtiResponse:
        """PUT resource to Ryhti API."""
        response = requests.put(
            endpoint, json=resource_dict, headers=self.xroad_headers
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
        elif response.status_code == 201:
            # PUT successful, but the resource is weirdly reported as created. This is
            # not in accordance of the API specification.
            #
            # If we really created a new resource, that is an internal implementation
            # detail; for the API consumer, the same resource with existing UUID has
            # been updated. Therefore, the response *should* be HTTP 200.
            # But let's accept HTTP 201 for now:
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
        return cast("RyhtiResponse", ryhti_response)

    def post_plan_matters(self) -> dict[UUID, RyhtiResponse]:
        """POST all plan matter data with permanent identifiers to Ryhti.

        This means either creating a new plan matter, updating the plan matter,
        creating a new plan matter phase, or updating the plan matter phase.
        """
        responses: dict[UUID, RyhtiResponse] = {}
        plan_matter_dictionaries = self.database_client.get_plan_matters()
        for plan_id, plan_matter in plan_matter_dictionaries.items():
            permanent_id = plan_matter["permanentPlanIdentifier"]
            if not permanent_id:
                LOGGER.info("Plan has no permanent id, cannot post plan matter.")
                continue
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
                    save_debug_json(
                        f"{permanent_id}.plan_matter_post_response.json",
                        responses[plan_id],
                    )
                LOGGER.info(responses[plan_id])
                continue
            # 2) If plan matter existed, check or create plan matter phase instead
            if get_response.status_code == 200:
                LOGGER.info(
                    f"Plan matter {permanent_id} found! "
                    "Checking if plan matter phase exists..."
                )
                phases: list[RyhtiPlanMatterPhase] = get_response.json()[
                    "planMatterPhases"
                ]
                local_phase = plan_matter["planMatterPhases"][0]
                local_lifecycle_status = local_phase["lifeCycleStatus"]
                print(phases)
                print(local_phase)

                current_phase = next(
                    (
                        phase
                        for phase in phases
                        if phase["lifeCycleStatus"] == local_lifecycle_status
                    ),
                    None,
                )
                if not current_phase:
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
                        save_debug_json(
                            f"{permanent_id}.plan_matter_phase_post_response.json",
                            responses[plan_id],
                        )
                    LOGGER.info(responses[plan_id])
                    continue
                # 3) If plan matter phase existed, update plan matter phase instead
                LOGGER.info(
                    f"Plan matter phase {current_phase['planMatterPhaseKey']} "
                    f"with status {local_lifecycle_status} found! Updating phase..."
                )
                # Use existing phase id:
                local_phase["planMatterPhaseKey"] = current_phase["planMatterPhaseKey"]
                plan_matter_phase_endpoint = (
                    plan_matter_endpoint
                    + "/phase/"
                    + current_phase["planMatterPhaseKey"]
                )
                responses[plan_id] = self.update_resource(
                    plan_matter_phase_endpoint, local_phase
                )
                if self.debug_json:
                    save_debug_json(
                        f"{permanent_id}.plan_matter_phase_put_response.json",
                        responses[plan_id],
                    )
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
