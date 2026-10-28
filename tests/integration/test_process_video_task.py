from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
from src.worker.tasks import process_video_task
from src.data.models.video import Video, VideoStatus


def test_processing_video(
    engine_sync, db_session_sync, create_camera_sync, monkeypatch, tmp_path
):
    camera_data = {
        "camera_id": "cam-00001",
        "camera_name": "Камера 1",
        "camera_latitude": 55.75,
        "camera_longitude": 37.6,
        "azimuth": 90,
    }
    camera = create_camera_sync(camera_data)
    sessionmaker_sync = sessionmaker(bind=engine_sync)

    first_frame_func = MagicMock()
    monkeypatch.setattr("src.worker.tasks.extract_first_frame", first_frame_func)
    storage_mock = MagicMock()
    monkeypatch.setattr("src.worker.tasks.minio_storage", storage_mock)
    monkeypatch.setattr("src.worker.tasks.session_local_sync", sessionmaker_sync)

    process_video_task(
        file_path=(tmp_path / "test.mp4"),
        camera_id=camera.id,
        video_storage_key="test/test.mp4",
        preview_storage_key="test/test.jpg",
    )

    with sessionmaker_sync() as session:
        stmt = select(Video).where(Video.camera_id == camera.id)
        video = session.execute(stmt).scalar_one_or_none()

    assert first_frame_func.call_count == 1
    assert storage_mock.upload_file.call_count == 2
    assert video is not None
    assert video.status == VideoStatus.success
