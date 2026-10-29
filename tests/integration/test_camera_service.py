import pytest
from src.domain.exceptions.camera_exceptions import (
    CameraNotFoundException,
    CameraAlreadyExistsException,
)
from src.schemas.camera import CameraCreate, CameraResponse, CameraFilters


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
