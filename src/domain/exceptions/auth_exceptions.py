from ...core.exceptions import AppException


class InvalidCredentialsException(AppException):
    def __init__(self, message: str = "Invalid credentials provided"):
        super().__init__(message, status_code=401)
