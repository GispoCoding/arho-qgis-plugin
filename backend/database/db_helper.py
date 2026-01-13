from __future__ import annotations

import json
import os
from enum import Enum
from typing import TypedDict, cast

import boto3


class ConnectionParameters(TypedDict):
    host: str
    port: str
    dbname: str
    user: str
    password: str


class UserCredentials(TypedDict):
    username: str
    password: str


class DbUser(Enum):
    DBA = "dba"
    SU = "su"


user_secret_arns = {
    DbUser.DBA: os.environ.get("DB_SECRET_DBA_ARN"),
    DbUser.SU: os.environ.get("DB_SECRET_SU_ARN"),
}

local_user_credentials = {
    DbUser.DBA: UserCredentials(username=username, password=password)
    if (username := os.environ.get("DBA_USER"))
    and (password := os.environ.get("DBA_USER_PW"))
    else None,
    DbUser.SU: UserCredentials(username=username, password=password)
    if (username := os.environ.get("SU_USER"))
    and (password := os.environ.get("SU_USER_PW"))
    else None,
}


def get_user_credentials_from_aws_secretsmanager(secret_arn: str) -> UserCredentials:
    session = boto3.session.Session()
    client = session.client(  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        service_name="secretsmanager", region_name=os.environ["AWS_REGION_NAME"]
    )
    secret_string = cast(
        "str",
        client.get_secret_value(SecretId=secret_arn)["SecretString"],  # pyright: ignore[reportUnknownMemberType]
    )
    credentials = cast("UserCredentials", json.loads(secret_string))
    return credentials


def get_user_credentials(user: DbUser) -> UserCredentials:
    if os.environ.get("READ_FROM_AWS") == "1":
        user_secret_arn = user_secret_arns.get(user)
        if user_secret_arn is None:
            raise ValueError(
                f"Secret ARN for user {user} is not set in environment variables."
            )

        return get_user_credentials_from_aws_secretsmanager(user_secret_arn)

    credentials = local_user_credentials.get(user)
    if credentials is None:
        raise ValueError(
            f"Credentials for user {user} are not set in environment variables."
        )
    return credentials


def get_connection_parameters(
    user_credentials: UserCredentials | None = None, db_name: str | None = None
) -> ConnectionParameters:
    if user_credentials is None:
        user_credentials = get_user_credentials(DbUser.DBA)
    if db_name is None:
        db_name = os.environ["DB_MAIN_NAME"]
    return {
        "host": os.environ["DB_INSTANCE_ADDRESS"],
        "port": os.environ["DB_INSTANCE_PORT"],
        "dbname": db_name,
        "user": user_credentials["username"],
        "password": user_credentials["password"],
    }


def get_connection_string(
    host: str, port: str, dbname: str, user: str, password: str
) -> str:
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"
