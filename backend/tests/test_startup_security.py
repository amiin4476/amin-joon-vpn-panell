import pytest
from fastapi.testclient import TestClient

from app.main import app


VALID_FERNET_KEY = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
VALID_APP_SECRET = "test-only-secret-key-for-startup-tests"


def test_startup_rejects_missing_app_secret(monkeypatch):
    monkeypatch.setenv("NODE_CREDENTIALS_KEY", VALID_FERNET_KEY)
    monkeypatch.delenv("APP_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="APP_SECRET_KEY is not configured"):
        with TestClient(app):
            pass


def test_startup_rejects_short_app_secret(monkeypatch):
    monkeypatch.setenv("NODE_CREDENTIALS_KEY", VALID_FERNET_KEY)
    monkeypatch.setenv("APP_SECRET_KEY", "short-secret")

    with pytest.raises(RuntimeError, match="at least 32 bytes"):
        with TestClient(app):
            pass


def test_startup_succeeds_with_valid_secrets(monkeypatch):
    monkeypatch.setenv("NODE_CREDENTIALS_KEY", VALID_FERNET_KEY)
    monkeypatch.setenv("APP_SECRET_KEY", VALID_APP_SECRET)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
