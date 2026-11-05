from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from ...core.database import Base


if TYPE_CHECKING:
    from .video import Video


class Camera(Base):
    __tablename__ = "cameras"

    camera_id: Mapped[str] = mapped_column(unique=True)  # номер камеры
    camera_class_cd: Mapped[int | None]  # идентификатор класса камеры
    camera_class: Mapped[str | None]  # класс камеры
    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=lambda: uuid4()
    )  # идентификатор камеры
    model: Mapped[str | None]  # модель
    camera_name: Mapped[str | None]  # название камеры
    camera_place: Mapped[str | None]  # адрес
    camera_place_cd: Mapped[int | None]  # идентификатор адреса
    serial_number: Mapped[str | None]  # серийный номер
    camera_type_cd: Mapped[int | None]  # идентификатор типа камеры
    camera_type: Mapped[str | None]  # тип камеры
    camera_latitude: Mapped[float]  # широта
    camera_longitude: Mapped[float]  # долгота
    archive: Mapped[bool] = mapped_column(default=False)  # признак архивной записи
    azimuth: Mapped[int]  # азимут
    process_dttm: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )  # дата и время добавления записи в таблицу (техн.)
    videos: Mapped[list["Video"]] = relationship(
        back_populates="camera", passive_deletes=True
    )


#
# CREATE TABLE d_camera (
#     camera_id        string    COMMENT 'Номер камеры',
#     camera_class_cd  int       COMMENT 'Идентификатор класса камеры',
#     camera_class     string    COMMENT 'Класс камеры',
#     id               UUID      COMMENT 'Идентификатор камеры',
#     model            string    COMMENT 'Модель',
#     camera_name      string    COMMENT 'Название камеры',
#     camera_place     string    COMMENT 'Адрес',
#     camera_place_cd  int       COMMENT 'Идентификатор адреса',
#     serial_number    string    COMMENT 'Серийный номер',
#     camera_type_cd   int       COMMENT 'Идентификатор типа камеры',
#     camera_type      string    COMMENT 'Тип камеры',
#     camera_latitude  float     COMMENT 'Широта',
#     camera_longitude float     COMMENT 'Долгота',
#     archive          tinyint   COMMENT 'Признак архивной записи',
#     azimuth          int       COMMENT 'Азимут',
#     process_dttm     Datetime  COMMENT 'Дата и время добавления записи в таблицу (техн.)'
# );
