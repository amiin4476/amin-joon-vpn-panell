from app.node_security import decrypt_node_token


OLD_TOKEN = "test-agent-token-12345678901234567890"
NEW_TOKEN = "new-agent-token-09876543210987654321"


def create_node(admin_client):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": "Token Rotation Node",
            "host": "example.com",
            "port": 22,
            "agent_port": 443,
            "agent_token": OLD_TOKEN,
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_updating_agent_token_replaces_old_token(
    admin_client,
    monkeypatch,
):
    node_id = create_node(admin_client)

    update = admin_client.put(
        f"/nodes/{node_id}",
        json={"agent_token": NEW_TOKEN},
    )

    assert update.status_code == 200
    assert "agent_token" not in update.json()
    assert "agent_token_encrypted" not in update.json()

    captured_tokens = []

    async def fake_health(**kwargs):
        captured_tokens.append(
            decrypt_node_token(kwargs["encrypted_token"])
        )
        return {"message": "pong"}

    monkeypatch.setattr(
        "app.nodes.check_node_health",
        fake_health,
    )

    response = admin_client.post(
        f"/nodes/{node_id}/health"
    )

    assert response.status_code == 200
    assert captured_tokens == [NEW_TOKEN]
    assert OLD_TOKEN not in str(response.json())
    assert NEW_TOKEN not in str(response.json())


def test_updating_agent_token_with_null_keeps_existing_token(
    admin_client,
    monkeypatch,
):
    node_id = create_node(admin_client)

    update = admin_client.put(
        f"/nodes/{node_id}",
        json={"agent_token": None},
    )

    assert update.status_code == 200

    captured_tokens = []

    async def fake_health(**kwargs):
        captured_tokens.append(
            decrypt_node_token(kwargs["encrypted_token"])
        )
        return {"message": "pong"}

    monkeypatch.setattr(
        "app.nodes.check_node_health",
        fake_health,
    )

    response = admin_client.post(
        f"/nodes/{node_id}/health"
    )

    assert response.status_code == 200
    assert captured_tokens == [OLD_TOKEN]


def test_updating_agent_token_with_short_value_is_rejected(
    admin_client,
):
    node_id = create_node(admin_client)

    response = admin_client.put(
        f"/nodes/{node_id}",
        json={"agent_token": "short"},
    )

    assert response.status_code == 422
