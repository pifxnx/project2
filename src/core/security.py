import bcrypt


def hash_password(password: str) -> str:
    bytes_password = password.encode("utf-8")

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bytes_password, salt)

    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    bytes_attempt = password.encode("utf-8")
    is_valid = bcrypt.checkpw(bytes_attempt, hashed.encode("utf-8"))

    return is_valid
