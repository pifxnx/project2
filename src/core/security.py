import bcrypt
import asyncio


def hash_password(password: str) -> str:
    bytes_password = password.encode("utf-8")

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bytes_password, salt)

    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    bytes_attempt = password.encode("utf-8")
    is_valid = bcrypt.checkpw(bytes_attempt, hashed.encode("utf-8"))

    return is_valid


async def hash_password_async(password: str) -> str:
    return await asyncio.to_thread(hash_password, password)


async def verify_password_async(password: str, hashed: str) -> bool:
    return await asyncio.to_thread(verify_password, password, hashed)
