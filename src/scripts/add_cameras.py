import asyncio
from random import uniform
from ..core.database import sessionmaker
from ..data.repositories.camera_repo import CameraRepo
from ..data.models.camera import Camera


async def add_cameras(cameras):
    async with sessionmaker() as session:
        repo = CameraRepo(session)
        await repo.create_many(cameras)


def make_cameras():


cameras = []





if __name__ == "__main__":
    asyncio.run(add_cameras(cameras))


# lon 37.3–37.9, lat 55.5–55.95
