from pydantic import BaseModel
from typing import Literal
from ..data.models.camera import Camera


class Geometry(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: list[float]


class Properties(BaseModel):
    camera_id: str
    has_video: bool


class Feature(BaseModel):
    type: Literal["Feature"] = "Feature"
    properties: Properties
    geometry: Geometry


class FeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[Feature]


def build_feature_collection(rows: list[tuple[Camera, bool]]) -> FeatureCollection:
    return FeatureCollection(
        features=[
            Feature(
                properties=Properties(has_video=row[1], camera_id=row[0].camera_id),
                geometry=Geometry(
                    coordinates=[row[0].camera_longitude, row[0].camera_latitude]
                ),
            )
            for row in rows
        ]
    )
