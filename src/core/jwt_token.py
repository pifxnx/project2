import jwt
from datetime import datetime, timedelta, timezone
from .config import settings


def create_access_token(
    sub: str,
):
    secret_key = settings.token_secret
    algorithm = settings.token_algorithm
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(seconds=settings.token_exp),
        "sub": sub,
    }
    token = jwt.encode(payload, secret_key, algorithm)

    return token


def create_refresh_token(
    sub: str,
) -> str:
    secret_key = settings.refresh_secret
    algorithm = settings.token_algorithm
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=settings.refresh_exp),
        "sub": sub,
    }
    token = jwt.encode(payload, secret_key, algorithm)

    return token


def decode_access_token(
    token: str,
):
    secret_key = settings.token_secret
    algorithm = settings.token_algorithm
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])

    return payload


def decode_refresh_token(
    token: str,
):
    secret_key = settings.refresh_secret
    algorithm = settings.token_algorithm
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])

    return payload
