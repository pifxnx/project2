import pytest
from src.data.models.video import VideoStatus
from src.domain.exceptions.video_exceptions import VideoNotFoundException


async def test_get_video_by_id_success(
    get_video_service_mock_storage, create_camera, create_video
):
    camera_data = {
        "camera_id": "cam-00001",
        "camera_name": "Камера 1",
        "camera_latitude": 55.75,
        "camera_longitude": 37.6,
        "azimuth": 90,
    }

    camera = await create_camera(camera_data)

    video_data = {
        "camera_id": camera.id,
        "video_storage_key": "test_video.mp4",
        "preview_storage_key": "test_video.jpg",
        "status": VideoStatus.success,
    }

    video = await create_video(video_data)

    video_service = get_video_service_mock_storage
    storage = video_service.storage
    storage.get_presigned_url.return_value = "http://url"

    result = await video_service.get_video_by_id(video.id)

    assert result.url == "http://url"
    storage.get_presigned_url.assert_called_once_with(video.video_storage_key)


async def test_get_video_by_id_not_found(get_video_service_mock_storage):
    video_service = get_video_service_mock_storage
    id = 999

    with pytest.raises(VideoNotFoundException) as exc_info:
        await video_service.get_video_by_id(id)

    assert str(exc_info.value) == f"Video with ID {id} not found."


async def test_delete_video(
    get_video_service_mock_storage, create_camera, create_video
):
    camera_data = {
        "camera_id": "cam-00001",
        "camera_name": "Камера 1",
        "camera_latitude": 55.75,
        "camera_longitude": 37.6,
        "azimuth": 90,
    }

    camera = await create_camera(camera_data)

    video_data = {
        "camera_id": camera.id,
        "video_storage_key": "test_video.mp4",
        "preview_storage_key": "test_video.jpg",
        "status": VideoStatus.success,
    }

    video = await create_video(video_data)

    video_service = get_video_service_mock_storage
    storage = video_service.storage

    await video_service.delete_video(video.id)

    storage.delete_file.assert_called_once_with(video.video_storage_key)

    with pytest.raises(VideoNotFoundException):
        await video_service.get_video_by_id(video.id)


async def test_delete_video_not_found(get_video_service_mock_storage):
    video_service = get_video_service_mock_storage

    storage = video_service.storage

    with pytest.raises(VideoNotFoundException) as exc_info:
        await video_service.delete_video(999)

    assert str(exc_info.value) == "Video with ID 999 not found."

    storage.delete_file.assert_not_called()


async def test_get_videos_by_camera_id(
    get_video_service_mock_storage, create_camera, create_video
):
    camera_data = {
        "camera_id": "cam-00001",
        "camera_name": "Камера 1",
        "camera_latitude": 55.75,
        "camera_longitude": 37.6,
        "azimuth": 90,
    }

    camera = await create_camera(camera_data)

    video_data = {
        "camera_id": camera.id,
        "video_storage_key": "test_video.mp4",
        "preview_storage_key": "test_video.jpg",
        "status": VideoStatus.success,
    }

    video = await create_video(video_data)
    video_data.update(
        {"video_storage_key": "test_video_2.mp4", "preview_storage_key": "test_video_2.jpg"}
    )
    video_2 = await create_video(video_data)

    video_service = get_video_service_mock_storage
    storage = video_service.storage
    storage.get_presigned_url.side_effect = lambda key: f"http://url/{key}"

    videos = await video_service.get_videos_by_camera_id(camera.id)

    assert len(videos) == 2
    assert videos[0].id == video.id
    assert videos[1].id == video_2.id
    assert videos[0].url == f"http://url/{video.video_storage_key}"
    assert videos[1].url == f"http://url/{video_2.video_storage_key}"
