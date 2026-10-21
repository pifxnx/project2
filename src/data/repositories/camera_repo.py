from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from ..models.camera import Camera


class CameraRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_camera(self, camera: Camera):
        try:
            self.session.add(camera)
            await self.session.commit()
            await self.session.refresh(camera)
            return camera
        except IntegrityError:
            await self.session.rollback()
            raise

    async def create_many(self, cameras: list[Camera]):
        async with self.session.begin_nested():
            for camera in cameras:
                self.session.add(camera)
                await self.session.flush()

        await self.session.commit()

    async def get_camera_by_id(self, id: UUID):
        camera = await self.session.get(Camera, id)

        return camera
