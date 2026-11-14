def test_customer_cannot_check_node_health(customer_client):
    response = customer_client.post("/nodes/1/health")
    assert response.status_code == 403


def test_customer_cannot_read_node_metrics(customer_client):
    response = customer_client.get("/nodes/1/metrics")
    assert response.status_code == 403


def test_unauthenticated_user_cannot_check_node_health(client):
    response = client.post("/nodes/1/health")
    assert response.status_code == 401


def test_unauthenticated_user_cannot_read_node_metrics(client):
    response = client.get("/nodes/1/metrics")
    assert response.status_code == 401
