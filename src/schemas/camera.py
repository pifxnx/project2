from pydantic import BaseModel, ConfigDict
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
