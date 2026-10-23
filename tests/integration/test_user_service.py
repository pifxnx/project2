import pytest
from src.schemas.user import UserCreate
from src.domain.exceptions.user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
)


async def test_get_user_by_id_success(get_user_service, create_user):
    user_data = {
        "email": "111@11.com",
        "fullname": "Test User",
        "hashed_password": "hashed_password",
        "organization": "Test",
    }

    user = await create_user(user_data)

    service = get_user_service

    retrieved_user = await service.get_user_by_id(user.id)

    assert retrieved_user.email == user_data["email"]
    assert retrieved_user.fullname == user_data["fullname"]
    assert retrieved_user.organization == user_data["organization"]


async def test_get_user_by_id_not_found(get_user_service):
    service = get_user_service

    with pytest.raises(UserNotFoundException):
        await service.get_user_by_id(9999)


async def test_register_user_success(get_user_service):
    service = get_user_service

    user_data = {
        "email": "a1@a.com",
        "fullname": "Test User",
        "password": "hashed_password",
        "organization": "Test",
    }

    user = await service.register_user(UserCreate(**user_data))

    assert user is not None
    assert user.email == user_data["email"]
    assert user.fullname == user_data["fullname"]
    assert user.organization == user_data["organization"]


async def test_register_user_already_exists(get_user_service, create_user):
    user_data = {
        "email": "a2@a.com",
        "fullname": "Test User",
        "hashed_password": "password",
        "organization": "Test",
    }

    await create_user(user_data)
    service = get_user_service

    del user_data["hashed_password"]
    user_data["password"] = "password"

    with pytest.raises(UserAlreadyExistsException):
        await service.register_user(UserCreate(**user_data))
