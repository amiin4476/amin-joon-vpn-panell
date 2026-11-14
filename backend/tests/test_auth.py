import jwt
import pytest

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app import auth
from app.models import User


def test_login_success(db, active_user, monkeypatch):
    monkeypatch.setattr(
        auth,
        "create_access_token",
        lambda **kwargs: "test-access-token",
    )

    from app.schemas import LoginRequest

    response = auth.login(
        LoginRequest(
            username=active_user.username,
            password="StrongPassword123!",
        ),
        db,
    )

    assert response.access_token == "test-access-token"


def test_login_rejects_wrong_password(db, active_user):
    from app.schemas import LoginRequest

    with pytest.raises(HTTPException) as exc:
        auth.login(
            LoginRequest(
                username=active_user.username,
                password="WrongPassword123!",
            ),
            db,
        )

    assert exc.value.status_code == 401


def test_login_rejects_inactive_user(db, active_user):
    from app.schemas import LoginRequest

    active_user.is_active = False
    db.commit()

    with pytest.raises(HTTPException) as exc:
        auth.login(
            LoginRequest(
                username=active_user.username,
                password="StrongPassword123!",
            ),
            db,
        )

    assert exc.value.status_code == 403


def test_get_current_user_success(db, active_user, monkeypatch):
    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {
            "sub": str(active_user.id),
            "username": active_user.username,
            "role": active_user.role,
        },
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    result = auth.get_current_user(credentials, db)

    assert result.id == active_user.id
    assert result.username == active_user.username
    assert result.role == active_user.role


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

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="invalid-token",
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(credentials, db)

    assert exc.value.status_code == 401


def test_get_current_user_rejects_missing_username(
    db,
    active_user,
    monkeypatch,
):
    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {"sub": str(active_user.id)},
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(credentials, db)

    assert exc.value.status_code == 401


def test_get_current_user_rejects_wrong_username(
    db,
    active_user,
    monkeypatch,
):
    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {
            "sub": str(active_user.id),
            "username": "another-user",
            "role": active_user.role,
        },
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(credentials, db)

    assert exc.value.status_code == 401


def test_get_current_user_rejects_wrong_role(
    db,
    active_user,
    monkeypatch,
):
    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {
            "sub": str(active_user.id),
            "username": active_user.username,
            "role": "different-role",
        },
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(credentials, db)

    assert exc.value.status_code == 401


def test_get_current_user_rejects_inactive_account(
    db,
    active_user,
    monkeypatch,
):
    active_user.is_active = False
    db.commit()

    monkeypatch.setattr(
        auth,
        "decode_access_token",
        lambda token: {
            "sub": str(active_user.id),
            "username": active_user.username,
            "role": active_user.role,
        },
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(credentials, db)

    assert exc.value.status_code == 401
