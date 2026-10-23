from ...core.exceptions import AppException


class VideoNotFoundException(AppException):
    def __init__(self, video_id: int):
        super().__init__(
            status_code=404, message=f"Video with ID {video_id} not found."
        )


class InvalidVideoFormatException(AppException):
    def __init__(self, file_name: str):
        super().__init__(
            status_code=400,
            message=f"Invalid video format for file {file_name}. Only .mp4 files are allowed.",
        )
