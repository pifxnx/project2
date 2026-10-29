from pydantic import BaseModel, ConfigDict, model_validator
from uuid import UUID


class CameraBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CameraCreate(CameraBase):
    camera_id: str  # номер камеры
    camera_class_cd: int | None = None  # идентификатор класса камеры
    camera_class: str | None = None  # класс камеры
    model: str | None = None  # модель
    camera_name: str | None = None  # название камеры
    camera_place: str | None = None  # адрес
    camera_place_cd: int | None = None  # идентификатор адреса
    serial_number: str | None = None  # серийный номер
    camera_type_cd: int | None = None  # идентификатор типа камеры
    camera_type: str | None = None  # тип камеры
    camera_latitude: float  # широта
    camera_longitude: float  # долгота
    archive: bool = False  # признак архивной записи
    azimuth: int  # азимут


class CameraResponse(CameraBase):
    id: UUID  # идентификатор камеры
    camera_id: str  # номер камеры
    camera_latitude: float  # широта
    camera_longitude: float  # долгота
    archive: bool  # признак архивной записи
    azimuth: int  # азимут


class CameraFilters(BaseModel):
    camera_name: str | None = None
    min_videos_count: int | None = None
    max_videos_count: int | None = None
    camera_model: str | None = None
    camera_type: str | None = None
    camera_class: str | None = None

    @model_validator(mode="after")
    def validate_videos_count(self):
        if self.min_videos_count is not None and self.max_videos_count is not None:
            if self.min_videos_count > self.max_videos_count:
                raise ValueError(
                    "videos_count_from must be less than or equal to videos_count_to"
                )
        return self
