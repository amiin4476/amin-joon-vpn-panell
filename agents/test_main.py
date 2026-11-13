
import importlib
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def agent_client(monkeypatch):
    monkeypatch.setenv(
        "AGENT_TOKEN",
        "test-agent-token-12345678901234567890",
    )
    monkeypatch.setenv("NODE_NAME", "test-node")

    import main
    importlib.reload(main)

    return TestClient(main.app)


def test_health_endpoint(agent_client):
    response = agent_client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ping_requires_authentication(agent_client):
    response = agent_client.get("/api/v1/ping")

    assert response.status_code == 401


def test_ping_accepts_valid_token(agent_client):
    response = agent_client.get(
        "/api/v1/ping",
        headers={
            "Authorization": (
                "Bearer test-agent-token-12345678901234567890"
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "connected"


def test_metrics_returns_resource_data(
    agent_client,
    monkeypatch,
):
    import main

    monkeypatch.setattr(
        main.psutil,
        "cpu_percent",
        lambda interval=None: 25.5,
    )

    monkeypatch.setattr(
        main.psutil,
        "cpu_count",
        lambda: 4,
    )

    class FakeMemory:
        total = 1000
        used = 600
        percent = 60.0

    class FakeDisk:
        total = 2000
        used = 800
        free = 1200
        percent = 40.0

    monkeypatch.setattr(
        main.psutil,
        "virtual_memory",
        lambda: FakeMemory(),
    )

    monkeypatch.setattr(
        main.psutil,
        "disk_usage",
        lambda path: FakeDisk(),
    )

    response = agent_client.get(
        "/api/v1/metrics",
        headers={
            "Authorization": (
                "Bearer test-agent-token-12345678901234567890"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["cpu_percent"] == 25.5
    assert data["memory_percent"] == 60.0
    assert data["disk_percent"] == 40.0
