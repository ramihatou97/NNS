from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import redis.asyncio as redis

from app.core.database import get_db, get_redis
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.chapter import Chapter, ChapterVersion, ChapterSection
from app.models.enrichment import GapDetection, EnrichmentRequest
from app.services.chapter_service import ChapterGenerationService
from app.services.ai_service import AIService
from app.services.cache_service import CacheService
from app.services.vector_search_service import VectorSearchService
from app.services.websocket_service import WebSocketService

router = APIRouter()


class ChapterGenerateRequest(BaseModel):
    topic: str
    enable_streaming: bool = True
    enable_external_research: bool = False
    auto_fill_gaps: bool = True
    upload_document: bool = False


class ChapterResponse(BaseModel):
    id: int
    title: str
    topic: str
    status: str
    total_words: int
    total_citations: int
    total_sections: int
    quality_score: float
    created_at: str

    class Config:
        from_attributes = True


class ChapterVersionResponse(BaseModel):
    id: int
    version_number: str
    version_tag: str | None
    word_count: int
    citation_count: int
    section_count: int
    quality_score: float
    created_at: str

    class Config:
        from_attributes = True


class GapDetectionResponse(BaseModel):
    id: int
    gap_title: str
    gap_description: str
    priority: str
    estimated_words: int | None
    clinical_relevance: str | None
    status: str

    class Config:
        from_attributes = True


async def generate_chapter_background(
    chapter_id: int,
    user_id: int,
    topic: str,
    config: dict,
    db_url: str
):
    """Background task for generating chapter"""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as AS
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AS, expire_on_commit=False)

    async with async_session() as session:
        redis_client = await get_redis()
        ai_service = AIService()
        cache_service = CacheService(redis_client, session)
        vector_search = VectorSearchService(session, ai_service)

        generation_service = ChapterGenerationService(
            session,
            redis_client,
            ai_service,
            cache_service,
            vector_search
        )

        # Get user and chapter
        user_result = await session.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one()

        # Generate with streaming updates
        async for update in generation_service.generate_chapter(user, topic, config, stream=config.get("enable_streaming", True)):
            # Emit progress via WebSocket
            if update["type"] == "section_chunk":
                await WebSocketService.emit_section_chunk(
                    update.get("job_id", ""),
                    update.get("section_title", ""),
                    update.get("chunk", "")
                )
            else:
                await WebSocketService.emit_generation_progress(
                    update.get("job_id", ""),
                    update.get("progress", 0),
                    update.get("stage_name", ""),
                    update
                )

    await engine.dispose()


@router.post("/generate", response_model=dict)
async def generate_chapter(
    request: ChapterGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a new chapter"""
    # Create chapter placeholder
    chapter = Chapter(
        title=f"Comprehensive Guide: {request.topic}",
        topic=request.topic,
        owner_id=current_user.id,
        status="generating",
        generation_config=request.dict()
    )

    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)

    # Start background generation
    background_tasks.add_task(
        generate_chapter_background,
        chapter.id,
        current_user.id,
        request.topic,
        request.dict(),
        settings.DATABASE_URL
    )

    return {
        "message": "Chapter generation started",
        "chapter_id": chapter.id,
        "status": "generating"
    }


@router.get("/", response_model=List[ChapterResponse])
async def list_chapters(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's chapters"""
    query = select(Chapter).where(Chapter.owner_id == current_user.id)

    if status:
        query = query.where(Chapter.status == status)

    query = query.order_by(Chapter.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    chapters = result.scalars().all()

    return chapters


@router.get("/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get chapter details"""
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.owner_id == current_user.id
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    return chapter


@router.get("/{chapter_id}/content")
async def get_chapter_content(
    chapter_id: int,
    version_number: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get chapter content (specific version or current)"""
    # Verify ownership
    chapter_result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.owner_id == current_user.id
        )
    )
    chapter = chapter_result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Get specific version or current
    if version_number:
        version_result = await db.execute(
            select(ChapterVersion).where(
                ChapterVersion.chapter_id == chapter_id,
                ChapterVersion.version_number == version_number
            )
        )
        version = version_result.scalar_one_or_none()
    else:
        if not chapter.current_version_id:
            raise HTTPException(status_code=404, detail="No content available yet")
        version_result = await db.execute(
            select(ChapterVersion).where(ChapterVersion.id == chapter.current_version_id)
        )
        version = version_result.scalar_one()

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    # Get sections
    sections_result = await db.execute(
        select(ChapterSection)
        .where(ChapterSection.version_id == version.id)
        .order_by(ChapterSection.order_index)
    )
    sections = sections_result.scalars().all()

    return {
        "version": {
            "version_number": version.version_number,
            "version_tag": version.version_tag,
            "word_count": version.word_count,
            "citation_count": version.citation_count,
            "quality_score": version.quality_score,
            "created_at": str(version.created_at)
        },
        "content": version.content,
        "sections": [
            {
                "title": s.title,
                "content": s.content,
                "word_count": s.word_count,
                "section_number": s.section_number
            }
            for s in sections
        ]
    }


@router.get("/{chapter_id}/versions", response_model=List[ChapterVersionResponse])
async def list_chapter_versions(
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all versions of a chapter"""
    # Verify ownership
    chapter_result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.owner_id == current_user.id
        )
    )
    chapter = chapter_result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Get versions
    versions_result = await db.execute(
        select(ChapterVersion)
        .where(ChapterVersion.chapter_id == chapter_id)
        .order_by(ChapterVersion.created_at.desc())
    )
    versions = versions_result.scalars().all()

    return versions


@router.post("/{chapter_id}/rollback")
async def rollback_chapter(
    chapter_id: int,
    target_version_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rollback chapter to a previous version"""
    # Verify ownership
    chapter_result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.owner_id == current_user.id
        )
    )
    chapter = chapter_result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Verify target version exists
    version_result = await db.execute(
        select(ChapterVersion).where(
            ChapterVersion.id == target_version_id,
            ChapterVersion.chapter_id == chapter_id
        )
    )
    target_version = version_result.scalar_one_or_none()

    if not target_version:
        raise HTTPException(status_code=404, detail="Target version not found")

    # Update current version
    chapter.current_version_id = target_version_id
    chapter.total_words = target_version.word_count
    chapter.total_citations = target_version.citation_count
    chapter.quality_score = target_version.quality_score

    await db.commit()

    return {
        "message": "Chapter rolled back successfully",
        "current_version": target_version.version_number
    }


@router.get("/{chapter_id}/gaps", response_model=List[GapDetectionResponse])
async def get_chapter_gaps(
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detected content gaps for a chapter"""
    # Verify ownership
    chapter_result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.owner_id == current_user.id
        )
    )
    chapter = chapter_result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Get gaps
    gaps_result = await db.execute(
        select(GapDetection)
        .where(GapDetection.chapter_id == chapter_id)
        .order_by(GapDetection.priority.desc())
    )
    gaps = gaps_result.scalars().all()

    return gaps


@router.delete("/{chapter_id}")
async def delete_chapter(
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a chapter"""
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.owner_id == current_user.id
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    await db.delete(chapter)
    await db.commit()

    return {"message": "Chapter deleted successfully"}
