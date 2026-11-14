
import pytest

import jwt

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import auth
from app.database import Base
from app.models import User
from app.schemas import LoginRequest


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSession = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)
    session = TestingSession()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def active_user(db):
    user = User(
        username="testuser",
        password_hash="hashed-password",
        full_name="Test User",
        role="customer",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_login_success(db, active_user, monkeypatch):
    monkeypatch.setattr(
        auth,
        "verify_password",
        lambda password, hashed: password == "correct-password",
    )

    monkeypatch.setattr(
        auth,
        "create_access_token",
        lambda **kwargs: "test-access-token",
    )

    result = auth.login(
        LoginRequest(
            username="testuser",
            password="correct-password",
        ),
        db,
    )

    assert result.access_token == "test-access-token"
    assert result.token_type == "bearer"


def test_login_rejects_wrong_password(db, active_user, monkeypatch):
    monkeypatch.setattr(
        auth,
        "verify_password",
        lambda password, hashed: False,
    )

    with pytest.raises(HTTPException) as error:
        auth.login(
            LoginRequest(
                username="testuser",
                password="wrong-password",
            ),
            db,
        )

    assert error.value.status_code == 401


def test_login_rejects_unknown_username(db):
    with pytest.raises(HTTPException) as error:
        auth.login(
            LoginRequest(
                username="unknown",
                password="correct-password",
            ),
            db,
        )

    assert error.value.status_code == 401


def test_login_rejects_inactive_user(db, active_user, monkeypatch):
    active_user.is_active = False
    db.commit()

    monkeypatch.setattr(
        auth,
        "verify_password",
        lambda password, hashed: True,
    )

    with pytest.raises(HTTPException) as error:
        auth.login(
            LoginRequest(
                username="testuser",
                password="correct-password",
            ),
            db,
        )

    assert error.value.status_code == 403


def test_get_current_user_success(db, active_user, monkeypatch):
    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {"sub": str(active_user.id)},
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    result = auth.get_current_user(credentials, db)

    assert result.id == active_user.id
    assert result.username == "testuser"


def test_get_current_user_rejects_missing_credentials(db):
    with pytest.raises(HTTPException) as error:
        auth.get_current_user(None, db)

    assert error.value.status_code == 401


def test_get_current_user_rejects_invalid_token(db, monkeypatch):
    def invalid_token(token):
        raise jwt.InvalidTokenError("Invalid token")

    monkeypatch.setattr(
        auth,
        "decode_access_token",
        invalid_token,
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="invalid-token",
    )

    with pytest.raises(HTTPException) as error:
        auth.get_current_user(credentials, db)

    assert error.value.status_code == 401


def test_get_current_user_rejects_inactive_user(
    db,
    active_user,
    monkeypatch,
):
    active_user.is_active = False
    db.commit()

    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {"sub": str(active_user.id)},
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    with pytest.raises(HTTPException) as error:
        auth.get_current_user(credentials, db)

    assert error.value.status_code == 401


def test_get_current_user_rejects_deleted_user(db, monkeypatch):
    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {"sub": "999"},
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    with pytest.raises(HTTPException) as error:
        auth.get_current_user(credentials, db)

    assert error.value.status_code == 401
