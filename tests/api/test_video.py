import pytest
from src.data.models.video import VideoStatus


async def test_get_all_videos(client, create_camera, create_video, auth_headers):
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
        "name": "test.mp4",
        "video_storage_key": "test_video.mp4",
        "preview_storage_key": "test_video.jpg",
        "status": VideoStatus.success,
    }

    await create_video(video_data)

    r = await client.get("/videos", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1
    assert r.json()["items"][0]["name"] == "test.mp4"
    assert r.json()["items"][0]["author"] is None


async def test_get_all_videos_no_token(client):
    r = await client.get("/videos")

    assert r.status_code == 401


async def _create_videos_with_durations(create_camera, create_video, durations):
    camera = await create_camera(
        {
            "camera_id": "cam-00001",
            "camera_name": "Камера 1",
            "camera_latitude": 55.75,
            "camera_longitude": 37.6,
            "azimuth": 90,
        }
    )

    for i, duration in enumerate(durations):
        await create_video(
            {
                "camera_id": camera.id,
                "name": f"video{i}.mp4",
                "video_storage_key": f"video{i}.mp4",
                "preview_storage_key": f"video{i}.jpg",
                "status": VideoStatus.success,
                "duration": duration,
            }
        )


@pytest.mark.parametrize(
    "order, expected",
    [("asc", [10.0, 20.0, 30.0]), ("desc", [30.0, 20.0, 10.0])],
)
async def test_get_all_videos_sort_by_duration(
    client, create_camera, create_video, auth_headers, order, expected
):
    await _create_videos_with_durations(create_camera, create_video, [20.0, 30.0, 10.0])

    r = await client.get(
        "/videos", params={"sort": "duration", "order": order}, headers=auth_headers
    )

    assert r.status_code == 200
    assert [v["duration"] for v in r.json()["items"]] == expected


async def test_get_all_videos_sort_by_name(
    client, create_camera, create_video, auth_headers
):
    await _create_videos_with_durations(create_camera, create_video, [1.0, 2.0, 3.0])

    r = await client.get(
        "/videos", params={"sort": "name", "order": "asc"}, headers=auth_headers
    )

    assert r.status_code == 200
    assert [v["name"] for v in r.json()["items"]] == ["video0.mp4", "video1.mp4", "video2.mp4"]


@pytest.mark.parametrize(
    "params",
    [{"sort": "hashed_password"}, {"order": "sideways"}, {"limit": 201}, {"limit": 0}],
)
async def test_get_all_videos_invalid_params(client, auth_headers, params):
    r = await client.get("/videos", params=params, headers=auth_headers)

    assert r.status_code == 422


async def test_get_all_videos_limit_200_allowed(client, auth_headers):
    r = await client.get("/videos", params={"limit": 200}, headers=auth_headers)

    assert r.status_code == 200


async def test_get_all_videos_has_status_and_email(
    client, create_camera, create_video, create_user, auth_headers
):
    camera = await create_camera(
        {
            "camera_id": "cam-00001",
            "camera_name": "Камера 1",
            "camera_latitude": 55.75,
            "camera_longitude": 37.6,
            "azimuth": 90,
        }
    )
    user = await create_user(
        {"email": "author@mail.com", "fullname": "Author", "hashed_password": "x"}
    )
    await create_video(
        {
            "camera_id": camera.id,
            "name": "test.mp4",
            "video_storage_key": "test_video.mp4",
            "preview_storage_key": "test_video.jpg",
            "status": VideoStatus.processing,
            "user_id": user.id,
        }
    )

    r = await client.get("/videos", headers=auth_headers)

    assert r.status_code == 200
    assert r.json()["items"][0]["status"] == "processing"
    assert r.json()["items"][0]["email"] == "author@mail.com"
