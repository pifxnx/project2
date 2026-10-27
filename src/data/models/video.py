import enum
from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from ...core.database import Base


if TYPE_CHECKING:
    from .camera import Camera


class VideoStatus(enum.Enum):
    processing = "processing"
    success = "success"
    failed = "failed"


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    camera_id: Mapped[UUID] = mapped_column(
        ForeignKey("cameras.id", ondelete="CASCADE"), index=True
    )
    video_storage_key: Mapped[str]
    preview_storage_key: Mapped[str]
    status: Mapped[VideoStatus] = mapped_column(Enum(VideoStatus))

    camera: Mapped["Camera"] = relationship(back_populates="videos")
