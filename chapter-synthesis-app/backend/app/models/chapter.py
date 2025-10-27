from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Chapter(BaseModel):
    __tablename__ = "chapters"

    title = Column(String(500), nullable=False, index=True)
    topic = Column(String(500), nullable=False, index=True)
    description = Column(Text)

    # Current active version
    current_version_id = Column(Integer, ForeignKey("chapter_versions.id"))

    # Generation parameters
    generation_config = Column(JSON, default={})

    # Overall statistics (from current version)
    total_words = Column(Integer, default=0)
    total_citations = Column(Integer, default=0)
    total_sections = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)

    # Status
    status = Column(String(50), default="generating")  # generating, completed, failed, archived

    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="chapters")
    versions = relationship("ChapterVersion", back_populates="chapter", cascade="all, delete-orphan", foreign_keys="ChapterVersion.chapter_id")
    current_version = relationship("ChapterVersion", foreign_keys=[current_version_id], post_update=True)
    gap_detections = relationship("GapDetection", back_populates="chapter", cascade="all, delete-orphan")
    enrichment_requests = relationship("EnrichmentRequest", back_populates="chapter", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chapter {self.title}>"


class ChapterVersion(BaseModel):
    __tablename__ = "chapter_versions"

    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    version_number = Column(String(50), nullable=False)  # v1.0, v1.1, etc.
    version_tag = Column(String(200))  # "primary", "with-enrichment", etc.

    # Content
    content = Column(Text, nullable=False)
    content_html = Column(Text)

    # Statistics
    word_count = Column(Integer, default=0)
    citation_count = Column(Integer, default=0)
    section_count = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)

    # Generation metadata
    generation_time_seconds = Column(Float)
    generation_cost = Column(Float)
    cache_hit_rate = Column(Float)
    sources_used = Column(JSON, default=[])

    # Version control
    parent_version_id = Column(Integer, ForeignKey("chapter_versions.id"))
    is_rollback = Column(Boolean, default=False)
    changes_summary = Column(Text)

    # Relationships
    chapter = relationship("Chapter", back_populates="versions", foreign_keys=[chapter_id])
    sections = relationship("ChapterSection", back_populates="version", cascade="all, delete-orphan")
    parent_version = relationship("ChapterVersion", remote_side="ChapterVersion.id", foreign_keys=[parent_version_id])

    def __repr__(self):
        return f"<ChapterVersion {self.version_number}>"


class ChapterSection(BaseModel):
    __tablename__ = "chapter_sections"

    version_id = Column(Integer, ForeignKey("chapter_versions.id"), nullable=False)
    section_number = Column(String(50))
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    order_index = Column(Integer, default=0)

    # Section metadata
    section_type = Column(String(100))  # introduction, methodology, clinical_presentation, etc.
    citations = Column(JSON, default=[])
    is_enriched = Column(Boolean, default=False)
    is_from_gap_filling = Column(Boolean, default=False)

    # Streaming metadata
    streaming_completed = Column(Boolean, default=True)
    generation_time_seconds = Column(Float)

    # Relationships
    version = relationship("ChapterVersion", back_populates="sections")

    def __repr__(self):
        return f"<ChapterSection {self.title}>"
