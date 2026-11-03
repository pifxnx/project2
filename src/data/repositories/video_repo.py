from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models.video import Video, VideoStatus
from ..models.user import User
from ...schemas.video import VideoFilters


class VideoRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_video(self, video: Video) -> Video:
        try:
            self.session.add(video)
            await self.session.commit()
            await self.session.refresh(video)
            return video
        except IntegrityError:
            await self.session.rollback()
            raise

    async def get_video_by_id(self, video_id: int) -> Video | None:
        video = await self.session.get(Video, video_id)

        return video

    async def get_videos_by_camera_id(self, camera_id: UUID) -> list[Video]:
        stmt = select(Video).where(
            Video.camera_id == camera_id, Video.status == VideoStatus.success
        )
        result = await self.session.execute(stmt)

        videos = result.scalars().all()

        return list(videos)

    async def delete_video(self, video: Video) -> None:
        await self.session.delete(video)
        await self.session.commit()

    async def get_all_videos(self, filters: VideoFilters):
        stmt = select(Video).options(selectinload(Video.user))

        if filters.user_id is not None:
            stmt = stmt.where(Video.user_id == filters.user_id)
        if filters.author is not None:
            stmt = stmt.join(User, Video.user_id == User.id).where(
                User.fullname.ilike(f"%{filters.author}%")
            )
        if filters.uploaded_from is not None:
            stmt = stmt.where(Video.created_at >= filters.uploaded_from)
        if filters.uploaded_to is not None:
            stmt = stmt.where(Video.created_at <= filters.uploaded_to)
        if filters.duration_from is not None:
            stmt = stmt.where(Video.duration >= filters.duration_from)
        if filters.duration_to is not None:
            stmt = stmt.where(Video.duration <= filters.duration_to)
        if filters.time_of_day is not None:
            stmt = stmt.where(Video.time_of_day == filters.time_of_day)
        if filters.user_id is not None:
            stmt = stmt.where(Video.user_id == filters.user_id)
        if filters.name is not None:
            stmt = stmt.where(Video.name.ilike(f"%{filters.name}%"))
        stmt = (
            stmt.limit(filters.limit)
            .offset(filters.offset)
            .order_by(Video.created_at.desc())
        )

        result = await self.session.execute(stmt)

        videos = result.scalars().all()

        return list(videos)
