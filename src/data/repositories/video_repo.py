from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, Select, func
from sqlalchemy.orm import selectinload
from ..models.video import Video, VideoStatus
from ..models.user import User
from ...schemas.video import VideoFilters


sort_column = {
    "created_at": Video.created_at,
    "duration": Video.duration,
    "name": Video.name,
}


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
        video = await self.session.get(
            Video, video_id, options=[selectinload(Video.user)]
        )

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

    async def _apply_filters(self, filters: VideoFilters, stmt: Select):
        if filters.user_id:
            stmt = stmt.where(Video.user_id.in_(filters.user_id))
        if filters.camera_id is not None:
            stmt = stmt.where(Video.camera_id == filters.camera_id)
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
        if filters.time_of_day:
            stmt = stmt.where(Video.time_of_day.in_(filters.time_of_day))
        if filters.name is not None:
            stmt = stmt.where(Video.name.ilike(f"%{filters.name}%"))
        if filters.status:
            stmt = stmt.where(Video.status.in_(filters.status))

        return stmt

    async def get_all_videos(self, filters: VideoFilters):

        stmt = select(Video).options(selectinload(Video.user))
        stmt = await self._apply_filters(filters, stmt)

        column = sort_column[filters.sort]
        direction = column.desc() if filters.order == "desc" else column.asc()
        stmt = (
            stmt.order_by(direction, Video.id)
            .offset(filters.offset)
            .limit(filters.limit)
        )

        result = await self.session.execute(stmt)

        videos = result.scalars().all()

        stmt = select(func.count()).select_from(Video)
        stmt = await self._apply_filters(filters, stmt)

        result = await self.session.execute(stmt)

        total = result.scalar_one()

        return list(videos), total
