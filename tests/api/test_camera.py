async def test_get_camera_geojson(client, create_camera):
    camera_data = {
        "camera_id": "cam-00001",
        "camera_name": "Камера 1",
        "camera_latitude": 55.75,
        "camera_longitude": 37.6,
        "azimuth": 90,
    }

    await create_camera(camera_data)
    camera_data.update({"camera_id": "cam-00002"})
    await create_camera(camera_data)

    r = await client.get("/camera/geojson")

    assert r.status_code == 200
    assert r.json()["type"] == "FeatureCollection"
    assert len(r.json()["features"]) == 2


async def test_get_camera_no_token(client):
    r = await client.get("/camera/1")

    assert r.status_code == 401
