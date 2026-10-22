from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from ..models.video import Video


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

    async def get_video_by_camera_id(self, camera_id: UUID) -> list[Video]:
        stmt = select(Video).where(Video.camera_id == camera_id)
        result = await self.session.execute(stmt)

        videos = result.scalars().all()

        return list(videos)

    async def delete_video(self, video_id: int) -> None:
        video = await self.get_video_by_id(video_id)
        if video:
            await self.session.delete(video)
            await self.session.commit()

        else:
            raise ValueError()
