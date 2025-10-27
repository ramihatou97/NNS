from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job, JobStage

router = APIRouter()


class JobResponse(BaseModel):
    id: int
    job_id: str
    job_type: str
    status: str
    progress: float
    current_stage: str | None
    total_time_seconds: float | None
    total_cost: float | None
    cache_hit_rate: float | None
    error_message: str | None
    created_at: str

    class Config:
        from_attributes = True


class JobStageResponse(BaseModel):
    id: int
    stage_number: int
    stage_name: str
    status: str
    progress: float
    duration_seconds: float | None
    items_processed: int | None
    items_total: int | None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 50,
    job_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's jobs"""
    query = select(Job).where(Job.user_id == current_user.id)

    if job_type:
        query = query.where(Job.job_type == job_type)

    if status:
        query = query.where(Job.status == status)

    query = query.order_by(Job.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    jobs = result.scalars().all()

    return jobs


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get job details"""
    result = await db.execute(
        select(Job).where(
            Job.job_id == job_id,
            Job.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/{job_id}/stages", response_model=List[JobStageResponse])
async def get_job_stages(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get job stages"""
    # Verify ownership
    job_result = await db.execute(
        select(Job).where(
            Job.job_id == job_id,
            Job.user_id == current_user.id
        )
    )
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get stages
    stages_result = await db.execute(
        select(JobStage)
        .where(JobStage.job_id == job.id)
        .order_by(JobStage.stage_number)
    )
    stages = stages_result.scalars().all()

    return stages


@router.delete("/{job_id}")
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a running job"""
    result = await db.execute(
        select(Job).where(
            Job.job_id == job_id,
            Job.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail="Job cannot be cancelled")

    job.status = "cancelled"
    await db.commit()

    return {"message": "Job cancelled successfully"}
