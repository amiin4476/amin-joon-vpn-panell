
import asyncio

import pytest
from cryptography.fernet import Fernet

from app import node_security
from app.node_client import (
    NodeConnectionError,
    check_node_health,
    get_node_metrics,
    format_node_host,
)


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {"status": "ok"}


class FakeAsyncClient:
    last_url = None
    last_headers = None

    def __init__(self, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get(self, url, headers):
        FakeAsyncClient.last_url = url
        FakeAsyncClient.last_headers = headers
        return FakeResponse()


def prepare_test(monkeypatch):
    key = Fernet.generate_key()
    fernet = Fernet(key)

    encrypted_token = fernet.encrypt(
        b"test-secret-token"
    ).decode("utf-8")

    monkeypatch.setattr(
        node_security,
        "get_node_fernet",
        lambda: fernet,
    )

    monkeypatch.setattr(
        "app.node_client.httpx.AsyncClient",
        FakeAsyncClient,
    )

    return encrypted_token


def test_node_health_uses_https_and_token(monkeypatch):
    encrypted_token = prepare_test(monkeypatch)

    result = asyncio.run(
        check_node_health(
            "example.com",
            443,
            encrypted_token,
        )
    )

    assert result == {"status": "ok"}
    assert FakeAsyncClient.last_url == (
        "https://example.com:443/api/v1/ping"
    )
    assert FakeAsyncClient.last_headers[
        "Authorization"
    ] == "Bearer test-secret-token"


def test_node_metrics_uses_https(monkeypatch):
    encrypted_token = prepare_test(monkeypatch)

    result = asyncio.run(
        get_node_metrics(
            "example.com",
            443,
            encrypted_token,
        )
    )

    assert result == {"status": "ok"}
    assert FakeAsyncClient.last_url == (
        "https://example.com:443/api/v1/metrics"
    )


def test_ipv4_node_address():
    assert format_node_host("192.0.2.10") == "192.0.2.10"


def test_ipv6_node_address():
    assert format_node_host("2001:db8::10") == "[2001:db8::10]"


def test_ipv6_node_address_with_brackets():
    assert format_node_host("[2001:db8::10]") == "[2001:db8::10]"


def test_domain_node_address():
    assert format_node_host("agent.example.com") == "agent.example.com"


def test_invalid_node_address():
    with pytest.raises(NodeConnectionError):
        format_node_host("https://example.com/path")


def test_ipv6_node_connection_uses_brackets(monkeypatch):
    encrypted_token = prepare_test(monkeypatch)

    result = asyncio.run(
        check_node_health(
            "2001:db8::10",
            443,
            encrypted_token,
        )
    )

    assert result == {"status": "ok"}
    assert FakeAsyncClient.last_url == (
        "https://[2001:db8::10]:443/api/v1/ping"
    )
