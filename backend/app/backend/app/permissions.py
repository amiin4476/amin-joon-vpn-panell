
from fastapi import Depends, HTTPException, status

from .auth import get_current_user
from .models import User


def require_roles(*allowed_roles: str):
    """
    بررسی نقش کاربر واردشده.
    فقط نقش‌های مجاز اجازه دسترسی دارند.
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="شما اجازه دسترسی به این بخش را ندارید",
            )

        return current_user

    return role_checker


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """دسترسی فقط برای مدیر اصلی."""

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="این بخش فقط برای مدیر اصلی قابل دسترسی است",
        )

    return current_user


def require_admin_or_reseller(
    current_user: User = Depends(get_current_user),
) -> User:
    """دسترسی برای مدیر اصلی و نماینده."""

    if current_user.role not in ("admin", "reseller"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما اجازه دسترسی به این بخش را ندارید",
        )

    return current_user
