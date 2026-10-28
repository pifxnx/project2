import pytest
from unittest.mock import MagicMock
from unittest.mock import AsyncMock
from src.core.config import settings
from src.domain.services.video_service import InvalidVideoFormatException


@pytest.fixture
def mock_queue(monkeypatch):
    queue = MagicMock()
    monkeypatch.setattr("src.domain.services.video_service.q", queue)
    return queue


@pytest.fixture
def upload_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path))
    return tmp_path


def make_file(filename, content=b"test"):
    mock_file = AsyncMock()
    mock_file.filename = filename
    mock_file.read.side_effect = [content, b""]
    return mock_file


def make_job(job_id):
    job = MagicMock()
    job.id = job_id
    return job


@pytest.mark.parametrize("filename", ["test.mp3", "test", "", None])
async def test_upload_video_invalid_format(
    get_video_service_mock_storage, mock_queue, upload_dir, filename
):
    video_service = get_video_service_mock_storage

    with pytest.raises(InvalidVideoFormatException):
        await video_service.upload_video(
            camera_id="test123", files=[make_file(filename)]
        )

    mock_queue.enqueue.assert_not_called()
    assert list(upload_dir.iterdir()) == []


async def test_upload_video_one_invalid_file_rejects_all(
    get_video_service_mock_storage, mock_queue, upload_dir
):
    video_service = get_video_service_mock_storage

    with pytest.raises(InvalidVideoFormatException):
        await video_service.upload_video(
            camera_id="test123",
            files=[make_file("good.mp4"), make_file("bad.txt")],
        )

    mock_queue.enqueue.assert_not_called()
    assert list(upload_dir.iterdir()) == []


async def test_upload_video_success(
    get_video_service_mock_storage, mock_queue, upload_dir
):
    mock_queue.enqueue.return_value = make_job("1")
    video_service = get_video_service_mock_storage

    res = await video_service.upload_video(
        camera_id="test123", files=[make_file("test.mp4", b"video-data")]
    )

    mock_queue.enqueue.assert_called_once()
    kwargs = mock_queue.enqueue.call_args.kwargs
    assert kwargs["camera_id"] == "test123"
    assert kwargs["video_storage_key"].endswith(".mp4")
    assert kwargs["preview_storage_key"].endswith(".jpg")
    assert kwargs["depends_on"] is None
    with open(kwargs["file_path"], "rb") as f:
        assert f.read() == b"video-data"

    assert len(res["jobs_info"]) == 1
    assert res["jobs_info"][0]["job_id"] == "1"
    assert res["jobs_info"][0]["video_storage_key"] == kwargs["video_storage_key"]
    assert res["jobs_info"][0]["preview_storage_key"] == kwargs["preview_storage_key"]


async def test_upload_video_uppercase_extension(
    get_video_service_mock_storage, mock_queue, upload_dir
):
    mock_queue.enqueue.return_value = make_job("1")
    video_service = get_video_service_mock_storage

    await video_service.upload_video(camera_id="test123", files=[make_file("A.MP4")])

    mock_queue.enqueue.assert_called_once()


async def test_upload_multiple_videos_are_chained(
    get_video_service_mock_storage, mock_queue, upload_dir
):
    mock_queue.enqueue.side_effect = [make_job("1"), make_job("2"), make_job("3")]
    video_service = get_video_service_mock_storage

    res = await video_service.upload_video(
        camera_id="test123",
        files=[make_file("a.mp4"), make_file("b.mp4"), make_file("c.mp4")],
    )

    assert [job["job_id"] for job in res["jobs_info"]] == ["1", "2", "3"]

    calls = mock_queue.enqueue.call_args_list
    assert len(calls) == 3

    assert calls[0].kwargs["depends_on"] is None

    for call, prev_id in zip(calls[1:], ["1", "2"]):
        dependency = call.kwargs["depends_on"]
        assert dependency.dependencies == [prev_id]
        assert dependency.allow_failure is True

    file_paths = {call.kwargs["file_path"] for call in calls}
    assert len(file_paths) == 3
