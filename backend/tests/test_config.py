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
    try:
        Settings(
            node_credentials_key="invalid-key"
        )
    except ValidationError:
        return

    raise AssertionError(
        "Invalid encryption key length was accepted"
    )
