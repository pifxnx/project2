from src.schemas.geo import (
    build_feature_collection,
    Geometry,
    Feature,
    FeatureCollection,
    Properties,
)
from src.data.models.camera import Camera


def test_builder_feature_collection():
    cameras = [
        (
            Camera(
                camera_id="camera_id",
                camera_name="camera_name",
                camera_type="camera_type",
                camera_class="camera_class",
                camera_longitude=1.0,
                camera_latitude=1.0,
            ),
            False,
        ),
        (
            Camera(
                camera_id="camera_id_2",
                camera_name="camera_name_2",
                camera_type="camera_type_2",
                camera_class="camera_class_2",
                camera_longitude=2.0,
                camera_latitude=2.0,
            ),
            True,
        ),
    ]

    expected = FeatureCollection(
        features=[
            Feature(
                properties=Properties(has_video=False, camera_id="camera_id"),
                geometry=Geometry(coordinates=[1.0, 1.0]),
            ),
            Feature(
                properties=Properties(has_video=True, camera_id="camera_id_2"),
                geometry=Geometry(coordinates=[2.0, 2.0]),
            ),
        ]
    )

    assert build_feature_collection(cameras) == expected


def test_builder_feature_collection_empty():
    res = build_feature_collection([])

    assert res == FeatureCollection(features=[])
