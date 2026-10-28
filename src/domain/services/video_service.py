import asyncio
import aiofiles
from uuid import UUID, uuid4
from fastapi import UploadFile
from rq.job import Dependency
from ...schemas.video import VideoResponse
from ...data.repositories.video_repo import VideoRepo
from ...data.models.video import Video
from ...core.storage import MinioStorage
from ..exceptions.video_exceptions import (
    VideoNotFoundException,
    InvalidVideoFormatException,
)
from ...worker.tasks import process_video_task
from ...worker.worker_queue import q
from ...core.config import settings


class VideoService:
    def __init__(self, repository: VideoRepo, storage: MinioStorage):
        self.repository = repository
        self.storage = storage

    def _to_response_list(self, videos: list[Video]):
        return [self._to_response(video) for video in videos]

    def _to_response(self, video: Video):
        return VideoResponse(
            id=video.id,
            camera_id=video.camera_id,
            video_url=self.storage.get_presigned_url(video.video_storage_key),
            preview_url=self.storage.get_presigned_url(video.preview_storage_key),
        )

    async def get_video_by_id(self, video_id: int) -> VideoResponse:
        video = await self.repository.get_video_by_id(video_id)

        if not video:
            raise VideoNotFoundException(video_id)

        res = await asyncio.to_thread(self._to_response, video)

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
        await asyncio.to_thread(self.storage.delete_file, video.video_storage_key)

    async def upload_video(
        self,
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
        prev_job = None
        for file in files:
            file_path = f"{settings.upload_dir}/{uuid4()}"

            key = f"{camera_id}/{uuid4()}"

            video_storage_key = key + ".mp4"
            preview_storage_key = key + ".jpg"

            async with aiofiles.open(file_path, "wb") as out_file:
                while chunk := await file.read(1024 * 1024):
                    await out_file.write(chunk)

            job = q.enqueue(
                process_video_task,
                file_path=file_path,
                camera_id=camera_id,
                video_storage_key=video_storage_key,
                preview_storage_key=preview_storage_key,
                depends_on=Dependency([prev_job], allow_failure=True)
                if prev_job
                else None,
            )

            prev_job = job.id

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
