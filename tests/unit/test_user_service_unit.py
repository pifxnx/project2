import pytest
from unittest.mock import AsyncMock
from sqlalchemy.exc import IntegrityError
from src.domain.services.user_service import UserService
from src.data.models.user import User
from src.schemas.user import UserCreate
from src.domain.exceptions.user_exceptions import UserAlreadyExistsException


async def test_create_user():

    repo = AsyncMock()
    repo.create_user.return_value = User(
        id=1, email="a@a.com", fullname="1", hashed_password="1", organization="1"
    )

    service = UserService(repo)

    user = await service.register_user(
        UserCreate(email="a@a.com", fullname="1", password="1", organization="1")
    )
    saved_user = repo.create_user.await_args[0][0]
    assert user.id == 1
    assert user.email == "a@a.com"
    assert user.fullname == "1"
    assert saved_user.hashed_password != "1"
    assert user.organization == "1"
    repo.create_user.assert_awaited_once()


async def test_create_user_already_exists():
    repo = AsyncMock()
    repo.create_user.side_effect = IntegrityError(
        None, None, Exception("duplicate key value violates unique constraint")
    )

    service = UserService(repo)

    with pytest.raises(UserAlreadyExistsException):
        await service.register_user(
            UserCreate(email="a@a.com", fullname="1", password="1", organization="1")
        )


async def test_get_user_by_id():
    repo = AsyncMock()
    repo.get_user_by_id.return_value = User(
        id=1, email="1", fullname="1", hashed_password="1", organization="1"
    )

    service = UserService(repo)

    user = await service.get_user_by_id(1)

    assert user.id == 1
    assert user.email == "1"
    assert user.fullname == "1"
    assert user.hashed_password == "1"
    assert user.organization == "1"
    repo.get_user_by_id.assert_awaited_once_with(1)
