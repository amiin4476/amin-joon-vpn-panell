import jwt
import pytest

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app import auth
from app.models import User
from app.schemas import LoginRequest
from app.security import get_password_hash


TEST_PASSWORD = "StrongPassword123!"


def create_test_user(
    db,
    username="testuser",
    role="customer",
    is_active=True,
):
    user = User(
        username=username,
        password_hash=get_password_hash(TEST_PASSWORD),
        full_name="Test User",
        role=role,
        is_active=is_active,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def make_credentials(token="valid-token"):
    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )


def test_login_success(db, monkeypatch):
    user = create_test_user(db)

    monkeypatch.setattr(
        auth,
        "create_access_token",
        lambda **kwargs: "test-access-token",
    )

    response = auth.login(
        LoginRequest(
            username=user.username,
            password=TEST_PASSWORD,
        ),
        db,
    )

    assert response.access_token == "test-access-token"


def test_login_rejects_wrong_password(db):
    user = create_test_user(db)

    with pytest.raises(HTTPException) as exc:
        auth.login(
            LoginRequest(
                username=user.username,
                password="WrongPassword123!",
            ),
            db,
        )

    assert exc.value.status_code == 401


def test_login_rejects_inactive_user(db):
    user = create_test_user(
        db,
        is_active=False,
    )

    with pytest.raises(HTTPException) as exc:
        auth.login(
            LoginRequest(
                username=user.username,
                password=TEST_PASSWORD,
            ),
            db,
        )

    assert exc.value.status_code == 403


def test_get_current_user_success(db, monkeypatch):
    user = create_test_user(db)

    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
        },
    )

    result = auth.get_current_user(
        make_credentials(),
        db,
    )

    assert result.id == user.id
    assert result.username == user.username
    assert result.role == user.role


def test_get_current_user_rejects_missing_credentials(db):
    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(None, db)

    assert exc.value.status_code == 401


def test_get_current_user_rejects_invalid_token(db, monkeypatch):
    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: (_ for _ in ()).throw(
            jwt.InvalidTokenError("Invalid token")
        ),
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(
            make_credentials("invalid-token"),
            db,
        )

    assert exc.value.status_code == 401


def test_get_current_user_rejects_missing_username(
    db,
    monkeypatch,
):
    user = create_test_user(db)

    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {
            "sub": str(user.id),
            "role": user.role,
        },
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(
            make_credentials(),
            db,
        )

    assert exc.value.status_code == 401


def test_get_current_user_rejects_wrong_username(
    db,
    monkeypatch,
):
    user = create_test_user(db)

    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {
            "sub": str(user.id),
            "username": "another-user",
            "role": user.role,
        },
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(
            make_credentials(),
            db,
        )

    assert exc.value.status_code == 401


def test_get_current_user_rejects_wrong_role(
    db,
    monkeypatch,
):
    user = create_test_user(db)

    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {
            "sub": str(user.id),
            "username": user.username,
            "role": "different-role",
        },
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(
            make_credentials(),
            db,
        )

    assert exc.value.status_code == 401


def test_get_current_user_rejects_inactive_account(
    db,
    monkeypatch,
):
    user = create_test_user(db)

    user.is_active = False
    db.commit()

    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
        },
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(
            make_credentials(),
            db,
        )

    assert exc.value.status_code == 401
