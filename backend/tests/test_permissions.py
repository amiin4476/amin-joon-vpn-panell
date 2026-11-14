
import pytest

from fastapi import HTTPException

from app.models import User
from app.permissions import (
    require_roles,
    require_admin,
    require_admin_or_reseller,
)


def make_user(role):
    return User(
        username=f"{role}_user",
        password_hash="test-hash",
        role=role,
        is_active=True,
    )


def test_require_roles_allows_admin():
    user = make_user("admin")

    checker = require_roles("admin", "reseller")

    assert checker(user) is user


def test_require_roles_allows_reseller():
    user = make_user("reseller")

    checker = require_roles("admin", "reseller")

    assert checker(user) is user


def test_require_roles_rejects_customer():
    user = make_user("customer")

    checker = require_roles("admin", "reseller")

    with pytest.raises(HTTPException) as error:
        checker(user)

    assert error.value.status_code == 403


def test_require_admin_allows_admin():
    user = make_user("admin")

    assert require_admin(user) is user


@pytest.mark.parametrize(
    "role",
    ["customer", "reseller"],
)
def test_require_admin_rejects_non_admin(role):
    user = make_user(role)

    with pytest.raises(HTTPException) as error:
        require_admin(user)

    assert error.value.status_code == 403


def test_require_admin_or_reseller_allows_admin():
    user = make_user("admin")

    assert require_admin_or_reseller(user) is user


def test_require_admin_or_reseller_allows_reseller():
    user = make_user("reseller")

    assert require_admin_or_reseller(user) is user


def test_require_admin_or_reseller_rejects_customer():
    user = make_user("customer")

    with pytest.raises(HTTPException) as error:
        require_admin_or_reseller(user)

    assert error.value.status_code == 403
