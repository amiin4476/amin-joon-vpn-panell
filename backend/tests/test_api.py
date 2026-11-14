
def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "AMIN JOON"
    assert response.json()["docs"] == "/docs"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["project"] == "AMIN JOON"


def test_users_endpoint_rejects_unauthenticated_request(client):
    response = client.get("/users/")

    assert response.status_code == 401


def test_users_endpoint_allows_admin(admin_client, admin, customer):
    response = admin_client.get("/users/")

    assert response.status_code == 200

    usernames = {
        user["username"]
        for user in response.json()
    }

    assert usernames == {"testadmin", "testcustomer"}


def test_users_endpoint_rejects_customer(customer_client):
    response = customer_client.get("/users/")

    assert response.status_code == 403


def test_admin_can_create_user(admin_client):
    response = admin_client.post(
        "/users/",
        json={
            "username": "newcustomer",
            "password": "strong-password-123",
            "full_name": "New Customer",
            "role": "customer",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "newcustomer"
    assert response.json()["role"] == "customer"
    assert "password_hash" not in response.json()


def test_customer_cannot_create_user(customer_client):
    response = customer_client.post(
        "/users/",
        json={
            "username": "blockeduser",
            "password": "strong-password-123",
            "role": "customer",
        },
    )

    assert response.status_code == 403
