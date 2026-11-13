
import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.nodes import node_metrics
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


def make_node(is_active=True):
    return SimpleNamespace(
        id=1,
        name="Test Node",
        host="example.com",
        agent_port=9000,
        agent_token_encrypted="encrypted-test-token",
        is_active=is_active,
        status="unknown",
    )


def test_metrics_success(monkeypatch):
    node = make_node()
    db = FakeDB(node)

    expected_metrics = {
        "cpu_percent": 25.5,
        "memory_percent": 60.0,
        "disk_percent": 40.0,
    }

    async def fake_metrics(**kwargs):
        return expected_metrics

    monkeypatch.setattr(
        "app.nodes.get_node_metrics",
        fake_metrics,
    )

    result = asyncio.run(
        node_metrics(1, db, object())
    )

    assert result["status"] == "online"
    assert result["metrics"] == expected_metrics
    assert node.status == "online"
    assert db.commits == 1


def test_metrics_failure_sets_offline(monkeypatch):
    node = make_node()
    db = FakeDB(node)

    async def fake_metrics(**kwargs):
        raise NodeConnectionError("Connection failed")

    monkeypatch.setattr(
        "app.nodes.get_node_metrics",
        fake_metrics,
    )

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            node_metrics(1, db, object())
        )

    assert error.value.status_code == 503
    assert node.status == "offline"
    assert db.commits == 1


def test_metrics_rejects_inactive_node():
    node = make_node(is_active=False)
    db = FakeDB(node)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            node_metrics(1, db, object())
        )

    assert error.value.status_code == 400
    assert db.commits == 0


def test_metrics_returns_404_for_missing_node():
    db = FakeDB(None)

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            node_metrics(1, db, object())
        )

    assert error.value.status_code == 404
