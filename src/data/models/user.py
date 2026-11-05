from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from ...core.database import Base


if TYPE_CHECKING:
    from .video import Video


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    fullname: Mapped[str]
    hashed_password: Mapped[str]
    organization: Mapped[str] = mapped_column(nullable=True)

    videos: Mapped[list["Video"]] = relationship(back_populates="user")
