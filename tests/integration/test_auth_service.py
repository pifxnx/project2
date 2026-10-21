import pytest
from src.core.security import hash_password_async
from src.domain.exceptions.auth_exceptions import InvalidCredentialsException


async def test_login_user_success(get_auth_service, create_user):
    password = "passowrd"
    user_data = {
        "email": "2",
        "fullname": "Test User",
        "hashed_password": await hash_password_async(password),
        "organization": "Test",
    }

    await create_user(user_data)
    service = get_auth_service

    access_token, refresh_token = await service.login_user(user_data["email"], password)

    assert access_token is not None
    assert refresh_token is not None


async def test_login_user_invalid_credentials(get_auth_service):
    service = get_auth_service

    with pytest.raises(InvalidCredentialsException):
        await service.login_user("invalid_email", "invalid_password")


async def test_login_existing_user_wrong_password(get_auth_service, create_user):
    password = "correct_password"
    user_data = {
        "email": "3",
        "fullname": "Test User",
        "hashed_password": await hash_password_async(password),
        "organization": "Test",
    }

    await create_user(user_data)
    service = get_auth_service

    with pytest.raises(InvalidCredentialsException):
        await service.login_user(user_data["email"], "wrong_password")


async def test_get_new_access_token_success(get_auth_service, create_user):
    password = "password"
    user_data = {
        "email": "4",
        "fullname": "Test User",
        "hashed_password": await hash_password_async(password),
        "organization": "Test",
    }

    await create_user(user_data)
    service = get_auth_service

    _, refresh_token = await service.login_user(user_data["email"], password)

    new_access_token = await service.get_access_token(refresh_token)

    assert new_access_token is not None


async def test_get_new_access_token_invalid_refresh(get_auth_service):
    service = get_auth_service

    with pytest.raises(InvalidCredentialsException):
        await service.get_access_token("invalid_refresh_token")
