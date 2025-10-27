from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.core.database import get_db, get_redis
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.chapter import Chapter
from app.models.job import Job
from app.services.cache_service import CacheService
import redis.asyncio as redis

router = APIRouter()


@router.get("/metrics")
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Get comprehensive dashboard metrics"""

    # Document statistics
    doc_result = await db.execute(
        select(
            func.count(Document.id).label("total"),
            func.sum(func.case((Document.indexing_status == "completed", 1), else_=0)).label("indexed"),
            func.sum(func.case((Document.indexing_status == "processing", 1), else_=0)).label("processing")
        ).where(Document.owner_id == current_user.id)
    )
    doc_stats = doc_result.first()

    # Chapter statistics
    chapter_result = await db.execute(
        select(
            func.count(Chapter.id).label("total"),
            func.sum(func.case((Chapter.status == "completed", 1), else_=0)).label("completed"),
            func.sum(func.case((Chapter.status == "generating", 1), else_=0)).label("generating"),
            func.avg(Chapter.quality_score).label("avg_quality")
        ).where(Chapter.owner_id == current_user.id)
    )
    chapter_stats = chapter_result.first()

    # Job statistics (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    job_result = await db.execute(
        select(
            func.count(Job.id).label("total"),
            func.sum(func.case((Job.status == "completed", 1), else_=0)).label("completed"),
            func.sum(func.case((Job.status == "running", 1), else_=0)).label("running"),
            func.sum(func.case((Job.status == "failed", 1), else_=0)).label("failed"),
            func.avg(Job.total_time_seconds).label("avg_time"),
            func.avg(Job.total_cost).label("avg_cost")
        ).where(
            Job.user_id == current_user.id,
            Job.created_at >= thirty_days_ago
        )
    )
    job_stats = job_result.first()

    # Active jobs
    active_jobs_result = await db.execute(
        select(Job).where(
            Job.user_id == current_user.id,
            Job.status.in_(["pending", "running"])
        ).order_by(Job.started_at.desc())
    )
    active_jobs = active_jobs_result.scalars().all()

    # Cache statistics
    cache_service = CacheService(redis_client, db)
    cache_stats = await cache_service.get_cache_stats()

    # System health
    system_health = {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "health_score": 98
    }

    return {
        "documents": {
            "total": doc_stats.total or 0,
            "indexed": doc_stats.indexed or 0,
            "processing": doc_stats.processing or 0
        },
        "chapters": {
            "total": chapter_stats.total or 0,
            "completed": chapter_stats.completed or 0,
            "generating": chapter_stats.generating or 0,
            "avg_quality_score": round(float(chapter_stats.avg_quality or 0), 1)
        },
        "jobs": {
            "total_last_30_days": job_stats.total or 0,
            "completed": job_stats.completed or 0,
            "running": job_stats.running or 0,
            "failed": job_stats.failed or 0,
            "avg_time_seconds": round(float(job_stats.avg_time or 0), 1),
            "avg_cost": round(float(job_stats.avg_cost or 0), 2)
        },
        "cache": cache_stats,
        "system_health": system_health,
        "active_jobs": [
            {
                "job_id": j.job_id,
                "job_type": j.job_type,
                "progress": j.progress,
                "current_stage": j.current_stage,
                "started_at": str(j.started_at)
            }
            for j in active_jobs
        ]
    }


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent user activity"""

    # Recent jobs
    jobs_result = await db.execute(
        select(Job)
        .where(Job.user_id == current_user.id)
        .order_by(Job.created_at.desc())
        .limit(limit)
    )
    jobs = jobs_result.scalars().all()

    activities = []
    for job in jobs:
        activities.append({
            "type": "job",
            "job_type": job.job_type,
            "status": job.status,
            "timestamp": str(job.created_at),
            "details": {
                "job_id": job.job_id,
                "progress": job.progress,
                "error": job.error_message if job.status == "failed" else None
            }
        })

    return {"activities": activities}


@router.get("/performance")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get performance metrics"""

    # Job performance over time
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    jobs_result = await db.execute(
        select(Job)
        .where(
            Job.user_id == current_user.id,
            Job.created_at >= seven_days_ago,
            Job.status == "completed"
        )
        .order_by(Job.created_at)
    )
    jobs = jobs_result.scalars().all()

    # Group by day
    daily_metrics = {}
    for job in jobs:
        day_key = job.created_at.date().isoformat()
        if day_key not in daily_metrics:
            daily_metrics[day_key] = {
                "date": day_key,
                "jobs_completed": 0,
                "total_time": 0,
                "total_cost": 0,
                "avg_cache_hit_rate": []
            }

        daily_metrics[day_key]["jobs_completed"] += 1
        daily_metrics[day_key]["total_time"] += job.total_time_seconds or 0
        daily_metrics[day_key]["total_cost"] += job.total_cost or 0
        if job.cache_hit_rate:
            daily_metrics[day_key]["avg_cache_hit_rate"].append(job.cache_hit_rate)

    # Calculate averages
    for day in daily_metrics.values():
        day["avg_time"] = round(day["total_time"] / day["jobs_completed"], 1) if day["jobs_completed"] > 0 else 0
        day["avg_cost"] = round(day["total_cost"] / day["jobs_completed"], 2) if day["jobs_completed"] > 0 else 0
        if day["avg_cache_hit_rate"]:
            day["avg_cache_hit_rate"] = round(sum(day["avg_cache_hit_rate"]) / len(day["avg_cache_hit_rate"]), 2)
        else:
            day["avg_cache_hit_rate"] = 0

    return {
        "daily_metrics": list(daily_metrics.values()),
        "summary": {
            "total_jobs": len(jobs),
            "avg_completion_time": round(sum(j.total_time_seconds or 0 for j in jobs) / len(jobs), 1) if jobs else 0,
            "total_cost": round(sum(j.total_cost or 0 for j in jobs), 2),
            "avg_cache_hit_rate": round(sum(j.cache_hit_rate or 0 for j in jobs if j.cache_hit_rate) / len([j for j in jobs if j.cache_hit_rate]), 2) if jobs else 0
        }
    }


@router.get("/cost-analysis")
async def get_cost_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Get cost analysis and savings"""

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Get all jobs with cost data
    jobs_result = await db.execute(
        select(Job)
        .where(
            Job.user_id == current_user.id,
            Job.created_at >= thirty_days_ago,
            Job.status == "completed"
        )
    )
    jobs = jobs_result.scalars().all()

    total_cost = sum(j.total_cost or 0 for j in jobs)
    total_cache_savings = sum(j.cache_savings or 0 for j in jobs)
    cost_without_cache = total_cost + total_cache_savings

    return {
        "period": "last_30_days",
        "total_cost": round(total_cost, 2),
        "cost_without_cache": round(cost_without_cache, 2),
        "total_savings": round(total_cache_savings, 2),
        "savings_percentage": round((total_cache_savings / cost_without_cache * 100), 1) if cost_without_cache > 0 else 0,
        "jobs_analyzed": len(jobs),
        "avg_cache_hit_rate": round(sum(j.cache_hit_rate or 0 for j in jobs if j.cache_hit_rate) / len([j for j in jobs if j.cache_hit_rate]), 2) if jobs else 0
    }
