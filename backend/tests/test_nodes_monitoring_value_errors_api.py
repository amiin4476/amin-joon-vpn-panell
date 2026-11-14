def create_node(admin_client, name):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": name,
            "host": "example.com",
            "port": 22,
            "agent_port": 443,
            "agent_token": "test-agent-token-12345678901234567890",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_health_value_error_returns_503_and_sets_offline(
    admin_client,
    monkeypatch,
):
    node_id = create_node(admin_client, "Health Value Error Node")

    async def fake_health(**kwargs):
        raise ValueError("Invalid response")

    monkeypatch.setattr(
        "app.nodes.check_node_health",
        fake_health,
    )

    response = admin_client.post(
        f"/nodes/{node_id}/health"
    )

    assert response.status_code == 503

    summary = admin_client.get("/nodes/stats/summary")

    assert summary.status_code == 200
    assert summary.json()["statuses"]["offline"] == 1


def test_metrics_value_error_returns_503_and_sets_offline(
    admin_client,
    monkeypatch,
):
    node_id = create_node(admin_client, "Metrics Value Error Node")

    async def fake_metrics(**kwargs):
        raise ValueError("Invalid metrics response")

    monkeypatch.setattr(
        "app.nodes.get_node_metrics",
        fake_metrics,
    )

    response = admin_client.get(
        f"/nodes/{node_id}/metrics"
    )

    assert response.status_code == 503

    summary = admin_client.get("/nodes/stats/summary")

    assert summary.status_code == 200
    assert summary.json()["statuses"]["offline"] == 1
