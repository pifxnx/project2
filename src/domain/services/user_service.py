from sqlalchemy.exc import IntegrityError
from ...core.security import hash_password_async
from ...data.repositories.user_repo import UserRepo
from ...data.models.user import User
from ..exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)


class UserService:
    def __init__(self, repository: UserRepo):
        self.repository = repository

    async def register_user(self, email, fullname, password, organization):
        try:
            pwd = await hash_password_async(password)
            user = User(
                email=email,
                fullname=fullname,
                hashed_password=pwd,
                organization=organization,
            )
            user = await self.repository.create_user(user)

        except IntegrityError:
            raise UserAlreadyExistsException()

        return user

    async def get_user_by_id(self, user_id: int):
        user = await self.repository.get_user_by_id(user_id)

        if not user:
            raise UserNotFoundException()

        return user
