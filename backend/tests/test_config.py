
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


def test_default_cors_origin_is_localhost():
    settings = Settings(
        node_credentials_key=Fernet.generate_key().decode("utf-8")
    )

    assert settings.cors_origins == [
        "http://localhost:5173"
    ]


def test_custom_domain_cors_origin_is_accepted():
    settings = Settings(
        node_credentials_key=Fernet.generate_key().decode("utf-8"),
        cors_origins=["https://panel.example.com"],
    )

    assert settings.cors_origins == [
        "https://panel.example.com"
    ]


def test_custom_ip_cors_origin_is_accepted():
    settings = Settings(
        node_credentials_key=Fernet.generate_key().decode("utf-8"),
        cors_origins=["http://192.168.1.100:5173"],
    )

    assert settings.cors_origins == [
        "http://192.168.1.100:5173"
    ]


def test_multiple_cors_origins_are_accepted():
    settings = Settings(
        node_credentials_key=Fernet.generate_key().decode("utf-8"),
        cors_origins=[
            "https://panel.example.com",
            "http://192.168.1.100:5173",
        ],
    )

    assert len(settings.cors_origins) == 2


def test_cors_origins_are_trimmed_and_deduplicated():
    settings = Settings(
        node_credentials_key=Fernet.generate_key().decode("utf-8"),
        cors_origins=[
            " https://panel.example.com/ ",
            "https://panel.example.com",
        ],
    )

    assert settings.cors_origins == [
        "https://panel.example.com"
    ]


def test_cors_origin_without_http_scheme_is_rejected():
    try:
        Settings(
            node_credentials_key=Fernet.generate_key().decode("utf-8"),
            cors_origins=["panel.example.com"],
        )
    except ValidationError:
        return

    raise AssertionError(
        "CORS origin without HTTP scheme was accepted"
    )


def test_wildcard_cors_origin_is_rejected():
    try:
        Settings(
            node_credentials_key=Fernet.generate_key().decode("utf-8"),
            cors_origins=["*"],
        )
    except ValidationError:
        return

    raise AssertionError(
        "Wildcard CORS origin was accepted"
    )


def test_cors_origin_with_query_string_is_rejected():
    try:
        Settings(
            node_credentials_key=Fernet.generate_key().decode("utf-8"),
            cors_origins=["https://panel.example.com/?token=123"],
        )
    except ValidationError:
        return

    raise AssertionError(
        "CORS origin with query string was accepted"
    )
