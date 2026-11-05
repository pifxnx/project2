import subprocess
import json
from pathlib import Path
from uuid import UUID
from redis.exceptions import RedisError
from zoneinfo import ZoneInfo
from rq.job import Dependency, Job, JobStatus
from rq.exceptions import NoSuchJobError
from .worker_queue import redis_conn_queue as redis
from .worker_queue import q
from ..core.storage import minio_storage
from ..core.database import session_local_sync
from ..data.models.video import Video, VideoStatus, TimeOfDay
from ..core.cache import invalidate_cache_sync, geojson_key


def get_time_of_day(hour: int) -> TimeOfDay:
    if 4 <= hour < 12:
        return TimeOfDay.morning
    elif 12 <= hour < 18:
        return TimeOfDay.day
    elif 18 <= hour <= 23:
        return TimeOfDay.evening
    else:
        return TimeOfDay.night


def probe_video(video_path: str) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate:format=duration",
            "-of",
            "json",
            video_path,
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    data = json.loads(result.stdout)

    stream = data["streams"][0]
    num, den = stream["r_frame_rate"].split("/")

    return {
        "duration": float(data["format"]["duration"]),
        "video_resolution": f"{stream['width']}x{stream['height']}",
        "fps": int(num) / int(den),
    }


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
    user_id: int,
    file_name: str,
    file_path: str,
    camera_id: UUID,
    video_storage_key: str,
    preview_storage_key: str,
):
    preview_file_path = f"{file_path}.jpg"

    try:
        with session_local_sync() as session:
            video = Video(
                user_id=user_id,
                name=Path(file_name).stem,
                camera_id=camera_id,
                video_storage_key=video_storage_key,
                preview_storage_key=preview_storage_key,
                status=VideoStatus.processing,
            )
            session.add(video)
            session.commit()
            session.refresh(video)
            video.name = f"{video.id}_{video.name}"

            try:
                probe = probe_video(file_path)
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
                video.duration = probe["duration"]
                video.video_resolution = probe["video_resolution"]
                video.fps = probe["fps"]
                video.status = VideoStatus.success
                video.name = f"{video.id}_{video.name}"
                video.time_of_day = get_time_of_day(
                    video.created_at.astimezone(ZoneInfo("Europe/Moscow")).hour
                )
                session.commit()

                try:
                    invalidate_cache_sync(geojson_key)
                except RedisError:
                    pass

    finally:
        Path(file_path).unlink(missing_ok=True)
        Path(preview_file_path).unlink(missing_ok=True)


def enqueue_upload(
    user_id, file_name, file_path, camera_id, video_storage_key, preview_storage_key
):
    key = f"user:{user_id}:last_upload"

    with redis.lock(f"{key}:lock", timeout=5):
        dep = None
        prev_id = redis.get(key)
        if prev_id:
            prev_id = prev_id.decode()
            try:
                prev = Job.fetch(prev_id, connection=redis)
                if prev.get_status() not in (
                    JobStatus.FINISHED,
                    JobStatus.FAILED,
                    JobStatus.STOPPED,
                    JobStatus.CANCELED,
                ):
                    dep = Dependency(jobs=[prev], allow_failure=True)

            except NoSuchJobError:
                pass

        job = q.enqueue(
            process_video_task,
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
            camera_id=camera_id,
            video_storage_key=video_storage_key,
            preview_storage_key=preview_storage_key,
            depends_on=dep,
            result_ttl=60 * 60,
        )

        redis.set(key, job.id, ex=60 * 60 * 3)

        return job
