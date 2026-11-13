import pytest

from cryptography.fernet import Fernet

from app import node_security


@pytest.fixture
def encryption_key(monkeypatch):
    key = Fernet.generate_key().decode("utf-8")

    monkeypatch.setattr(
        node_security,
        "get_node_encryption_key",
        lambda: key,
    )

    return key


def test_encrypt_and_decrypt_node_token(encryption_key):
    original_token = "test-node-token-12345678901234567890"

    encrypted = node_security.encrypt_node_token(
        original_token
    )

    assert encrypted != original_token

    decrypted = node_security.decrypt_node_token(
        encrypted
    )

    assert decrypted == original_token


def test_encrypt_empty_token():
    with pytest.raises(ValueError):
        node_security.encrypt_node_token("")


def test_decrypt_empty_token():
    with pytest.raises(ValueError):
        node_security.decrypt_node_token("")


def test_decrypt_invalid_token(encryption_key):
    with pytest.raises(ValueError):
        node_security.decrypt_node_token(
            "invalid-encrypted-token"
        )


def test_invalid_fernet_key(monkeypatch):
    monkeypatch.setattr(
        node_security,
        "get_node_encryption_key",
        lambda: "!" * 44,
    )

    with pytest.raises(RuntimeError):
        node_security.get_node_fernet()
