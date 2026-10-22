from fastapi import APIRouter, Depends, status
from ..core.dependencies import get_camera_service, get_current_user


router = APIRouter(prefix="/camera", tags=["camera"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_cameras(
    camera_service=Depends(get_camera_service), user=Depends(get_current_user)
):
    cameras = await camera_service.get_all_cameras()

    return cameras


@router.get("/{camera_id}", status_code=status.HTTP_200_OK)
async def get_camera_by_camera_id(
    camera_id: str,
    camera_service=Depends(get_camera_service),
    user=Depends(get_current_user),
):
    camera = await camera_service.get_camera_by_camera_id(camera_id)

    return camera
