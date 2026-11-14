
import pytest
from pydantic import ValidationError

from app.nodes import (
    NodeCreate,
    NodeUpdate,
    NodeResponse,
    normalize_node_host,
)


def test_node_response_does_not_expose_credentials():
    response_fields = set(NodeResponse.model_fields.keys())

    assert "agent_token" not in response_fields
    assert "agent_token_encrypted" not in response_fields


@pytest.mark.parametrize(
    ("host", "expected"),
    [
        ("example.com", "example.com"),
        ("EXAMPLE.COM", "example.com"),
        (" example.com ", "example.com"),
        ("example.com.", "example.com"),
        ("192.0.2.10", "192.0.2.10"),
        ("2001:db8::10", "2001:db8::10"),
        ("[2001:db8::10]", "2001:db8::10"),
        ("bücher.de", "xn--bcher-kva.de"),
    ],
)
def test_normalize_valid_node_hosts(host, expected):
    assert normalize_node_host(host) == expected


@pytest.mark.parametrize(
    "host",
    [
        "",
        "   ",
        "https://example.com",
        "http://example.com",
        "example.com:443",
        "example.com/path",
        "example.com?query=1",
        "example.com#fragment",
        "user@example.com",
        "-example.com",
        "example-.com",
        "example..com",
        "bad_host.com",
        "256.256.256.256",
    ],
)
def test_reject_invalid_node_hosts(host):
    with pytest.raises(ValueError):
        normalize_node_host(host)


def test_node_create_normalizes_host():
    node = NodeCreate(
        name="Germany Server",
        host=" EXAMPLE.COM ",
        agent_token="a" * 32,
    )

    assert node.host == "example.com"


def test_node_create_accepts_ipv4():
    node = NodeCreate(
        name="Germany Server",
        host="192.0.2.10",
        agent_token="a" * 32,
    )

    assert node.host == "192.0.2.10"


def test_node_create_accepts_bracketed_ipv6():
    node = NodeCreate(
        name="Germany Server",
        host="[2001:db8::10]",
        agent_token="a" * 32,
    )

    assert node.host == "2001:db8::10"


def test_node_create_rejects_url_as_host():
    with pytest.raises(ValidationError):
        NodeCreate(
            name="Germany Server",
            host="https://example.com",
            agent_token="a" * 32,
        )


def test_node_update_normalizes_host():
    update = NodeUpdate(host=" EXAMPLE.COM ")

    assert update.host == "example.com"


def test_node_update_allows_missing_host():
    update = NodeUpdate()

    assert update.host is None


def test_node_update_rejects_invalid_host():
    with pytest.raises(ValidationError):
        NodeUpdate(host="https://example.com")
