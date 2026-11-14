def update_node_payload(host):
    return {
        "host": host,
    }


def create_node(admin_client):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": "Update Validation Node",
            "host": "example.com",
            "port": 22,
            "agent_port": 443,
            "agent_token": "test-agent-token-12345678901234567890",
            "country": "Germany",
            "city": "Frankfurt",
            "description": "Validation test",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_admin_can_update_node_host_to_domain(admin_client):
    node_id = create_node(admin_client)

    response = admin_client.put(
        f"/nodes/{node_id}",
        json=update_node_payload("NEW-EXAMPLE.COM"),
    )

    assert response.status_code == 200
    assert response.json()["host"] == "new-example.com"


def test_admin_can_update_node_host_to_ipv4(admin_client):
    node_id = create_node(admin_client)

    response = admin_client.put(
        f"/nodes/{node_id}",
        json=update_node_payload("192.0.2.20"),
    )

    assert response.status_code == 200
    assert response.json()["host"] == "192.0.2.20"


def test_admin_can_update_node_host_to_ipv6(admin_client):
    node_id = create_node(admin_client)

    response = admin_client.put(
        f"/nodes/{node_id}",
        json=update_node_payload("[2001:db8::2]"),
    )

    assert response.status_code == 200
    assert response.json()["host"] == "2001:db8::2"


def test_admin_cannot_update_node_host_with_url(admin_client):
    node_id = create_node(admin_client)

    response = admin_client.put(
        f"/nodes/{node_id}",
        json=update_node_payload("https://example.com"),
    )

    assert response.status_code == 422


def test_admin_cannot_update_node_host_with_invalid_ipv4(admin_client):
    node_id = create_node(admin_client)

    response = admin_client.put(
        f"/nodes/{node_id}",
        json=update_node_payload("256.256.256.256"),
    )

    assert response.status_code == 422


def test_admin_cannot_update_node_host_with_invalid_domain(admin_client):
    node_id = create_node(admin_client)

    response = admin_client.put(
        f"/nodes/{node_id}",
        json=update_node_payload("invalid_domain.com"),
    )

    assert response.status_code == 422
