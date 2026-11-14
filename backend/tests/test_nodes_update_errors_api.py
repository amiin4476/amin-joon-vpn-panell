def create_node(admin_client, name, host):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": name,
            "host": host,
            "port": 22,
            "agent_port": 443,
            "agent_token": "test-agent-token-12345678901234567890",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_admin_cannot_rename_node_to_existing_name(admin_client):
    create_node(
        admin_client,
        "Germany Server",
        "germany.example.com",
    )

    second_id = create_node(
        admin_client,
        "France Server",
        "france.example.com",
    )

    response = admin_client.put(
        f"/nodes/{second_id}",
        json={"name": "Germany Server"},
    )

    assert response.status_code == 409


def test_failed_rename_does_not_change_node_name(admin_client):
    create_node(
        admin_client,
        "Germany Server",
        "germany.example.com",
    )

    second_id = create_node(
        admin_client,
        "France Server",
        "france.example.com",
    )

    admin_client.put(
        f"/nodes/{second_id}",
        json={"name": "Germany Server"},
    )

    response = admin_client.get(f"/nodes/{second_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "France Server"


def test_admin_can_update_node_without_changing_other_fields(admin_client):
    node_id = create_node(
        admin_client,
        "Germany Server",
        "germany.example.com",
    )

    response = admin_client.put(
        f"/nodes/{node_id}",
        json={"name": "Updated Germany"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Germany"
    assert response.json()["host"] == "germany.example.com"
    assert response.json()["port"] == 22
    assert response.json()["agent_port"] == 443
