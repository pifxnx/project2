import enum
from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime
from datetime import datetime, timezone
from ...core.database import Base


if TYPE_CHECKING:
    from .camera import Camera
    from .user import User


class VideoStatus(enum.Enum):
    processing = "processing"
    success = "success"
    failed = "failed"


class TimeOfDay(enum.Enum):
    morning = "morning"
    day = "day"
    evening = "evening"
    night = "night"


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    camera_id: Mapped[UUID] = mapped_column(
        ForeignKey("cameras.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    name: Mapped[str]
    duration: Mapped[float | None] = mapped_column(nullable=True)
    video_resolution: Mapped[str | None] = mapped_column(nullable=True)
    fps: Mapped[float | None] = mapped_column(nullable=True)
    time_of_day: Mapped[TimeOfDay | None] = mapped_column(
        Enum(TimeOfDay), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    video_storage_key: Mapped[str]
    preview_storage_key: Mapped[str]
    status: Mapped[VideoStatus] = mapped_column(Enum(VideoStatus))

    camera: Mapped["Camera"] = relationship(back_populates="videos")
    user: Mapped["User | None"] = relationship(back_populates="videos")
