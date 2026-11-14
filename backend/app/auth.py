import jwt

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .schemas import LoginRequest, TokenResponse, UserResponse
from .security import (
    verify_password,
    create_access_token,
    decode_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

bearer = HTTPBearer(auto_error=False)


def unauthorized(detail: str = "توکن نامعتبر یا منقضی شده است"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.username == data.username
    ).first()

    if not user or not verify_password(
        data.password,
        user.password_hash,
    ):
        raise unauthorized(
            "نام کاربری یا رمز عبور اشتباه است"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری غیرفعال است",
        )

    token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role,
    )

    return TokenResponse(access_token=token)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise unauthorized(
            "ابتدا وارد حساب کاربری شوید"
        )

    try:
        payload = decode_access_token(
            credentials.credentials
        )

        user_id = int(payload["sub"])
        token_username = payload["username"]
        token_role = payload["role"]

        if (
            not isinstance(token_username, str)
            or not token_username
            or not isinstance(token_role, str)
            or not token_role
        ):
            raise ValueError("Invalid token claims")

    except (
        jwt.InvalidTokenError,
        ValueError,
        KeyError,
        TypeError,
    ):
        raise unauthorized()

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user or not user.is_active:
        raise unauthorized(
            "حساب کاربری معتبر نیست"
        )

    # Reject tokens whose identity or role no longer
    # matches the current database record.
    if (
        user.username != token_username
        or user.role != token_role
    ):
        raise unauthorized()

    return user


@router.get("/me", response_model=UserResponse)
def my_account(
    user: User = Depends(get_current_user),
):
    return user
