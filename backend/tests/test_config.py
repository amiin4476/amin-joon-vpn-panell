import pytest

from cryptography.fernet import Fernet
from pydantic import ValidationError

from app.config import Settings


def test_valid_encryption_key_is_accepted():
    key = Fernet.generate_key().decode("utf-8")

    settings = Settings(
        node_credentials_key=key
    )

    assert settings.node_credentials_key == key


def test_invalid_key_length_is_rejected():
    with pytest.raises(ValidationError):
        Settings(
            node_credentials_key="invalid-key"
        )


def test_missing_key_is_rejected(monkeypatch):
    monkeypatch.delenv(
        "NODE_CREDENTIALS_KEY",
        raising=False,
    )

    def test_missing_key_is_rejected():
    with pytest.raises(ValidationError):
        Settings.model_validate({})
