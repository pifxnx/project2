import asyncio
from rq import Queue
from redis import Redis
from rq.job import Job
from rq.exceptions import NoSuchJobError
from ..core.config import settings
from ..domain.exceptions.job_exceptions import JobNotFoundException
from ..schemas.job import JobResponse


redis_conn_queue = Redis.from_url(settings.redis_url)

q = Queue(connection=redis_conn_queue)


def get_job_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn_queue)

    except NoSuchJobError:
        raise JobNotFoundException()

    return JobResponse(job_id=job.id, status=job.get_status())


async def get_job_status_async(job_id: str):
    return await asyncio.to_thread(get_job_status, job_id)
