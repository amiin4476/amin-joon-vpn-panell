
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from .config import get_jwt_secret_key


password_hash = PasswordHash.recommended()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_secret_key() -> str:
    return get_jwt_secret_key()


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
