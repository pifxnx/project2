import asyncio
from random import uniform, randint, choice
from sqlalchemy.dialects.postgresql import insert
from ..core.database import session_local_async
from ..data.models.camera import Camera

# Москва: lon 37.3–37.9, lat 55.5–55.95
LON_RANGE = (37.3, 37.9)
LAT_RANGE = (55.5, 55.95)

MODELS = ["Axis P3245", "Hikvision DS-2CD2043", "Dahua IPC-HFW", "Bosch DINION"]
# (код, название)
CAMERA_TYPES = [(1, "Купольная"), (2, "Цилиндрическая"), (3, "Поворотная")]
CAMERA_CLASSES = [(1, "Обзорная"), (2, "Распознавание номеров"), (3, "Контроль нарушений")]
# Несколько камер делят один адрес, из них потом можно собирать комплексы
PLACES = [
    (1, "Красногвардейский 1-й проезд"),
    (2, "Ленинградский проспект"),
    (3, "Кутузовский проспект"),
    (4, "Тверская улица"),
    (5, "Садовое кольцо"),
    (6, "Варшавское шоссе"),
    (7, "Ленинский проспект"),
    (8, "Волгоградский проспект"),
    (9, "Щёлковское шоссе"),
    (10, "Профсоюзная улица"),
    (11, "Дмитровское шоссе"),
    (12, "Новый Арбат"),
]


async def add_cameras(cameras: list[dict]):
    async with session_local_async() as session:
        stmt = (
            insert(Camera)
            .values(cameras)
            .on_conflict_do_nothing(index_elements=["camera_id"])
        )
        await session.execute(stmt)
        await session.commit()


def make_cameras(count: int = 50) -> list[dict]:
    cameras = []
    for i in range(1, count + 1):
        type_cd, type_name = choice(CAMERA_TYPES)
        class_cd, class_name = choice(CAMERA_CLASSES)
        place_cd, place = choice(PLACES)

        cameras.append(
            {
                "camera_id": f"cam-{i:05d}",
                "camera_name": f"Камера {i}",
                "model": choice(MODELS),
                "camera_type_cd": type_cd,
                "camera_type": type_name,
                "camera_class_cd": class_cd,
                "camera_class": class_name,
                "camera_place_cd": place_cd,
                "camera_place": place,
                "serial_number": f"SN-{i:06d}",
                "camera_latitude": round(uniform(*LAT_RANGE), 6),
                "camera_longitude": round(uniform(*LON_RANGE), 6),
                "archive": False,
                "azimuth": randint(0, 359),
            }
        )

    return cameras


if __name__ == "__main__":
    asyncio.run(add_cameras(make_cameras()))
