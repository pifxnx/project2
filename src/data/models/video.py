from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from ...core.database import Base


if TYPE_CHECKING:
    from .camera import Camera


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    camera_id: Mapped[UUID] = mapped_column(
        ForeignKey("cameras.id", ondelete="CASCADE"), index=True
    )
    storage_url: Mapped[str]

    camera: Mapped["Camera"] = relationship(back_populates="videos")
