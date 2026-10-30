import pytest
from src.domain.exceptions.camera_exceptions import (
    CameraNotFoundException,
    CameraAlreadyExistsException,
)
from src.schemas.camera import CameraCreate, CameraResponse, CameraFilters
from src.schemas.geo import FeatureCollection, Feature, Properties, Geometry
from src.data.models.video import VideoStatus
from src.core.cache import geojson_key


async def test_create_camera(get_camera_service):
    camera_service = get_camera_service
    camera_data = {
        "camera_id": "cam-00001",
        "camera_name": "Камера 1",
        "camera_latitude": 55.75,
        "camera_longitude": 37.6,
        "azimuth": 90,
    }

    camera = await camera_service.create_camera(CameraCreate(**camera_data))

    assert camera.camera_id == camera_data["camera_id"]
    assert camera.camera_latitude == camera_data["camera_latitude"]
    assert camera.camera_longitude == camera_data["camera_longitude"]
    assert camera.azimuth == camera_data["azimuth"]


async def test_create_camera_already_exists(get_camera_service, create_camera):
    camera_service = get_camera_service
    camera_data = {
        "camera_id": "cam-00001",
        "camera_name": "Камера 1",
        "camera_latitude": 55.75,
        "camera_longitude": 37.6,
        "azimuth": 90,
    }

    await create_camera(camera_data)

    with pytest.raises(CameraAlreadyExistsException):
        await camera_service.create_camera(CameraCreate(**camera_data))


async def test_get_camera_by_id(get_camera_service, create_camera):
    camera_service = get_camera_service
    camera_data = {
        "camera_id": "cam-00001",
        "camera_name": "Камера 1",
        "camera_latitude": 55.75,
        "camera_longitude": 37.6,
        "azimuth": 90,
    }

    created_camera = await create_camera(camera_data)
    retrieved_camera = await camera_service.get_camera_by_id(created_camera.id)

    assert retrieved_camera.camera_id == created_camera.camera_id
    assert retrieved_camera.camera_latitude == created_camera.camera_latitude
    assert retrieved_camera.camera_longitude == created_camera.camera_longitude
    assert retrieved_camera.azimuth == created_camera.azimuth


async def test_get_camera_by_id_not_found(get_camera_service):
    camera_service = get_camera_service
    non_existent_id = "99999999-9999-9999-9999-999999999999"

    with pytest.raises(CameraNotFoundException):
        await camera_service.get_camera_by_id(non_existent_id)


async def create_diff_cameras(attr: dict[str], create_camera):
    camera_data = {
        "camera_id": "cam-00001",
        "camera_name": "Камера 1",
        "camera_latitude": 55.75,
        "camera_longitude": 37.6,
        "azimuth": 90,
    }

    camera_data2 = {**camera_data, "camera_id": "cam-00002"}
    for key, value in attr.items():
        camera_data[key] = value

    matching = await create_camera(camera_data)
    other = await create_camera(camera_data2)

    return matching, other


async def test_get_camera_filters(get_camera_service, create_camera):
    camera_service = get_camera_service

    matching, other = await create_diff_cameras({"camera_name": "test"}, create_camera)

    cameras = await camera_service.get_all_cameras(CameraFilters(camera_name="est"))

    assert len(cameras) == 1
    assert cameras[0].id == matching.id


async def test_get_camera_filters_video_count(
    get_camera_service, create_camera, create_video
):
    camera_service = get_camera_service

    camera1, camera2 = await create_diff_cameras({"camera_name": "test"}, create_camera)
    camera3 = await create_camera(
        {
            "camera_name": "test",
            "camera_id": "cam-00003",
            "camera_latitude": 55.75,
            "camera_longitude": 37.6,
            "azimuth": 90,
        }
    )

    video_data = {
        "camera_id": camera1.id,
        "name": "test.mp4",
        "video_storage_key": "test_video.mp4",
        "preview_storage_key": "test_video.jpg",
        "status": VideoStatus.success,
    }
    await create_video(video_data)

    video_data.update({"camera_id": camera2.id})
    await create_video(video_data)

    video_data.update(
        {
            "video_storage_key": "test_video_2.mp4",
            "preview_storage_key": "test_video_2.jpg",
        }
    )
    await create_video(video_data)

    video_data.update({"camera_id": camera3.id, "status": VideoStatus.failed})
    await create_video(video_data)

    first = await camera_service.get_all_cameras(CameraFilters(min_videos_count=1))

    assert len(first) == 2

    second = await camera_service.get_all_cameras(CameraFilters(min_videos_count=2))

    assert len(second) == 1

    third = await camera_service.get_all_cameras(CameraFilters(min_videos_count=3))

    assert len(third) == 0

    fourth = await camera_service.get_all_cameras(CameraFilters(max_videos_count=0))

    assert len(fourth) == 1


@pytest.mark.parametrize(
    "db_field, filter_field",
    [
        ("model", "camera_model"),
        ("camera_class", "camera_class"),
        ("camera_type", "camera_type"),
    ],
)
async def test_get_cameras_filtered(
    get_camera_service, create_camera, db_field, filter_field
):
    matching, other = await create_diff_cameras({db_field: "X"}, create_camera)
    camera_service = get_camera_service

    cameras = await camera_service.get_all_cameras(CameraFilters(**{filter_field: "X"}))

    assert len(cameras) == 1
    assert cameras[0].id == matching.id


async def test_get_camera_geojson(get_camera_service, create_camera, create_video):
    camera_service = get_camera_service

    camera_data = {
        "camera_id": "cam-00001",
        "camera_name": "Камера 1",
        "camera_latitude": 55.75,
        "camera_longitude": 37.6,
        "azimuth": 90,
    }
    camera1 = await create_camera(camera_data)

    camera_data.update({"camera_id": "cam-00002"})
    camera2 = await create_camera(camera_data)

    video_data = {
        "camera_id": camera1.id,
        "name": "test.mp4",
        "video_storage_key": "test_video.mp4",
        "preview_storage_key": "test_video.jpg",
        "status": VideoStatus.success,
    }
    await create_video(video_data)

    video_data.update({"camera_id": camera2.id, "status": VideoStatus.failed})
    await create_video(video_data)

    cameras = await camera_service.get_cameras_geojson()

    features = cameras.features

    assert len(features) == 2
    assert [x.properties.has_video for x in features] == [True, False]
    assert [x.properties.camera_id for x in features] == [
        camera1.camera_id,
        camera2.camera_id,
    ]


async def test_geojson_cache_miss(get_camera_service, mock_cache, create_camera):
    await create_camera(
        {
            "camera_id": "cam-00001",
            "camera_name": "Камера 1",
            "camera_latitude": 55.75,
            "camera_longitude": 37.6,
            "azimuth": 90,
        }
    )

    camera_service = get_camera_service

    geojson = await camera_service.get_cameras_geojson()

    mock_cache.get.assert_called_once_with(geojson_key)
    mock_cache.set.assert_called_once()

    assert len(geojson.features) == 1


async def test_geojson_cache_hit(get_camera_service, mock_cache):
    cached = FeatureCollection(
        features=[
            Feature(
                properties=Properties(has_video=False, camera_id="cam-00001"),
                geometry=Geometry(coordinates=[55.75, 37.6]),
            )
        ]
    )

    mock_cache.get.return_value = cached.model_dump_json()

    camera_service = get_camera_service

    geojson = await camera_service.get_cameras_geojson()

    mock_cache.get.assert_called_once_with(geojson_key)
    mock_cache.set.assert_not_called()

    assert geojson == cached
