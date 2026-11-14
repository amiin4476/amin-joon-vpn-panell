import jwt
import pytest

from app.security import decode_access_token


def test_rejects_token_signed_with_wrong_secret(monkeypatch):
    monkeypatch.setenv(
        "APP_SECRET_KEY",
        "correct-secret-key-with-at-least-32-characters",
    )

    forged_token = jwt.encode(
        {
            "sub": "1",
            "username": "attacker",
            "role": "admin",
        },
        "wrong-secret-key-with-at-least-32-characters",
        algorithm="HS256",
    )

    with pytest.raises(jwt.InvalidSignatureError):
        decode_access_token(forged_token)


def test_rejects_malformed_token(monkeypatch):
    monkeypatch.setenv(
        "APP_SECRET_KEY",
        "correct-secret-key-with-at-least-32-characters",
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("this-is-not-a-valid-jwt")


def test_rejects_token_with_modified_payload(monkeypatch):
    secret = "correct-secret-key-with-at-least-32-characters"
    monkeypatch.setenv("APP_SECRET_KEY", secret)

    token = jwt.encode(
        {
            "sub": "1",
            "username": "customer",
            "role": "customer",
        },
        secret,
        algorithm="HS256",
    )

    parts = token.split(".")
    parts[1] = parts[1][:-1] + (
        "A" if parts[1][-1] != "A" else "B"
    )
    modified_token = ".".join(parts)

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(modified_token)
