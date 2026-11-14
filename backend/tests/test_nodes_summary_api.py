from app.node_client import NodeConnectionError


def create_node(admin_client, name):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": name,
            "host": f"{name.lower().replace(' ', '-')}.example.com",
            "port": 22,
            "agent_port": 443,
            "agent_token": "test-agent-token-12345678901234567890",
            "country": "Germany",
            "city": "Frankfurt",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_node_summary_counts_active_and_inactive_nodes(admin_client):
    create_node(admin_client, "Active Server")

    inactive_id = create_node(admin_client, "Inactive Server")

    update = admin_client.put(
        f"/nodes/{inactive_id}",
        json={"is_active": False},
    )
    assert update.status_code == 200

    response = admin_client.get("/nodes/stats/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["active"] == 1
    assert data["inactive"] == 1


def test_node_summary_counts_node_statuses(
    admin_client,
    monkeypatch,
):
    online_id = create_node(admin_client, "Online Server")
    offline_id = create_node(admin_client, "Offline Server")
    unknown_id = create_node(admin_client, "Unknown Server")

    async def fake_health_online(**kwargs):
        return {"message": "pong"}

    async def fake_health_offline(**kwargs):
        raise NodeConnectionError("Connection failed")

    monkeypatch.setattr(
        "app.nodes.check_node_health",
        fake_health_online,
    )

    online_response = admin_client.post(
        f"/nodes/{online_id}/health"
    )
    assert online_response.status_code == 200

    monkeypatch.setattr(
        "app.nodes.check_node_health",
        fake_health_offline,
    )

    offline_response = admin_client.post(
        f"/nodes/{offline_id}/health"
    )
    assert offline_response.status_code == 503

    response = admin_client.get("/nodes/stats/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert data["active"] == 3
    assert data["inactive"] == 0
    assert data["statuses"]["online"] == 1
    assert data["statuses"]["offline"] == 1
    assert data["statuses"]["unknown"] == 1
