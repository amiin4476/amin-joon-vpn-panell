from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app import security


def test_create_access_token_success(monkeypatch):
    monkeypatch.setenv(
        "APP_SECRET_KEY",
        "test-secret-key-with-at-least-32-characters",
    )

    token = security.create_access_token(
        user_id=1,
        username="testuser",
        role="admin",
    )

    assert isinstance(token, str)

    payload = jwt.decode(
        token,
        "test-secret-key-with-at-least-32-characters",
        algorithms=["HS256"],
    )

    assert payload["sub"] == "1"
    assert payload["username"] == "testuser"
    assert payload["role"] == "admin"
    assert "exp" in payload


def test_create_access_token_rejects_missing_secret(monkeypatch):
    monkeypatch.delenv("APP_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="not configured"):
        security.create_access_token(
            user_id=1,
            username="testuser",
            role="admin",
        )


def test_create_access_token_rejects_short_secret(monkeypatch):
    monkeypatch.setenv("APP_SECRET_KEY", "short-secret")

    with pytest.raises(RuntimeError, match="at least 32 bytes"):
        security.create_access_token(
            user_id=1,
            username="testuser",
            role="admin",
        )


def test_decode_access_token_success(monkeypatch):
    secret = "test-secret-key-with-at-least-32-characters"

    monkeypatch.setenv("APP_SECRET_KEY", secret)

    token = security.create_access_token(
        user_id=7,
        username="customer",
        role="customer",
    )

    payload = security.decode_access_token(token)

    assert payload["sub"] == "7"
    assert payload["username"] == "customer"


def test_decode_access_token_rejects_wrong_secret(monkeypatch):
    monkeypatch.setenv(
        "APP_SECRET_KEY",
        "test-secret-key-with-at-least-32-characters",
    )

    token = security.create_access_token(
        user_id=1,
        username="testuser",
        role="admin",
    )

    monkeypatch.setenv(
        "APP_SECRET_KEY",
        "another-secret-key-with-at-least-32-characters",
    )

    with pytest.raises(jwt.InvalidTokenError):
        security.decode_access_token(token)


def test_decode_access_token_rejects_missing_secret(monkeypatch):
    monkeypatch.delenv("APP_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="not configured"):
        security.decode_access_token("some-token")


def test_decode_access_token_rejects_expired_token(monkeypatch):
    secret = "test-secret-key-with-at-least-32-characters"
    monkeypatch.setenv("APP_SECRET_KEY", secret)

    expired_payload = {
        "sub": "1",
        "username": "testuser",
        "role": "admin",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }

    token = jwt.encode(
        expired_payload,
        secret,
        algorithm="HS256",
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        security.decode_access_token(token)
