from src.core.jwt_token import create_access_token
from src.data.models.video import VideoStatus


async def test_get_me_videos(client, create_camera, create_video, create_user):
    user_data = {
        "email": "001@11.com",
        "fullname": "fullname",
        "hashed_password": "hashed_password",
    }
    user1 = await create_user(user_data)
    user_data.update({"email": "002@11.com", "fullname": "fullname2"})
    user2 = await create_user(user_data)
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
        "user_id": user1.id,
    }

    await create_video(video_data)
    token1 = "Bearer " + create_access_token(str(user1.id))
    r = await client.get(
        "/users/me/videos",
        headers={"Authorization": token1},
    )

    assert r.status_code == 200
    assert len(r.json()["items"]) == 1

    token2 = "Bearer " + create_access_token(str(user2.id))
    r = await client.get("/users/me/videos", headers={"Authorization": token2})

    assert r.status_code == 200
    assert len(r.json()["items"]) == 0
