from jwt import InvalidTokenError
from ...data.repositories.user_repo import UserRepo
from ...core.security import verify_password_async
from ...core.jwt_token import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from ..exceptions.auth_exceptions import InvalidCredentialsException


class AuthService:
    def __init__(self, repository: UserRepo):
        self.repository = repository

    async def login_user(self, email, password):
        user = await self.repository.get_user_by_email(email)
        if not user:
            raise InvalidCredentialsException()

        is_valid = await verify_password_async(password, user.hashed_password)

        if not is_valid:
            raise InvalidCredentialsException()

        return create_access_token(sub=str(user.id)), create_refresh_token(
            sub=str(user.id)
        )

    async def get_access_token(self, refresh_token: str):
        try:
            payload = decode_refresh_token(refresh_token)
            user_id = payload.get("sub")
            if user_id is None:
                raise InvalidCredentialsException()

            new_access_token = create_access_token(sub=user_id)

        except InvalidTokenError:
            raise InvalidCredentialsException()

        return new_access_token
