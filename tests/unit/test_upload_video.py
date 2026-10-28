import pytest
from unittest.mock import MagicMock
from unittest.mock import AsyncMock
from src.domain.services.video_service import InvalidVideoFormatException


async def test_upload_video_invalid_format(
    get_video_service_mock_storage, tmp_path, monkeypatch
):
    mock_queue = MagicMock()
    mock_queue.enqueue.return_value.id = "1"
    monkeypatch.setattr("src.domain.services.video_service.q", mock_queue)

    mock_file = AsyncMock()
    mock_file.read.side_effect = [b"test", b""]
    video_service = get_video_service_mock_storage
    with pytest.raises(InvalidVideoFormatException):
        await video_service.upload_video(
            camera_id="test123",
            file=mock_file,
            file_path=(tmp_path / "test.mp4"),
            file_name="test.mp3",
        )

    mock_queue.assert_not_called()


async def test_upload_video_no_name(
    get_video_service_mock_storage, tmp_path, monkeypatch
):
    mock_queue = MagicMock()
    mock_queue.enqueue.return_value.id = "1"
    monkeypatch.setattr("src.domain.services.video_service.q", mock_queue)

    mock_file = AsyncMock()
    mock_file.read.side_effect = [b"test", b""]
    video_service = get_video_service_mock_storage
    with pytest.raises(InvalidVideoFormatException):
        await video_service.upload_video(
            camera_id="test123",
            file=mock_file,
            file_path=(tmp_path / "test.mp4"),
            file_name="",
        )

    mock_queue.assert_not_called()


async def test_upload_video_success(
    get_video_service_mock_storage, monkeypatch, tmp_path
):
    mock_queue = MagicMock()
    mock_queue.enqueue.return_value.id = "1"
    monkeypatch.setattr("src.domain.services.video_service.q", mock_queue)

    mock_file = AsyncMock()
    mock_file.read.side_effect = [b"test", b""]
    video_service = get_video_service_mock_storage
    res = await video_service.upload_video(
        camera_id="test123",
        file=mock_file,
        file_path=(tmp_path / "test.mp4"),
        file_name="test.mp4",
    )

    assert res["job_id"] == "1"
