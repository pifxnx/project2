from ...core.exceptions import AppException


class UserAlreadyExistsException(AppException):
    def __init__(self, message: str = "User with this email already exists"):
        super().__init__(message, status_code=409)


class UserNotFoundException(AppException):
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=404)
