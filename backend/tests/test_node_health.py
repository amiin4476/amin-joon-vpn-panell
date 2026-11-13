
import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.nodes import check_node
from app.node_client import NodeConnectionError


class FakeQuery:
    def __init__(self, node):
        self.node = node

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.node


class FakeDB:
    def __init__(self, node):
        self.node = node
        self.commits = 0

    def query(self, model):
        return FakeQuery(self.node)

    def commit(self):
        self.commits += 1


def make_node(
    is_active=True,
    token="encrypted-test-token",
):
    return SimpleNamespace(
        id=1,
        name="Test Node",
        host="example.com",
        agent_port=9000,
        agent_token_encrypted=token,
        is_active=is_active,
        status="unknown",
    )


def test_health_success_sets_online(monkeypatch):
    node = make_node()
    db = FakeDB(node)

    async def fake_health_check(**kwargs):
        return {"status": "ok"}

    monkeypatch.setattr(
        "app.nodes.check_node_health",
        fake_health_check,
    )

    result = asyncio.run(
        check_node(1, db, object())
    )

    assert result["status"] == "online"
    assert node.status == "online"
    assert db.commits == 1


def test_health_failure_sets_offline(monkeypatch):
    node = make_node()
    db = FakeDB(node)

    async def fake_health_check(**kwargs):
        raise NodeConnectionError("Connection failed")

    monkeypatch.setattr(
        "app.nodes.check_node_health",
        fake_health_check,
    )

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            check_node(1, db, object())
        )

    assert error.value.status_code == 503
    assert node.status == "offline"
    assert db.commits == 1


def test_inactive_node_is_not_checked(monkeypatch):
    node = make_node(is_active=False)
    db = FakeDB(node)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            check_node(1, db, object())
        )

    assert error.value.status_code == 400
    assert db.commits == 0


def test_missing_node_returns_404():
    db = FakeDB(None)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            check_node(1, db, object())
        )

    assert error.value.status_code == 404
