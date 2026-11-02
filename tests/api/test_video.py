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
    assert len(r.json()) == 1
    assert r.json()[0]["name"] == "test.mp4"
    assert r.json()[0]["author"] is None


async def test_get_all_videos_no_token(client):
    r = await client.get("/videos")

    assert r.status_code == 401
