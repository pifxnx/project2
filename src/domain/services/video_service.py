from uuid import UUID, uuid4
from ...schemas.video import VideoResponse
from ...data.repositories.video_repo import VideoRepo
from ...core.storage import MinioStorage
from ..exceptions.video_exceptions import (
    VideoNotFoundException,
    InvalidVideoFormatException,
)
from ...worker.tasks import process_video_task
from ...worker.worker_queue import q


class VideoService:
    def __init__(self, repository: VideoRepo, storage: MinioStorage):
        self.repository = repository
        self.storage = storage

    async def get_video_by_id(self, video_id: int) -> VideoResponse:
        video = await self.repository.get_video_by_id(video_id)

        if not video:
            raise VideoNotFoundException(video_id)

        url = self.storage.get_presigned_url(video.storage_key)

        return VideoResponse(id=video.id, camera_id=video.camera_id, url=url)

    async def get_videos_by_camera_id(self, camera_id: UUID):
        videos = await self.repository.get_videos_by_camera_id(camera_id)

        urls = [self.storage.get_presigned_url(video.storage_key) for video in videos]

        return [
            VideoResponse(id=video.id, camera_id=video.camera_id, url=url)
            for video, url in zip(videos, urls)
        ]

    async def delete_video(self, video_id: int):
        video = await self.repository.get_video_by_id(video_id)

        if not video:
            raise VideoNotFoundException(video_id)

        await self.repository.delete_video(video)
        self.storage.delete_file(video.storage_key)

    async def upload_video(self, camera_id: UUID, file_path: str, file_name: str):
        if file_ext := file_name.split(".")[-1] != "mp4":
            raise InvalidVideoFormatException(file_name)

        storage_key = f"{camera_id}/{uuid4()}.mp4"

        res = q.enqueue(process_video_task, file_path, storage_key)

        return {
            "message": "Video upload initiated",
            "job_id": res.id,
            "storage_key": storage_key,
        }
