from ...core.exceptions import AppException


class JobNotFoundException(AppException):
    def __init__(self, message: str = "Job not found"):
        super().__init__(message, status_code=404)
