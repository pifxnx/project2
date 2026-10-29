from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func
from ..models.camera import Camera
from ..models.video import Video, VideoStatus
from ...schemas.camera import CameraFilters


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

    async def get_all_cameras(self, filters: CameraFilters):
        stmt = select(Camera)

        if filters.min_videos_count is not None or filters.max_videos_count is not None:
            video_count = func.count(Video.id)
            stmt = stmt.outerjoin(
                Video,
                (Video.camera_id == Camera.id) & (Video.status == VideoStatus.success),
            ).group_by(Camera.id)
            if filters.min_videos_count is not None:
                stmt = stmt.having(video_count >= filters.min_videos_count)
            if filters.max_videos_count is not None:
                stmt = stmt.having(video_count <= filters.max_videos_count)

        if filters.camera_name is not None:
            stmt = stmt.where(Camera.camera_name.ilike(f"%{filters.camera_name}%"))
        if filters.camera_model is not None:
            stmt = stmt.where(Camera.model == filters.camera_model)
        if filters.camera_type is not None:
            stmt = stmt.where(Camera.camera_type == filters.camera_type)
        if filters.camera_class is not None:
            stmt = stmt.where(Camera.camera_class == filters.camera_class)

        result = await self.session.execute(stmt)

        cameras = result.scalars().all()

        return cameras

    async def get_cameras_has_videos(self):
        has_video = (
            select(Video.id)
            .where(Video.camera_id == Camera.id, Video.status == VideoStatus.success)
            .exists()
        )

        stmt = select(Camera, has_video.label("has_video"))

        res = await self.session.execute(stmt)
        cameras = res.all()

        return [(camera, has_video) for camera, has_video in cameras]
