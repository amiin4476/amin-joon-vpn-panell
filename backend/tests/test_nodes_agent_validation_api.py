def create_node(admin_client):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": "Agent Validation Node",
            "host": "example.com",
            "port": 22,
            "agent_port": 443,
            "agent_token": "test-agent-token-12345678901234567890",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_health_rejects_inactive_node(admin_client, monkeypatch):
    node_id = create_node(admin_client)

    update = admin_client.put(
        f"/nodes/{node_id}",
        json={"is_active": False},
    )
    assert update.status_code == 200

    async def fake_health(**kwargs):
        raise AssertionError("Agent must not be contacted")

    monkeypatch.setattr(
        "app.nodes.check_node_health",
        fake_health,
    )

    response = admin_client.post(
        f"/nodes/{node_id}/health"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "این سرور غیرفعال است"


def test_metrics_rejects_inactive_node(admin_client, monkeypatch):
    node_id = create_node(admin_client)

    update = admin_client.put(
        f"/nodes/{node_id}",
        json={"is_active": False},
    )
    assert update.status_code == 200

    async def fake_metrics(**kwargs):
        raise AssertionError("Agent must not be contacted")

    monkeypatch.setattr(
        "app.nodes.get_node_metrics",
        fake_metrics,
    )

    response = admin_client.get(
        f"/nodes/{node_id}/metrics"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "این سرور غیرفعال است"


def test_health_rejects_node_without_agent_token(
    admin_client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.nodes.encrypt_node_token",
        lambda token: None,
    )

    response = admin_client.post(
        "/nodes/",
        json={
            "name": "No Token Health Node",
            "host": "example.com",
            "port": 22,
            "agent_port": 443,
            "agent_token": "test-agent-token-12345678901234567890",
        },
    )

    assert response.status_code == 201
    node_id = response.json()["id"]

    async def fake_health(**kwargs):
        raise AssertionError("Agent must not be contacted")

    monkeypatch.setattr(
        "app.nodes.check_node_health",
        fake_health,
    )

    response = admin_client.post(
        f"/nodes/{node_id}/health"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "توکن Agent برای این سرور ثبت نشده است"


def test_metrics_rejects_node_without_agent_token(
    admin_client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.nodes.encrypt_node_token",
        lambda token: None,
    )

    response = admin_client.post(
        "/nodes/",
        json={
            "name": "No Token Metrics Node",
            "host": "example.com",
            "port": 22,
            "agent_port": 443,
            "agent_token": "test-agent-token-12345678901234567890",
        },
    )

    assert response.status_code == 201
    node_id = response.json()["id"]

    async def fake_metrics(**kwargs):
        raise AssertionError("Agent must not be contacted")

    monkeypatch.setattr(
        "app.nodes.get_node_metrics",
        fake_metrics,
    )

    response = admin_client.get(
        f"/nodes/{node_id}/metrics"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "توکن Agent برای این سرور ثبت نشده است"
