def create_node_payload(name="Germany Node"):
    return {
        "name": name,
        "host": "example.com",
        "port": 22,
        "agent_port": 443,
        "agent_token": "test-agent-token-12345678901234567890",
        "country": "Germany",
        "city": "Frankfurt",
        "description": "API error test",
    }


def test_admin_cannot_create_node_with_duplicate_name(admin_client):
    first = admin_client.post(
        "/nodes/",
        json=create_node_payload(),
    )
    assert first.status_code == 201

    second = admin_client.post(
        "/nodes/",
        json=create_node_payload(),
    )

    assert second.status_code == 409


def test_admin_get_missing_node_returns_404(admin_client):
    response = admin_client.get("/nodes/999999")
    assert response.status_code == 404


def test_admin_update_missing_node_returns_404(admin_client):
    response = admin_client.put(
        "/nodes/999999",
        json={"name": "Missing Node"},
    )
    assert response.status_code == 404


def test_admin_delete_missing_node_returns_404(admin_client):
    response = admin_client.delete("/nodes/999999")
    assert response.status_code == 404
