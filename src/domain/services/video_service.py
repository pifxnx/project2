from uuid import UUID
from ...schemas.video import VideoResponse
from ...data.repositories.video_repo import VideoRepo
from ...core.storage import MinioStorage
from ..exceptions.video_exceptions import VideoNotFoundException


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
        pass
        ##TODO: Implement upload_video method
