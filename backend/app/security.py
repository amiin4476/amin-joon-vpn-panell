
import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_secret_key() -> str:
    secret_key = os.getenv("APP_SECRET_KEY")

    if not secret_key:
        raise RuntimeError("APP_SECRET_KEY is not configured")

    if len(secret_key.encode("utf-8")) < 32:
        raise RuntimeError(
            "APP_SECRET_KEY must contain at least 32 bytes"
        )

    return secret_key


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(
    user_id: int,
    username: str,
    role: str,
) -> str:
    secret_key = get_secret_key()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    secret_key = get_secret_key()

    return jwt.decode(
        token,
        secret_key,
        algorithms=[ALGORITHM],
    )
