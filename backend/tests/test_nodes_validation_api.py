def create_node_payload(host):
    return {
        "name": "Validation Test Node",
        "host": host,
        "port": 22,
        "agent_port": 443,
        "agent_token": "test-agent-token-12345678901234567890",
        "country": "Germany",
        "city": "Frankfurt",
        "description": "Validation test",
    }


def test_admin_can_create_node_with_domain(admin_client):
    response = admin_client.post(
        "/nodes/",
        json=create_node_payload("EXAMPLE.COM"),
    )

    assert response.status_code == 201
    assert response.json()["host"] == "example.com"


def test_admin_can_create_node_with_ipv4(admin_client):
    response = admin_client.post(
        "/nodes/",
        json=create_node_payload("192.0.2.10"),
    )

    assert response.status_code == 201
    assert response.json()["host"] == "192.0.2.10"


def test_admin_can_create_node_with_ipv6(admin_client):
    response = admin_client.post(
        "/nodes/",
        json=create_node_payload("[2001:db8::1]"),
    )

    assert response.status_code == 201
    assert response.json()["host"] == "2001:db8::1"


def test_admin_cannot_create_node_with_url(admin_client):
    response = admin_client.post(
        "/nodes/",
        json=create_node_payload("https://example.com"),
    )

    assert response.status_code == 422


def test_admin_cannot_create_node_with_invalid_ipv4(admin_client):
    response = admin_client.post(
        "/nodes/",
        json=create_node_payload("256.256.256.256"),
    )

    assert response.status_code == 422


def test_admin_cannot_create_node_with_invalid_domain(admin_client):
    response = admin_client.post(
        "/nodes/",
        json=create_node_payload("invalid_domain.com"),
    )

    assert response.status_code == 422
