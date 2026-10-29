from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import InvalidTokenError
from ..core.jwt_token import decode_access_token
from ..domain.services.auth_service import AuthService
from .database import get_db
from ..data.repositories.user_repo import UserRepo
from ..domain.services.user_service import UserService
from ..domain.exceptions.auth_exceptions import InvalidCredentialsException
from ..domain.exceptions.user_exceptions import UserNotFoundException
from ..data.repositories.camera_repo import CameraRepo
from ..domain.services.camera_service import CameraService
from ..data.repositories.video_repo import VideoRepo
from ..domain.services.video_service import VideoService
from ..core.storage import minio_storage
from ..core.cache import cache


def get_user_service(db: AsyncSession = Depends(get_db)):
    user_repo = UserRepo(db)
    return UserService(user_repo)


def get_auth_service(db: AsyncSession = Depends(get_db)):
    user_repo = UserRepo(db)

    return AuthService(user_repo)


def get_camera_service(db: AsyncSession = Depends(get_db)):
    camera_repo = CameraRepo(db)

    return CameraService(camera_repo, cache)


def get_video_service(db: AsyncSession = Depends(get_db)):
    video_repo = VideoRepo(db)
    return VideoService(video_repo, minio_storage)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    user_service=Depends(get_user_service), token: str = Depends(oauth2_scheme)
):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidCredentialsException()

    except InvalidTokenError:
        raise InvalidCredentialsException()

    try:
        user = await user_service.get_user_by_id(int(user_id))
        return user
    except UserNotFoundException:
        raise InvalidCredentialsException()
