from fastapi import APIRouter, UploadFile, Depends, status, Query
from uuid import UUID
from typing import Annotated
from ..schemas.video import (
    VideoResponse,
    VideoFilters,
    VideoListItem,
    VideoListItemsPage,
    VideoDetail,
)
from ..core.dependencies import get_video_service, get_camera_service, get_current_user


router = APIRouter(tags=["videos"])


@router.get("/camera/{camera_id}/videos", response_model=list[VideoResponse])
async def get_videos_by_camera(
    camera_id: UUID,
    video_service=Depends(get_video_service),
    camera_service=Depends(get_camera_service),
):
    await camera_service.get_camera_by_id(camera_id)
    videos = await video_service.get_videos_by_camera_id(camera_id)

    return videos


@router.get("/videos", response_model=VideoListItemsPage)
async def get_all_videos(
    filters: Annotated[VideoFilters, Query()],
    video_service=Depends(get_video_service),
    user=Depends(get_current_user),
):
    videos = await video_service.get_all_videos(filters)

    return videos


@router.get("/videos/{video_id}", response_model=VideoDetail)
async def get_video(
    video_id: int,
    video_service=Depends(get_video_service),
    user=Depends(get_current_user),
):
    video = await video_service.get_video_by_id(video_id)

    return video


@router.delete("/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: int,
    video_service=Depends(get_video_service),
    user=Depends(get_current_user),
):
    await video_service.delete_video(video_id)


@router.post("/camera/{camera_id}/videos", status_code=status.HTTP_202_ACCEPTED)
async def upload_video(
    camera_id: UUID,
    files: list[UploadFile],
    video_service=Depends(get_video_service),
    camera_service=Depends(get_camera_service),
    user=Depends(get_current_user),
):

    await camera_service.get_camera_by_id(camera_id)

    res = await video_service.upload_video(user.id, camera_id, files)

    return res
