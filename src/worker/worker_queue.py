from rq import Queue
from redis import Redis
from ..core.config import settings


redis_conn_queue = Redis.from_url(settings.redis_url)

q = Queue(connection=redis_conn_queue)
