def create_node(
    admin_client,
    name,
    host,
    country,
    city,
    is_active=True,
):
    response = admin_client.post(
        "/nodes/",
        json={
            "name": name,
            "host": host,
            "port": 22,
            "agent_port": 443,
            "agent_token": "test-agent-token-12345678901234567890",
            "country": country,
            "city": city,
        },
    )

    assert response.status_code == 201

    node_id = response.json()["id"]

    if not is_active:
        update = admin_client.put(
            f"/nodes/{node_id}",
            json={"is_active": False},
        )
        assert update.status_code == 200

    return node_id


def test_search_nodes_by_name(admin_client):
    create_node(
        admin_client,
        "Germany Server",
        "germany.example.com",
        "Germany",
        "Frankfurt",
    )

    response = admin_client.get(
        "/nodes/",
        params={"search": "Germany"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Germany Server"


def test_search_nodes_by_host(admin_client):
    create_node(
        admin_client,
        "France Server",
        "192.0.2.10",
        "France",
        "Paris",
    )

    response = admin_client.get(
        "/nodes/",
        params={"search": "192.0.2.10"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_nodes_by_city(admin_client):
    create_node(
        admin_client,
        "Germany Server",
        "germany.example.com",
        "Germany",
        "Frankfurt",
    )

    response = admin_client.get(
        "/nodes/",
        params={"search": "Frankfurt"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_nodes_by_country(admin_client):
    create_node(
        admin_client,
        "France Server",
        "france.example.com",
        "France",
        "Paris",
    )

    response = admin_client.get(
        "/nodes/",
        params={"search": "France"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_nodes_by_country(admin_client):
    create_node(
        admin_client,
        "Germany Server",
        "germany.example.com",
        "Germany",
        "Frankfurt",
    )

    create_node(
        admin_client,
        "France Server",
        "france.example.com",
        "France",
        "Paris",
    )

    response = admin_client.get(
        "/nodes/",
        params={"country": "Germany"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["country"] == "Germany"


def test_filter_active_nodes(admin_client):
    create_node(
        admin_client,
        "Active Server",
        "active.example.com",
        "Germany",
        "Berlin",
    )

    create_node(
        admin_client,
        "Inactive Server",
        "inactive.example.com",
        "France",
        "Paris",
        is_active=False,
    )

    response = admin_client.get(
        "/nodes/",
        params={"is_active": "true"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["is_active"] is True


def test_filter_inactive_nodes(admin_client):
    create_node(
        admin_client,
        "Active Server",
        "active.example.com",
        "Germany",
        "Berlin",
    )

    create_node(
        admin_client,
        "Inactive Server",
        "inactive.example.com",
        "France",
        "Paris",
        is_active=False,
    )

    response = admin_client.get(
        "/nodes/",
        params={"is_active": "false"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["is_active"] is False


def test_nodes_pagination_limit(admin_client):
    for index in range(3):
        create_node(
            admin_client,
            f"Server {index}",
            f"server{index}.example.com",
            "Germany",
            "Berlin",
        )

    response = admin_client.get(
        "/nodes/",
        params={"limit": 2},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_nodes_pagination_offset(admin_client):
    for index in range(3):
        create_node(
            admin_client,
            f"Server {index}",
            f"server{index}.example.com",
            "Germany",
            "Berlin",
        )

    response = admin_client.get(
        "/nodes/",
        params={"offset": 2},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
