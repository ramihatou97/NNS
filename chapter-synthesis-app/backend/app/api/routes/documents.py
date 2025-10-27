import os
import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import redis.asyncio as redis

from app.core.database import get_db, get_redis
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.document import Document, DocumentSection
from app.services.pdf_indexing_service import PDFIndexingService
from app.services.ai_service import AIService
from app.services.cache_service import CacheService
from app.services.websocket_service import WebSocketService

router = APIRouter()


class DocumentResponse(BaseModel):
    id: int
    title: str
    file_path: str
    file_size: int | None
    file_type: str | None
    total_pages: int | None
    total_chapters: int
    indexing_status: str
    indexing_progress: float
    created_at: str

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


async def index_document_background(
    document_id: int,
    file_path: str,
    user_id: int,
    db_url: str
):
    """Background task for indexing document"""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as AS
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AS, expire_on_commit=False)

    async with async_session() as session:
        redis_client = await get_redis()
        ai_service = AIService()
        cache_service = CacheService(redis_client, session)
        indexing_service = PDFIndexingService(session, ai_service, cache_service)

        # Get document
        result = await session.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one()

        # Index with streaming updates
        async for update in indexing_service.index_document(document, file_path, user_id):
            # Emit progress via WebSocket
            await WebSocketService.emit_indexing_progress(
                document_id=document_id,
                progress=update.get("progress", 0),
                stage=update.get("stage", ""),
                data=update
            )

    await engine.dispose()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and index a PDF document"""
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds limit")

    # Create uploads directory
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file_content)

    # Create document record
    document = Document(
        title=file.filename,
        file_path=str(file_path),
        file_size=len(file_content),
        file_type="pdf",
        owner_id=current_user.id,
        indexing_status="pending"
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Start background indexing
    background_tasks.add_task(
        index_document_background,
        document.id,
        str(file_path),
        current_user.id,
        settings.DATABASE_URL
    )

    # Notify user
    await WebSocketService.emit_notification(
        str(current_user.id),
        {
            "type": "document_uploaded",
            "message": f"Document '{file.filename}' uploaded. Indexing started.",
            "document_id": document.id
        }
    )

    return document


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's documents"""
    result = await db.execute(
        select(Document)
        .where(Document.owner_id == current_user.id)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    documents = result.scalars().all()

    # Get total count
    count_result = await db.execute(
        select(Document).where(Document.owner_id == current_user.id)
    )
    total = len(count_result.scalars().all())

    return {
        "documents": documents,
        "total": total
    }


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document details"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.owner_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.get("/{document_id}/sections")
async def get_document_sections(
    document_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document sections"""
    # Verify ownership
    doc_result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.owner_id == current_user.id
        )
    )
    document = doc_result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get sections
    result = await db.execute(
        select(DocumentSection)
        .where(DocumentSection.document_id == document_id)
        .order_by(DocumentSection.page_start)
        .offset(skip)
        .limit(limit)
    )
    sections = result.scalars().all()

    return {
        "sections": [
            {
                "id": s.id,
                "title": s.title,
                "chapter_number": s.chapter_number,
                "page_start": s.page_start,
                "page_end": s.page_end,
                "word_count": s.word_count,
                "content": s.content[:500] + "..." if len(s.content) > 500 else s.content
            }
            for s in sections
        ],
        "total": len(sections)
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.owner_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete from database
    await db.delete(document)
    await db.commit()

    return {"message": "Document deleted successfully"}
