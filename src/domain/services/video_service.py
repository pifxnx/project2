import asyncio
import aiofiles
from uuid import UUID, uuid4
from fastapi import UploadFile
from redis.exceptions import RedisError
from ...schemas.video import (
    VideoResponse,
    VideoFilters,
    VideoListItem,
    VideoListItemsPage,
    VideoDetail,
)
from ...data.repositories.video_repo import VideoRepo
from ...data.models.video import Video
from ...core.storage import MinioStorage
from ..exceptions.video_exceptions import (
    VideoNotFoundException,
    InvalidVideoFormatException,
)
from ...worker.tasks import enqueue_upload
from ...core.config import settings
from ...core.cache import Cache, geojson_key


class VideoService:
    def __init__(self, repository: VideoRepo, storage: MinioStorage, cache: Cache):
        self.repository = repository
        self.storage = storage
        self.cache = cache

    def _to_response_list(self, videos: list[Video]):
        return [self._to_response(video) for video in videos]

    def _to_response(self, video: Video):
        return VideoResponse(
            id=video.id,
            camera_id=video.camera_id,
            video_url=self.storage.get_presigned_url(video.video_storage_key),
            preview_url=self.storage.get_presigned_url(video.preview_storage_key),
        )

    def _to_response_video_items(self, videos: list[Video]) -> list[VideoListItem]:
        return [
            VideoListItem(
                id=video.id,
                name=video.name,
                duration=video.duration,
                video_resolution=video.video_resolution,
                fps=video.fps,
                time_of_day=video.time_of_day,
                uploaded_at=video.created_at,
                author=video.user.fullname if video.user else None,
                video_url=self.storage.get_presigned_url(video.video_storage_key),
                preview_url=self.storage.get_presigned_url(video.preview_storage_key),
                status=video.status,
                email=video.user.email if video.user else None,
            )
            for video in videos
        ]

    def _to_response_video_detail(self, video: Video) -> VideoDetail:
        return VideoDetail(
            camera_id=video.camera_id,
            id=video.id,
            name=video.name,
            duration=video.duration,
            video_resolution=video.video_resolution,
            fps=video.fps,
            time_of_day=video.time_of_day,
            uploaded_at=video.created_at,
            author=video.user.fullname if video.user else None,
            video_url=self.storage.get_presigned_url(video.video_storage_key),
            preview_url=self.storage.get_presigned_url(video.preview_storage_key),
            status=video.status,
            email=video.user.email if video.user else None,
        )

    async def get_video_by_id(self, video_id: int) -> VideoDetail:
        video = await self.repository.get_video_by_id(video_id)

        if not video:
            raise VideoNotFoundException(video_id)

        res = await asyncio.to_thread(self._to_response_video_detail, video)

        return res

    async def get_videos_by_camera_id(self, camera_id: UUID):
        videos = await self.repository.get_videos_by_camera_id(camera_id)

        res = await asyncio.to_thread(self._to_response_list, videos)

        return res

    async def delete_video(self, video_id: int):
        video = await self.repository.get_video_by_id(video_id)

        if not video:
            raise VideoNotFoundException(video_id)

        await self.repository.delete_video(video)

        try:
            await self.cache.delete(geojson_key)
        except RedisError:
            pass

        await asyncio.to_thread(self.storage.delete_file, video.video_storage_key)

    async def upload_video(
        self,
        user_id: int,
        camera_id: UUID,
        files: list[UploadFile],
    ):
        file_names = []
        for file in files:
            file_name = file.filename
            if not file_name or file_name.split(".")[-1].lower() != "mp4":
                raise InvalidVideoFormatException(file_name)
            file_names.append(file_name)

        jobs_info = []
        for file, name in zip(files, file_names):
            file_path = f"{settings.upload_dir}/{uuid4()}"

            key = f"{camera_id}/{uuid4()}"

            video_storage_key = key + ".mp4"
            preview_storage_key = key + ".jpg"

            async with aiofiles.open(file_path, "wb") as out_file:
                while chunk := await file.read(1024 * 1024):
                    await out_file.write(chunk)

            job = enqueue_upload(
                user_id,
                file_name=name,
                file_path=file_path,
                camera_id=camera_id,
                video_storage_key=video_storage_key,
                preview_storage_key=preview_storage_key,
            )

            jobs_info.append(
                {
                    "job_id": job.id,
                    "video_storage_key": video_storage_key,
                    "preview_storage_key": preview_storage_key,
                }
            )

        return {
            "message": "Video upload initiated",
            "jobs_info": jobs_info,
        }

    async def get_all_videos(self, filters: VideoFilters):
        videos, total = await self.repository.get_all_videos(filters)

        videos = await asyncio.to_thread(self._to_response_video_items, videos)

        return VideoListItemsPage(items=videos, total=total)
