from fastapi import APIRouter, Depends
from ..worker.worker_queue import get_job_status_async
from ..core.dependencies import get_current_user
from ..schemas.job import JobResponse


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, user=Depends(get_current_user)):
    return await get_job_status_async(job_id)
