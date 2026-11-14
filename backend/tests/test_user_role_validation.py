import pytest
from pydantic import ValidationError

from app.users import UserCreate, UserUpdate


def test_user_create_accepts_reseller_role():
    user = UserCreate(
        username="reseller1",
        password="StrongPassword123!",
        role="reseller",
    )

    assert user.role == "reseller"


def test_user_create_accepts_customer_role():
    user = UserCreate(
        username="customer1",
        password="StrongPassword123!",
        role="customer",
    )

    assert user.role == "customer"


def test_user_create_rejects_invalid_role():
    with pytest.raises(ValidationError):
        UserCreate(
            username="invalid1",
            password="StrongPassword123!",
            role="superadmin",
        )


def test_user_update_rejects_invalid_role():
    with pytest.raises(ValidationError):
        UserUpdate(role="superadmin")


def test_user_create_rejects_short_password():
    with pytest.raises(ValidationError):
        UserCreate(
            username="shortpass",
            password="short",
            role="customer",
        )


def test_user_update_rejects_short_password():
    with pytest.raises(ValidationError):
        UserUpdate(password="short")
