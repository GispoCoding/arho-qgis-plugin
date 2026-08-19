from __future__ import annotations

import email.utils
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast

import requests
import simplejson as json

if TYPE_CHECKING:
    from database import models
    from ryhti_client.ryhti_schema import (
        RyhtiPlan,
        RyhtiPlanMatter,
        RyhtiPlanMatterPhase,
    )

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
    logging_folder = Path("/tmp/logs")  # noqa: S108
    logging_folder.mkdir(exist_ok=True)

    with Path(logging_folder, filename).open("w", encoding="utf-8") as f:
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
                "X-Road-Client": f"{xroad_instance}/{xroad_member_class}/{xroad_member_code}/{xroad_member_client_name}"
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

    def validate_plan(
        self, plan: models.Plan, plan_dictionary: RyhtiPlan
    ) -> RyhtiResponse:
        """Validates a serialized plan with the public Ryhti API."""
        plan_validation_endpoint = f"{self.public_api_base}/Plan/validate"
        LOGGER.info(f"Validating JSON for plan {plan.id}...")

        # Some plan fields may only be present in plan matter, not in the plan
        # dictionary. In the context of plan validation, they must be provided as
        # query parameters.
        plan_type_parameter = plan.plan_matter.plan_type.value
        # We only support one area id, no need for commas and concat:
        admin_area_id_parameter = (
            plan.plan_matter.organisation.municipality.value
            if plan.plan_matter.organisation.municipality
            else plan.plan_matter.organisation.administrative_region.value
        )
        if self.debug_json:
            save_debug_json(f"{plan.id}.json", plan_dictionary)
        LOGGER.info(f"POSTing JSON: {json.dumps(plan_dictionary)}")

        # requests apparently uses simplejson automatically if it is installed!
        # A bit too much magic for my taste, but seems to work.
        response = requests.post(
            plan_validation_endpoint,
            json=plan_dictionary,
            headers=self.public_headers,
            params={
                "planType": plan_type_parameter,
                "administrativeAreaIdentifiers": admin_area_id_parameter,
            },
        )
        LOGGER.info(f"Got response {response}")
        if response.status_code == 200:
            # Successful validation does not return any json!
            ryhti_response: RyhtiResponse = {
                "status": 200,
                "errors": None,
                "detail": None,
                "warnings": None,
            }
        else:
            try:
                # Validation errors always contain JSON
                ryhti_response = response.json()
            except json.JSONDecodeError:
                # There is something wrong with the API
                response.raise_for_status()
        if self.debug_json:
            save_debug_json(f"{plan.id}.response.json", ryhti_response)
        LOGGER.info(ryhti_response)
        return ryhti_response

    def upload_plan_documents(self, plan: models.Plan) -> list[RyhtiResponse]:
        """Upload any changed documents of the plan. If a document has not been
        modified since it was last uploaded, do nothing.

        If the plan has no permanent plan identifier, no documents are uploaded.
        """
        responses: list[RyhtiResponse] = []
        # Only upload documents for plans that are actually going to Ryhti
        if not plan.plan_matter.permanent_plan_identifier:
            return responses
        file_endpoint = self.xroad_server_address + self.xroad_api_path + "File"
        upload_headers = self.xroad_headers.copy()
        # We must *not* provide Content-Type header:
        # https://blog.jetbridge.com/multipart-encoded-python-requests/
        del upload_headers["Content-Type"]
        municipality = (
            plan.plan_matter.organisation.municipality.value
            if plan.plan_matter.organisation.municipality
            else None
        )
        region = plan.plan_matter.organisation.administrative_region.value
        for document in plan.documents:
            if document.url:
                # No need to upload if document hasn't changed
                headers = requests.head(document.url).headers
                print(headers)
                etag = headers.get("ETag")
                last_modified = headers.get("Last-Modified")
                if (
                    document.exported_file_etag and document.exported_file_etag == etag
                ) or (
                    document.exported_at
                    and last_modified
                    and document.exported_at
                    > email.utils.parsedate_to_datetime(last_modified)
                ):
                    LOGGER.info("File unchanged since last upload.")
                    responses.append(
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
                        responses.append(
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
                        responses.append(
                            RyhtiResponse(
                                status=post_response.status_code,
                                detail=f"Could not upload file {file_name}!",
                                errors=post_response.json(),
                                warnings=None,
                            )
                        )
                else:
                    LOGGER.warning("Could not fetch file! Please check file URL.")
                    responses.append(
                        RyhtiResponse(
                            status=None,
                            detail="Could not fetch file! Please check file URL.",
                            errors=None,
                            warnings=None,
                        )
                    )
        return responses

    def get_permanent_plan_identifier(
        self, plan_matter: models.PlanMatter
    ) -> RyhtiResponse | None:
        """Get a permanent plan identifier for the plan matter from the X-Road API.

        Returns None if the plan matter already has a permanent identifier.
        """
        if plan_matter.permanent_plan_identifier:
            return None
        plan_identifier_endpoint = (
            self.xroad_server_address
            + self.xroad_api_path
            + self.get_plan_matter_api_path(plan_matter.plan_type.uri)
            + "permanentPlanIdentifier"
        )
        LOGGER.info(
            "Getting permanent identifier for plan_matter %s...", plan_matter.id
        )
        administrative_area_identifier = (
            plan_matter.organisation.municipality.value
            if plan_matter.organisation.municipality
            else plan_matter.organisation.administrative_region.value
        )
        data = {
            "administrativeAreaIdentifier": administrative_area_identifier,
            "projectName": plan_matter.producers_plan_identifier,
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
            detail = (
                "No permission to get plan identifier in this region or municipality!"  # noqa: E501
            )
            LOGGER.info(detail)
            ryhti_response: RyhtiResponse = {
                "status": 401,
                "errors": response.json(),
                "detail": detail,
                "warnings": None,
            }
        elif response.status_code == 400:
            detail = "Could not get identifier! Most likely producers_plan_identifier is missing."  # noqa: E501
            LOGGER.info(detail)
            ryhti_response = {
                "status": 400,
                "errors": response.json(),
                "detail": detail,
                "warnings": None,
            }
        else:
            response.raise_for_status()
            LOGGER.info("Received identifier %s", response.json())
            ryhti_response = {
                "status": 200,
                "detail": response.json(),
                "errors": None,
                "warnings": None,
            }
        if self.debug_json:
            save_debug_json(
                f"{plan_matter.id}.identifier.response.json", ryhti_response
            )
        return ryhti_response

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
