
import pytest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import User
from app.users import (
    UserCreate,
    UserUpdate,
    UserStatusUpdate,
    list_users,
    create_user,
    update_user,
    update_user_status,
    delete_user,
)
from app import users


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
def admin(db):
    user = User(
        username="admin",
        password_hash="admin-hash",
        full_name="Administrator",
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def customer(db):
    user = User(
        username="customer",
        password_hash="customer-hash",
        full_name="Test Customer",
        role="customer",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_list_users_returns_users(db, admin, customer):
    result = list_users(db, admin)

    assert len(result) == 2
    assert {user.username for user in result} == {
        "admin",
        "customer",
    }


def test_create_user_success(db, admin, monkeypatch):
    monkeypatch.setattr(
        users,
        "get_password_hash",
        lambda password: f"hashed-{password}",
    )

    result = create_user(
        UserCreate(
            username="newuser",
            password="strong-password-123",
            full_name="New User",
            role="reseller",
        ),
        db,
        admin,
    )

    assert result.username == "newuser"
    assert result.full_name == "New User"
    assert result.role == "reseller"
    assert result.is_active is True
    assert result.password_hash == "hashed-strong-password-123"


def test_create_user_rejects_duplicate_username(
    db,
    admin,
    customer,
):
    with pytest.raises(HTTPException) as error:
        create_user(
            UserCreate(
                username="customer",
                password="strong-password-123",
            ),
            db,
            admin,
        )

    assert error.value.status_code == 409


def test_update_user_success(db, admin, customer, monkeypatch):
    monkeypatch.setattr(
        users,
        "get_password_hash",
        lambda password: f"hashed-{password}",
    )

    result = update_user(
        customer.id,
        UserUpdate(
            full_name="Updated Customer",
            password="new-strong-password-123",
            role="reseller",
        ),
        db,
        admin,
    )

    assert result.full_name == "Updated Customer"
    assert result.password_hash == "hashed-new-strong-password-123"
    assert result.role == "reseller"


def test_update_user_rejects_missing_user(db, admin):
    with pytest.raises(HTTPException) as error:
        update_user(
            999,
            UserUpdate(full_name="Missing"),
            db,
            admin,
        )

    assert error.value.status_code == 404


def test_update_user_rejects_admin_account(db, admin):
    with pytest.raises(HTTPException) as error:
        update_user(
            admin.id,
            UserUpdate(full_name="Changed"),
            db,
            admin,
        )

    assert error.value.status_code == 400


def test_update_user_status_deactivates_user(
    db,
    admin,
    customer,
):
    result = update_user_status(
        customer.id,
        UserStatusUpdate(is_active=False),
        db,
        admin,
    )

    assert result.is_active is False


def test_update_user_status_activates_user(
    db,
    admin,
    customer,
):
    customer.is_active = False
    db.commit()

    result = update_user_status(
        customer.id,
        UserStatusUpdate(is_active=True),
        db,
        admin,
    )

    assert result.is_active is True


def test_update_user_status_rejects_deactivating_admin(
    db,
    admin,
):
    with pytest.raises(HTTPException) as error:
        update_user_status(
            admin.id,
            UserStatusUpdate(is_active=False),
            db,
            admin,
        )

    assert error.value.status_code == 400


def test_update_user_status_rejects_missing_user(db, admin):
    with pytest.raises(HTTPException) as error:
        update_user_status(
            999,
            UserStatusUpdate(is_active=False),
            db,
            admin,
        )

    assert error.value.status_code == 404


def test_delete_user_success(db, admin, customer):
    result = delete_user(customer.id, db, admin)

    assert result["status"] == "success"
    assert db.query(User).filter(
        User.id == customer.id
    ).first() is None


def test_delete_user_rejects_admin_account(db, admin):
    with pytest.raises(HTTPException) as error:
        delete_user(admin.id, db, admin)

    assert error.value.status_code == 400


def test_delete_user_rejects_missing_user(db, admin):
    with pytest.raises(HTTPException) as error:
        delete_user(999, db, admin)

    assert error.value.status_code == 404
