def create_node(admin_client):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": "Credential Security Node",
            "host": "example.com",
            "port": 22,
            "agent_port": 443,
            "agent_token": "test-agent-token-12345678901234567890",
            "country": "Germany",
            "city": "Frankfurt",
            "description": "Credential security test",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def assert_credentials_are_hidden(data):
    assert "agent_token" not in data
    assert "agent_token_encrypted" not in data


def test_create_node_response_hides_credentials(admin_client):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": "Create Security Node",
            "host": "example.com",
            "port": 22,
            "agent_port": 443,
            "agent_token": "test-agent-token-12345678901234567890",
        },
    )

    assert response.status_code == 201
    assert_credentials_are_hidden(response.json())


def test_list_nodes_response_hides_credentials(admin_client):
    create_node(admin_client)

    response = admin_client.get("/nodes/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert_credentials_are_hidden(response.json()[0])


def test_get_node_response_hides_credentials(admin_client):
    node_id = create_node(admin_client)

    response = admin_client.get(f"/nodes/{node_id}")

    assert response.status_code == 200
    assert_credentials_are_hidden(response.json())


def test_update_node_response_hides_credentials(admin_client):
    node_id = create_node(admin_client)

    response = admin_client.put(
        f"/nodes/{node_id}",
        json={"name": "Updated Security Node"},
    )

    assert response.status_code == 200
    assert_credentials_are_hidden(response.json())
