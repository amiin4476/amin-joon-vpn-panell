
import pytest

from cryptography.fernet import Fernet
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Node
from app.nodes import (
    NodeCreate,
    NodeUpdate,
    NodeResponse,
    create_node,
    list_nodes,
    get_node,
    update_node,
    delete_node,
)
from app import node_security


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    session = testing_session_local()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def encryption(monkeypatch):
    fernet = Fernet(Fernet.generate_key())

    monkeypatch.setattr(
        node_security,
        "get_node_fernet",
        lambda: fernet,
    )

    return fernet


@pytest.fixture
def admin():
    return object()


def make_node_data(
    name="Germany Node",
    host="example.com",
    token="test-agent-token-12345678901234567890",
):
    return NodeCreate(
        name=name,
        host=host,
        agent_token=token,
    )


def test_create_node_success(db, admin, encryption):
    data = make_node_data()

    result = create_node(data, db, admin)

    assert result.id is not None
    assert result.name == "Germany Node"
    assert result.host == "example.com"
    assert result.agent_port == 443

    saved_node = db.query(Node).filter(
        Node.id == result.id
    ).first()

    assert saved_node is not None
    assert saved_node.agent_token_encrypted != data.agent_token

    decrypted = encryption.decrypt(
        saved_node.agent_token_encrypted.encode("utf-8")
    ).decode("utf-8")

    assert decrypted == data.agent_token


def test_create_node_rejects_duplicate_name(db, admin, encryption):
    data = make_node_data()

    create_node(data, db, admin)

    with pytest.raises(HTTPException) as error:
        create_node(data, db, admin)

    assert error.value.status_code == 409


def test_list_nodes_returns_saved_nodes(db, admin, encryption):
    create_node(
        make_node_data(
            name="Germany Node",
            host="germany.example.com",
        ),
        db,
        admin,
    )

    create_node(
        make_node_data(
            name="France Node",
            host="france.example.com",
        ),
        db,
        admin,
    )

    result = list_nodes(
        search=None,
        country=None,
        is_active=None,
        limit=50,
        offset=0,
        db=db,
        admin=admin,
    )

    assert len(result) == 2
    assert {node.name for node in result} == {
        "Germany Node",
        "France Node",
    }


def test_get_node_returns_existing_node(db, admin, encryption):
    created = create_node(
        make_node_data(),
        db,
        admin,
    )

    result = get_node(created.id, db, admin)

    assert result.id == created.id
    assert result.name == "Germany Node"


def test_get_node_returns_404_for_missing_node(db, admin):
    with pytest.raises(HTTPException) as error:
        get_node(999, db, admin)

    assert error.value.status_code == 404


def test_update_node_changes_host_and_name(db, admin, encryption):
    created = create_node(
        make_node_data(),
        db,
        admin,
    )

    update_data = NodeUpdate(
        name="Updated Germany",
        host="NEW.EXAMPLE.COM",
    )

    result = update_node(
        created.id,
        update_data,
        db,
        admin,
    )

    assert result.name == "Updated Germany"
    assert result.host == "new.example.com"


def test_update_node_rejects_duplicate_name(db, admin, encryption):
    first = create_node(
        make_node_data(name="Germany Node"),
        db,
        admin,
    )

    create_node(
        make_node_data(
            name="France Node",
            host="france.example.com",
        ),
        db,
        admin,
    )

    with pytest.raises(HTTPException) as error:
        update_node(
            first.id,
            NodeUpdate(name="France Node"),
            db,
            admin,
        )

    assert error.value.status_code == 409


def test_update_node_reencrypts_agent_token(db, admin, encryption):
    created = create_node(
        make_node_data(),
        db,
        admin,
    )

    new_token = "new-agent-token-12345678901234567890"

    update_node(
        created.id,
        NodeUpdate(agent_token=new_token),
        db,
        admin,
    )

    saved_node = db.query(Node).filter(
        Node.id == created.id
    ).first()

    decrypted = encryption.decrypt(
        saved_node.agent_token_encrypted.encode("utf-8")
    ).decode("utf-8")

    assert decrypted == new_token


def test_update_node_returns_404_for_missing_node(db, admin):
    with pytest.raises(HTTPException) as error:
        update_node(
            999,
            NodeUpdate(name="Updated Node"),
            db,
            admin,
        )

    assert error.value.status_code == 404


def test_delete_node_success(db, admin, encryption):
    created = create_node(
        make_node_data(),
        db,
        admin,
    )

    result = delete_node(created.id, db, admin)

    assert result["status"] == "success"

    deleted_node = db.query(Node).filter(
        Node.id == created.id
    ).first()

    assert deleted_node is None


def test_delete_node_returns_404_for_missing_node(db, admin):
    with pytest.raises(HTTPException) as error:
        delete_node(999, db, admin)

    assert error.value.status_code == 404


def test_node_response_does_not_expose_credentials(db, admin, encryption):
    created = create_node(
        make_node_data(),
        db,
        admin,
    )

    response = NodeResponse.model_validate(created)
    response_data = response.model_dump()

    assert "agent_token" not in response_data
    assert "agent_token_encrypted" not in response_data
