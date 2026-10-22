import asyncio
from random import uniform, randint
from ..core.database import sessionmaker
from ..data.repositories.camera_repo import CameraRepo
from ..data.models.camera import Camera

# Москва: lon 37.3–37.9, lat 55.5–55.95
LON_RANGE = (37.3, 37.9)
LAT_RANGE = (55.5, 55.95)


async def add_cameras(cameras: list[Camera]):
    async with sessionmaker() as session:
        repo = CameraRepo(session)
        await repo.create_many(cameras)


def make_cameras(count: int = 50) -> list[Camera]:
    return [
        Camera(
            camera_id=f"cam-{i:05d}",
            camera_name=f"Камера {i}",
            camera_latitude=round(uniform(*LAT_RANGE), 6),
            camera_longitude=round(uniform(*LON_RANGE), 6),
            archive=False,
            azimuth=randint(0, 359),
        )
        for i in range(1, count + 1)
    ]


if __name__ == "__main__":
    asyncio.run(add_cameras(make_cameras()))
