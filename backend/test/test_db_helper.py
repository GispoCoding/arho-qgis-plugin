from __future__ import annotations

import boto3.session
import pytest

from database.db_helper import get_secret

APIKEY_ARN = "arn:aws:secretsmanager:eu-north-1:123456789012:secret:test-apikey"


class FakeSecretsManagerClient:
    """The part of the Secrets Manager client that db_helper calls."""

    def get_secret_value(self, SecretId: str) -> dict[str, str]:  # noqa: N803
        return {"SecretString": {APIKEY_ARN: "key-from-aws"}[SecretId]}


class FakeSession:
    def client(self, service_name: str, region_name: str) -> FakeSecretsManagerClient:
        assert service_name == "secretsmanager"
        return FakeSecretsManagerClient()


@pytest.fixture
def in_aws(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("READ_FROM_AWS", "1")
    monkeypatch.setenv("AWS_REGION_NAME", "eu-north-1")
    monkeypatch.setattr(boto3.session, "Session", FakeSession)


@pytest.fixture
def local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("READ_FROM_AWS", "0")


def test_get_secret_reads_the_variable_locally(
    local: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_APIKEY", "local-key")

    assert get_secret("TEST_APIKEY") == "local-key"


def test_get_secret_raises_without_the_variable_locally(
    local: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("TEST_APIKEY", raising=False)

    with pytest.raises(ValueError, match="TEST_APIKEY is not set"):
        get_secret("TEST_APIKEY")


def test_get_secret_reads_secrets_manager_in_aws(
    in_aws: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """In AWS, a key in the environment is ignored: only the secret counts."""
    monkeypatch.setenv("TEST_APIKEY_SECRET_ARN", APIKEY_ARN)
    monkeypatch.setenv("TEST_APIKEY", "key-from-environment")

    assert get_secret("TEST_APIKEY") == "key-from-aws"


def test_get_secret_raises_without_the_secret_arn_in_aws(
    in_aws: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("TEST_APIKEY_SECRET_ARN", raising=False)
    monkeypatch.setenv("TEST_APIKEY", "key-from-environment")

    with pytest.raises(ValueError, match="TEST_APIKEY_SECRET_ARN is not set"):
        get_secret("TEST_APIKEY")
