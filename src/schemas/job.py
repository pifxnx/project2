from pydantic import BaseModel
from rq.job import JobStatus


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
