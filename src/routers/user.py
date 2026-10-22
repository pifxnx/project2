from fastapi import APIRouter, Depends, status
from ..schemas.user import UserCreate, UserResponse
from ..domain.services.user_service import UserService
from ..core.dependencies import get_user_service, get_current_user


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
