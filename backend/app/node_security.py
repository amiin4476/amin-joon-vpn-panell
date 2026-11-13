
from cryptography.fernet import Fernet, InvalidToken

from .config import get_node_encryption_key


def get_node_fernet() -> Fernet:
    key = get_node_encryption_key()

    try:
        return Fernet(key.encode("utf-8"))
    except (ValueError, TypeError):
        raise RuntimeError(
            "NODE_CREDENTIALS_KEY is invalid"
        )


def encrypt_node_token(token: str) -> str:
    if not token:
        raise ValueError("Node token cannot be empty")

    return get_node_fernet().encrypt(
        token.encode("utf-8")
    ).decode("utf-8")


def decrypt_node_token(encrypted_token: str) -> str:
    if not encrypted_token:
        raise ValueError("Encrypted token cannot be empty")

    try:
        return get_node_fernet().decrypt(
            encrypted_token.encode("utf-8")
        ).decode("utf-8")
    except InvalidToken:
        raise ValueError(
            "Node token could not be decrypted"
        )
