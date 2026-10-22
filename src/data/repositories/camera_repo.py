from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
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
        try:
            self.session.add_all(cameras)
            await self.session.commit()
            for camera in cameras:
                await self.session.refresh(camera)
            return cameras
        except IntegrityError:
            await self.session.rollback()
            raise

    async def get_camera_by_id(self, id: UUID):
        camera = await self.session.get(Camera, id)

        return camera

    async def get_camera_by_camera_id(self, camera_id: str):
        stmt = select(Camera).where(Camera.camera_id == camera_id)
        result = await self.session.execute(stmt)

        camera = result.scalar_one_or_none()

        return camera

    async def get_all_cameras(self):
        stmt = select(Camera)
        result = await self.session.execute(stmt)

        cameras = result.scalars().all()

        return cameras
