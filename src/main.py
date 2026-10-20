from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .routers.user import router as user_router
from .routers.auth import router as auth_router
from .core.exceptions import AppException


app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )


app.include_router(user_router)
app.include_router(auth_router)
