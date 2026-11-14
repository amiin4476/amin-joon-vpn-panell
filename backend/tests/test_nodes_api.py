
def create_node_payload(name="Germany Node", host="example.com"):
    return {
        "name": name,
        "host": host,
        "port": 22,
        "agent_port": 443,
        "agent_token": "test-agent-token-12345678901234567890",
        "country": "Germany",
        "city": "Frankfurt",
        "description": "Test server",
    }


def test_nodes_endpoint_rejects_unauthenticated_request(client):
    response = client.get("/nodes/")

    assert response.status_code == 401


def test_nodes_endpoint_rejects_customer(customer_client):
    response = customer_client.get("/nodes/")

    assert response.status_code == 403


def test_admin_can_create_node(admin_client):
    response = admin_client.post(
        "/nodes/",
        json=create_node_payload(),
    )

    assert response.status_code == 201
    data = response.json()

    assert data["name"] == "Germany Node"
    assert data["host"] == "example.com"
    assert data["agent_port"] == 443

    assert "agent_token" not in data
    assert "agent_token_encrypted" not in data


def test_customer_cannot_create_node(customer_client):
    response = customer_client.post(
        "/nodes/",
        json=create_node_payload(),
    )

    assert response.status_code == 403


def test_admin_can_list_nodes(admin_client):
    created = admin_client.post(
        "/nodes/",
        json=create_node_payload(),
    )

    assert created.status_code == 201

    response = admin_client.get("/nodes/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Germany Node"


def test_admin_can_get_node(admin_client):
    created = admin_client.post(
        "/nodes/",
        json=create_node_payload(),
    )

    node_id = created.json()["id"]

    response = admin_client.get(f"/nodes/{node_id}")

    assert response.status_code == 200
    assert response.json()["id"] == node_id


def test_customer_cannot_get_node(customer_client):
    response = customer_client.get("/nodes/1")

    assert response.status_code == 403


def test_admin_can_update_node(admin_client):
    created = admin_client.post(
        "/nodes/",
        json=create_node_payload(),
    )

    node_id = created.json()["id"]

    response = admin_client.put(
        f"/nodes/{node_id}",
        json={
            "name": "Updated Germany",
            "host": "new.example.com",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Germany"
    assert response.json()["host"] == "new.example.com"


def test_customer_cannot_update_node(customer_client):
    response = customer_client.put(
        "/nodes/1",
        json={"name": "Unauthorized Change"},
    )

    assert response.status_code == 403


def test_admin_can_delete_node(admin_client):
    created = admin_client.post(
        "/nodes/",
        json=create_node_payload(),
    )

    node_id = created.json()["id"]

    response = admin_client.delete(f"/nodes/{node_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_customer_cannot_delete_node(customer_client):
    response = customer_client.delete("/nodes/1")

    assert response.status_code == 403


def test_admin_can_view_node_summary(admin_client):
    response = admin_client.get("/nodes/stats/summary")

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_customer_cannot_view_node_summary(customer_client):
    response = customer_client.get("/nodes/stats/summary")

    assert response.status_code == 403
