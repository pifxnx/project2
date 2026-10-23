import pytest
from unittest.mock import MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from src.core.database import Base
from src.data.models.user import User
from src.data.models.camera import Camera
from src.data.models.video import Video
from src.data.repositories.user_repo import UserRepo
from src.data.repositories.camera_repo import CameraRepo
from src.data.repositories.video_repo import VideoRepo
from src.domain.services.user_service import UserService
from src.domain.services.auth_service import AuthService
from src.domain.services.camera_service import CameraService
from src.domain.services.video_service import VideoService
from src.core.storage import MinioStorage


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5433/test_project2"
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session


@pytest.fixture(autouse=True)
async def truncate_db(db_session):
    await db_session.execute(
        text("TRUNCATE TABLE users, cameras, videos RESTART IDENTITY CASCADE;")
    )
    await db_session.commit()


@pytest.fixture
async def create_user(db_session):
    async def _create_user(user_data):
        user = User(**user_data)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
async def create_camera(db_session):
    async def _create_camera(camera_data):
        camera = Camera(**camera_data)
        db_session.add(camera)
        await db_session.commit()
        await db_session.refresh(camera)
        return camera

    return _create_camera


@pytest.fixture
async def create_video(db_session):
    async def _create_video(video_data):
        video = Video(**video_data)
        db_session.add(video)
        await db_session.commit()
        await db_session.refresh(video)
        return video

    return _create_video


@pytest.fixture
async def get_user_service(db_session):
    user_repo = UserRepo(db_session)
    user_service = UserService(user_repo)
    return user_service


@pytest.fixture
async def get_auth_service(db_session):
    user_repo = UserRepo(db_session)
    auth_service = AuthService(user_repo)
    return auth_service


@pytest.fixture
async def get_camera_service(db_session):
    camera_repo = CameraRepo(db_session)
    camera_service = CameraService(camera_repo)
    return camera_service


@pytest.fixture
def get_video_service_mock_storage(db_session):
    video_repo = VideoRepo(db_session)
    mock_storage = MagicMock(spec=MinioStorage)
    video_service = VideoService(video_repo, mock_storage)
    return video_service
