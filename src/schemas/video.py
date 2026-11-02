from pydantic import BaseModel, ConfigDict, model_validator, Field
from uuid import UUID
from datetime import datetime
from ..data.models.video import TimeOfDay


class VideoBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class VideoResponse(VideoBase):
    id: int
    camera_id: UUID
    video_url: str
    preview_url: str


class VideoFilters(BaseModel):
    uploaded_from: datetime | None = None
    uploaded_to: datetime | None = None
    duration_from: float | None = None
    duration_to: float | None = None
    time_of_day: TimeOfDay | None = None
    user_id: int | None = None
    author: str | None = None
    name: str | None = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.uploaded_from is not None and self.uploaded_to is not None:
            if self.uploaded_from > self.uploaded_to:
                raise ValueError(
                    "uploaded_from must be less than or equal to uploaded_to"
                )
        return self

    @model_validator(mode="after")
    def validate_duration(self):
        if self.duration_from is not None and self.duration_to is not None:
            if self.duration_from > self.duration_to:
                raise ValueError(
                    "duration_from must be less than or equal to duration_to"
                )
        return self


class VideoListItem(BaseModel):
    id: int
    name: str
    duration: float | None
    video_resolution: str | None
    fps: float | None
    time_of_day: TimeOfDay | None
    uploaded_at: datetime
    author: str | None
    video_url: str
    preview_url: str
