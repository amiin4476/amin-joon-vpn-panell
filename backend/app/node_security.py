
import os

from cryptography.fernet import Fernet, InvalidToken


def get_node_fernet():
    key = os.getenv("NODE_CREDENTIALS_KEY")

    if not key:
        raise RuntimeError(
            "NODE_CREDENTIALS_KEY is not configured"
        )

    try:
        return Fernet(key.encode("utf-8"))
    except (ValueError, TypeError):
        raise RuntimeError(
            "NODE_CREDENTIALS_KEY is invalid"
        )


def encrypt_node_token(token: str) -> str:
    if not token:
        raise ValueError("Node token cannot be empty")

    fernet = get_node_fernet()

    return fernet.encrypt(
        token.encode("utf-8")
    ).decode("utf-8")


def decrypt_node_token(encrypted_token: str) -> str:
    if not encrypted_token:
        raise ValueError("Encrypted token cannot be empty")

    fernet = get_node_fernet()

    try:
        return fernet.decrypt(
            encrypted_token.encode("utf-8")
        ).decode("utf-8")
    except InvalidToken:
        raise ValueError(
            "Node token could not be decrypted"
        )
