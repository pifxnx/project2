from fastapi import APIRouter, Depends, status, Query
from typing import Annotated
from ..schemas.user import UserCreate, UserResponse
from ..schemas.video import VideoResponse, VideoFilters, VideoListItem
from ..domain.services.user_service import UserService
from ..core.dependencies import get_user_service, get_current_user, get_video_service


router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user: UserCreate, user_service: UserService = Depends(get_user_service)
):
    new_user = await user_service.register_user(user)
    return new_user


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_user)):
    return user


@router.get("/me/videos", response_model=list[VideoListItem])
async def get_me_videos(
    filters: Annotated[VideoFilters, Query()],
    user=Depends(get_current_user),
    video_service=Depends(get_video_service),
):
    filters.user_id = user.id
    videos = await video_service.get_all_videos(filters)

    return videos
