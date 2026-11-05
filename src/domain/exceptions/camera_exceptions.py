from ...core.exceptions import AppException


class CameraNotFoundException(AppException):
    def __init__(self, camera_id: str):
        super().__init__(
            message=f"Camera with ID '{camera_id}' not found.",
            status_code=404,
        )


class CameraAlreadyExistsException(AppException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=409,
        )
