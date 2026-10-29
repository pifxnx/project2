from uuid import UUID
from sqlalchemy.exc import IntegrityError
from ...data.repositories.camera_repo import CameraRepo
from ...data.models.camera import Camera
from ...schemas.camera import CameraCreate, CameraResponse, CameraFilters
from ...schemas.geo import build_feature_collection, FeatureCollection
from ..exceptions.camera_exceptions import (
    CameraNotFoundException,
    CameraAlreadyExistsException,
)
from ...core.cache import Cache
from redis.exceptions import RedisError


class CameraService:
    def __init__(self, repository: CameraRepo, cache: Cache):
        self.repository = repository
        self.cache = cache

    async def create_camera(self, data: CameraCreate):
        camera = Camera(**data.model_dump())

        try:
            camera = await self.repository.create_camera(camera)
            return CameraResponse.model_validate(camera)
        except IntegrityError:
            raise CameraAlreadyExistsException("Camera with this ID already exists.")

    async def create_many(self, data: list[CameraCreate]):
        cameras = [Camera(**item.model_dump()) for item in data]

        try:
            await self.repository.create_many(cameras)
            return [CameraResponse.model_validate(camera) for camera in cameras]
        except IntegrityError:
            raise CameraAlreadyExistsException("One or more cameras already exist.")

    async def get_camera_by_id(self, id: UUID):
        camera = await self.repository.get_camera_by_id(id)

        if not camera:
            raise CameraNotFoundException(str(id))

        return CameraResponse.model_validate(camera)

    async def get_camera_by_camera_id(self, camera_id: str):
        camera = await self.repository.get_camera_by_camera_id(camera_id)

        if not camera:
            raise CameraNotFoundException(camera_id)

        return CameraResponse.model_validate(camera)

    async def get_all_cameras(self, filters: CameraFilters):
        cameras = await self.repository.get_all_cameras(filters)
        return [CameraResponse.model_validate(camera) for camera in cameras]

    async def get_cameras_geojson(self):
        try:
            if res := await self.cache.get("cameras:geojson"):
                res = FeatureCollection.model_validate_json(res)
        except RedisError:
            res = None

        if res is None:
            cameras = await self.repository.get_cameras_has_videos()

            res = build_feature_collection(cameras)
            try:
                await self.cache.set("cameras:geojson", res.model_dump_json())
            except RedisError:
                pass

        return res
