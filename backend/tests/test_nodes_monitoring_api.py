from app.node_client import NodeConnectionError


def create_node(admin_client):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": "Monitoring Test Node",
            "host": "example.com",
            "port": 22,
            "agent_port": 443,
            "agent_token": "test-agent-token-12345678901234567890",
            "country": "Germany",
            "city": "Frankfurt",
            "description": "Monitoring API test",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_health_endpoint_returns_online(
    admin_client,
    monkeypatch,
):
    node_id = create_node(admin_client)

    async def fake_check_node_health(**kwargs):
        return {"message": "pong"}

    monkeypatch.setattr(
        "app.nodes.check_node_health",
        fake_check_node_health,
    )

    response = admin_client.post(
        f"/nodes/{node_id}/health"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert response.json()["node_id"] == node_id
    assert response.json()["agent"] == {"message": "pong"}


def test_health_endpoint_returns_503_on_connection_error(
    admin_client,
    monkeypatch,
):
    node_id = create_node(admin_client)

    async def fake_check_node_health(**kwargs):
        raise NodeConnectionError("Connection failed")

    monkeypatch.setattr(
        "app.nodes.check_node_health",
        fake_check_node_health,
    )

    response = admin_client.post(
        f"/nodes/{node_id}/health"
    )

    assert response.status_code == 503


def test_metrics_endpoint_returns_data(
    admin_client,
    monkeypatch,
):
    node_id = create_node(admin_client)

    expected_metrics = {
        "cpu_percent": 25.5,
        "memory_percent": 60.0,
        "disk_percent": 45.0,
    }

    async def fake_get_node_metrics(**kwargs):
        return expected_metrics

    monkeypatch.setattr(
        "app.nodes.get_node_metrics",
        fake_get_node_metrics,
    )

    response = admin_client.get(
        f"/nodes/{node_id}/metrics"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["node_id"] == node_id
    assert data["node_name"] == "Monitoring Test Node"
    assert data["status"] == "online"
    assert data["metrics"] == expected_metrics


def test_metrics_endpoint_returns_503_on_connection_error(
    admin_client,
    monkeypatch,
):
    node_id = create_node(admin_client)

    async def fake_get_node_metrics(**kwargs):
        raise NodeConnectionError("Connection failed")

    monkeypatch.setattr(
        "app.nodes.get_node_metrics",
        fake_get_node_metrics,
    )

    response = admin_client.get(
        f"/nodes/{node_id}/metrics"
    )

    assert response.status_code == 503


def test_health_endpoint_returns_404_for_missing_node(
    admin_client,
):
    response = admin_client.post("/nodes/999999/health")

    assert response.status_code == 404


def test_metrics_endpoint_returns_404_for_missing_node(
    admin_client,
):
    response = admin_client.get("/nodes/999999/metrics")

    assert response.status_code == 404
