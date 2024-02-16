import inspect
import json
import logging
import os
from typing import Any, Dict, List, Optional, Type, TypedDict

import boto3
import codes
import requests
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

"""
Koodistot.suomi.fi client for populating all code tables, adapted from
Tarmo lambda functions
"""

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


class Response(TypedDict):
    statusCode: int  # noqa N815
    body: str


class Event(TypedDict):
    pass
    # event_type: int  # EventType


class DatabaseHelper:
    def __init__(self):
        if os.environ.get("READ_FROM_AWS", "1") == "1":
            session = boto3.session.Session()
            client = session.client(
                service_name="secretsmanager",
                region_name=os.environ.get("AWS_REGION_NAME"),
            )
            self._credentials = json.loads(
                client.get_secret_value(SecretId=os.environ.get("DB_SECRET_RW_ARN"))[
                    "SecretString"
                ]
            )
        else:
            self._credentials = {
                "username": os.environ.get("ADMIN_USER"),
                "password": os.environ.get("ADMIN_USER_PW"),
            }

        self._host = os.environ.get("DB_INSTANCE_ADDRESS")
        self._db = os.environ.get("DB_MAIN_NAME")
        self._port = os.environ.get("DB_INSTANCE_PORT", "5432")
        self._region_name = os.environ.get("AWS_REGION_NAME")

    def get_connection_parameters(self) -> Dict[str, str]:
        return {
            "host": self._host,
            "port": self._port,
            "dbname": self._db,
            "user": self._credentials["username"],
            "password": self._credentials["password"],
        }

    def get_connection_string(self) -> str:
        db_params = self.get_connection_parameters()
        return (
            f'postgresql://{db_params["user"]}:{db_params["password"]}'
            f'@{db_params["host"]}:{db_params["port"]}/{db_params["dbname"]}'
        )


def iso_639_two_to_three_letter(language_dict: Dict[str, str]) -> Dict[str, str]:
    """
    Koodistot.suomi.fi uses two letter iso codes, while we use three letter codes.
    """
    language_map = {"fi": "fin", "sv": "swe", "en": "eng"}
    return {language_map[key]: value for key, value in language_dict.items()}


class KoodistotLoader:
    HEADERS = {"User-Agent": "HAME - Ryhti compatible Maakuntakaava database"}
    api_base = (
        "https://koodistot.suomi.fi/codelist-api/api/v1/coderegistries/rytj/codeschemes"
    )

    def __init__(self, connection_string: str, api_url: Optional[str] = None) -> None:
        if api_url:
            self.api_base = api_url
        engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=engine)

        # Only load koodistot that have external URI defined
        self.koodistot: List[Type[codes.CodeBase]] = [
            value
            for name, value in inspect.getmembers(codes, inspect.isclass)
            if issubclass(value, codes.CodeBase) and value.code_list_uri
        ]
        LOGGER.info("Loader initialized with code classes:")
        LOGGER.info(self.koodistot)

    def get_objects(self) -> Dict[Type[codes.CodeBase], List[dict]]:
        """
        Gets all koodistot data, divided by table.
        """
        data = dict()
        for koodisto in self.koodistot:
            name = koodisto.code_list_uri.rsplit("/", 1)[-1]
            LOGGER.info(koodisto.code_list_uri)
            LOGGER.info(name)
            url = f"{self.api_base}/{name}/codes"
            LOGGER.info(f"Loading codes from {url}")
            r = requests.get(url, headers=self.HEADERS)
            r.raise_for_status()
            try:
                data[koodisto] = r.json()["results"]
            except (KeyError, requests.exceptions.JSONDecodeError):
                LOGGER.warning(f"{koodisto} response did not contain data")
                data[koodisto] = []
        return data

    def get_object(self, element: Dict) -> Optional[dict]:
        """
        Returns database-ready dict of object to import, or None if the data
        was invalid.
        """
        code_dict = dict()
        # SQLAlchemy merge() doesn't know how to handle unique constraints that are not
        # pk. Therefore, we will have to specify the primary key here (not generated in
        # db) so we will not get an IntegrityError. Use uuids from koodistot.suomi.fi.
        # https://sqlalchemy.narkive.com/mCDgZiDa/why-does-session-merge-only-look-at-primary-key-and-not-all-unique-keys
        code_dict["id"] = element["id"]
        code_dict["value"] = element["codeValue"]
        short_name = element.get("shortName", None)
        if short_name:
            code_dict["short_name"] = short_name
        code_dict["name"] = iso_639_two_to_three_letter(element["prefLabel"])
        if "description" in element.keys():
            code_dict["description"] = iso_639_two_to_three_letter(
                element["description"]
            )
        code_dict["status"] = element["status"]
        code_dict["level"] = element["hierarchyLevel"]

        # TODO: At the moment, koodisto API seems to always provide the objects in the
        # right order so that parents exist before children. We can just save the
        # parent id as is.
        #
        # We don't know if this is a general feature of koodistot.fi API data, so
        # parents will have to be saved one level at a time, refactoring here, if
        # koodistot.fi API data ordering changes.
        parent = element.get("broaderCode", None)
        if parent:
            code_dict["parent_id"] = parent["id"]
        return code_dict

    def create_object(
        self, code_class: Type[codes.CodeBase], incoming: Dict[str, Any]
    ) -> codes.CodeBase:
        """
        Create code_class instance with incoming field values.
        """
        column_keys = set(code_class.__table__.columns.keys())
        vals = {
            key: incoming[key] for key in set(incoming.keys()).intersection(column_keys)
        }
        return code_class(**vals)

    def save_object(
        self, code_class: Type[codes.CodeBase], object: Dict[str, Any], session: Session
    ) -> bool:
        """
        Save object defined in the object dict as instance of code_class.
        """
        new_obj = self.create_object(code_class, object)
        try:
            session.merge(new_obj)
        except SQLAlchemyError as e:
            # We want to crash for now. That way we'll know if there is a problem with
            # the data.
            raise e
            # LOGGER.exception(f"Error occurred while saving {object}")
        return True

    def save_objects(self, objects: Dict[Type[codes.CodeBase], List[dict]]) -> str:
        """
        Save all objects in the objects dict, grouped by object class.
        """
        successful_actions = 0
        with self.Session() as session:
            for code_class, class_codes in objects.items():
                LOGGER.info(f"Importing codes to {code_class}...")
                for i, element in enumerate(class_codes):
                    if i % 10 == 0:
                        LOGGER.info(
                            f"{100 * float(i) / len(class_codes)}% - {i}/{len(class_codes)}"  # noqa
                        )
                    code = self.get_object(element)
                    if code is not None:
                        succeeded = self.save_object(code_class, code, session)
                        if succeeded:
                            successful_actions += 1
                    else:
                        LOGGER.debug(f"Could not save code data {element}")
            session.commit()
        msg = f"{successful_actions} inserted or updated. 0 deleted."
        LOGGER.info(msg)
        return msg


def handler(event: Event, _) -> Response:
    """Handler which is called when accessing the endpoint."""
    response: Response = {"statusCode": 200, "body": json.dumps("")}
    db_helper = DatabaseHelper()

    loader = KoodistotLoader(db_helper.get_connection_string())
    LOGGER.info("Getting objects...")
    objects = loader.get_objects()

    LOGGER.info("Saving objects...")
    msg = loader.save_objects(objects)
    response["body"] = json.dumps(msg)
    return response
