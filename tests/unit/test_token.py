import jwt
import pytest
from datetime import datetime, timedelta, timezone
from src.core.config import settings
from src.core.jwt_token import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)


def test_create_access_token():
    sub = "1"
    token = create_access_token(sub)
    assert token is not None

    payload = decode_access_token(token)
    assert payload["sub"] == sub


def test_expired_access_token():
    payload = {"exp": datetime.now(timezone.utc) - timedelta(seconds=1)}

    token = jwt.encode(payload, settings.token_secret, settings.token_algorithm)

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_refresh_secret_on_access_token():
    sub = "1"
    token = create_access_token(sub)

    with pytest.raises(jwt.InvalidSignatureError):
        decode_refresh_token(token)
