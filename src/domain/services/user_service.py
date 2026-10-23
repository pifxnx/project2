from sqlalchemy.exc import IntegrityError
from ...core.security import hash_password_async
from ...data.repositories.user_repo import UserRepo
from ...data.models.user import User
from ...schemas.user import UserCreate, UserResponse
from ..exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)


class UserService:
    def __init__(self, repository: UserRepo):
        self.repository = repository

    async def register_user(self, data: UserCreate):
        try:
            pwd = await hash_password_async(data.password)
            user = User(
                email=data.email,
                fullname=data.fullname,
                hashed_password=pwd,
                organization=data.organization,
            )
            user = await self.repository.create_user(user)

        except IntegrityError:
            raise UserAlreadyExistsException()

        return UserResponse.model_validate(user)

    async def get_user_by_id(self, user_id: int):
        user = await self.repository.get_user_by_id(user_id)

        if not user:
            raise UserNotFoundException()

        return UserResponse.model_validate(user)
