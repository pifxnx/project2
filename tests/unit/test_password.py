from src.core.security import hash_password, verify_password


def test_hash_password():
    password = "password"
    hashed = hash_password(password)
    assert hashed != password

    veryfy = verify_password(password, hashed)
    assert veryfy is True
