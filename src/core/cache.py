from redis.asyncio import Redis
from .config import settings


redis_client = Redis.from_url(settings.redis_url, decode_responses=True)

geojson_key = "cameras:geojson"


class Cache:
    def __init__(self, client: Redis, ttl: int):
        self.client = client
        self.ttl = ttl

    async def get(self, key: str):
        return await self.client.get(key)

    async def set(self, key: str, value: str):
        return await self.client.set(key, value, ex=self.ttl)

    async def delete(self, key: str):
        return await self.client.delete(key)


cache = Cache(redis_client, 60)
