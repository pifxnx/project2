from pydantic import BaseModel, ConfigDict
from uuid import UUID


class VideoBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class VideoResponse(VideoBase):
    id: int
    camera_id: UUID
    video_url: str
    preview_url: str
