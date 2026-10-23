from ...core.exceptions import AppException


class VideoNotFoundException(AppException):
    def __init__(self, video_id: int):
        super().__init__(
            status_code=404, message=f"Video with ID {video_id} not found."
        )
