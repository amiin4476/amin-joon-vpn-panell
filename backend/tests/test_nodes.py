from app.nodes import NodeResponse


def test_node_response_does_not_expose_credentials():
    response_fields = set(NodeResponse.model_fields.keys())

    assert "agent_token" not in response_fields
    assert "agent_token_encrypted" not in response_fields
