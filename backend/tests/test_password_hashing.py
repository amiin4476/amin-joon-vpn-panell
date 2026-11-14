from app.security import get_password_hash, verify_password


def test_password_is_hashed():
    password = "StrongPassword123!"

    hashed_password = get_password_hash(password)

    assert hashed_password != password
    assert len(hashed_password) > 30


def test_password_hash_can_be_verified():
    password = "StrongPassword123!"

    hashed_password = get_password_hash(password)

    assert verify_password(password, hashed_password)


def test_wrong_password_is_rejected():
    hashed_password = get_password_hash("CorrectPassword123!")

    assert not verify_password(
        "WrongPassword123!",
        hashed_password,
    )


def test_same_password_generates_different_hashes():
    password = "StrongPassword123!"

    first_hash = get_password_hash(password)
    second_hash = get_password_hash(password)

    assert first_hash != second_hash
