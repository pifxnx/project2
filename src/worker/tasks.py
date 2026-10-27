import subprocess
import os
from pathlib import Path
from uuid import UUID
from ..core.storage import minio_storage
from ..core.database import session_local_sync
from ..data.models.video import Video, VideoStatus


def extract_first_frame(video_path: str, out_path: str) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",  # перезаписать out_path, если есть
            "-i",
            video_path,  # входной файл
            "-frames:v",
            "1",  # взять один кадр
            "-q:v",
            "2",  # качество JPEG (2 — высокое)
            out_path,
        ],
        check=True,  # CalledProcessError при ненулевом коде возврата
        capture_output=True,  # не засорять вывод, stderr доступен в исключении
        timeout=30,
    )


def process_video_task(
    file_path: str, camera_id: UUID, video_storage_key: str, preview_storage_key: str
):
    preview_file_path = f"{file_path}.jpg"

    try:
        with session_local_sync() as session:
            video = Video(
                camera_id=camera_id,
                video_storage_key=video_storage_key,
                preview_storage_key=preview_storage_key,
                status=VideoStatus.processing,
            )
            session.add(video)
            session.commit()
            session.refresh(video)

            try:
                extract_first_frame(file_path, preview_file_path)
                minio_storage.upload_file(
                    file_path=preview_file_path,
                    object_name=preview_storage_key,
                )
                minio_storage.upload_file(
                    file_path=file_path, object_name=video_storage_key
                )
            except Exception:
                video.status = VideoStatus.failed
                session.commit()
                raise

            else:
                video.status = VideoStatus.success
                session.commit()

    finally:
        Path(file_path).unlink(missing_ok=True)
        Path(preview_file_path).unlink(missing_ok=True)
