def test_nodes_rejects_zero_limit(admin_client):
    response = admin_client.get(
        "/nodes/",
        params={"limit": 0},
    )
    assert response.status_code == 422


def test_nodes_rejects_limit_above_maximum(admin_client):
    response = admin_client.get(
        "/nodes/",
        params={"limit": 101},
    )
    assert response.status_code == 422


def test_nodes_rejects_negative_offset(admin_client):
    response = admin_client.get(
        "/nodes/",
        params={"offset": -1},
    )
    assert response.status_code == 422


def test_nodes_rejects_empty_search(admin_client):
    response = admin_client.get(
        "/nodes/",
        params={"search": ""},
    )
    assert response.status_code == 422


def test_nodes_rejects_search_longer_than_maximum(admin_client):
    response = admin_client.get(
        "/nodes/",
        params={"search": "a" * 101},
    )
    assert response.status_code == 422


def test_nodes_rejects_country_longer_than_maximum(admin_client):
    response = admin_client.get(
        "/nodes/",
        params={"country": "a" * 101},
    )
    assert response.status_code == 422


def test_create_node_rejects_invalid_ssh_port(admin_client):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": "Invalid Port Node",
            "host": "example.com",
            "port": 65536,
            "agent_port": 443,
            "agent_token": "test-agent-token-12345678901234567890",
        },
    )
    assert response.status_code == 422


def test_create_node_rejects_invalid_agent_port(admin_client):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": "Invalid Agent Port Node",
            "host": "example.com",
            "port": 22,
            "agent_port": 0,
            "agent_token": "test-agent-token-12345678901234567890",
        },
    )
    assert response.status_code == 422


def test_create_node_rejects_short_agent_token(admin_client):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": "Short Token Node",
            "host": "example.com",
            "port": 22,
            "agent_port": 443,
            "agent_token": "short",
        },
    )
    assert response.status_code == 422
