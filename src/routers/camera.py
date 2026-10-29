from fastapi import APIRouter, Depends, Query, status
from typing import Annotated
from ..core.dependencies import get_camera_service, get_current_user
from ..schemas.camera import CameraFilters, CameraResponse, CameraCreate
from ..schemas.geo import FeatureCollection


router = APIRouter(prefix="/camera", tags=["camera"])


@router.get("/", response_model=list[CameraResponse], status_code=status.HTTP_200_OK)
async def get_cameras(
    filters: Annotated[CameraFilters, Query()],
    camera_service=Depends(get_camera_service),
    user=Depends(get_current_user),
):
    cameras = await camera_service.get_all_cameras(filters)

    return cameras


@router.get("/geojson", response_model=FeatureCollection)
async def get_cameras_geojson(camera_service=Depends(get_camera_service)):
    cameras = await camera_service.get_cameras_has_videos()

    return cameras


@router.get(
    "/{camera_id}", response_model=CameraResponse, status_code=status.HTTP_200_OK
)
async def get_camera_by_camera_id(
    camera_id: str,
    camera_service=Depends(get_camera_service),
    user=Depends(get_current_user),
):
    camera = await camera_service.get_camera_by_camera_id(camera_id)

    return camera
