from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..schemas.token import AccessToken, RefreshToken, TokenPair
from ..domain.services.auth_service import AuthService
from ..core.dependencies import get_auth_service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
async def login_user(
    user: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    access, refresh = await auth_service.login_user(
        email=user.username,
        password=user.password,
    )

    return TokenPair(access_token=access, refresh_token=refresh)


@router.post(
    "/refresh",
)
async def refresh_token(
    refresh_token: RefreshToken, auth_service: AuthService = Depends(get_auth_service)
):
    new_access_token = await auth_service.get_access_token(refresh_token.refresh_token)

    return AccessToken(access_token=new_access_token)
