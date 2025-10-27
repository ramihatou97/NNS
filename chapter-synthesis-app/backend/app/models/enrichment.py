from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class EnrichmentRequest(BaseModel):
    __tablename__ = "enrichment_requests"

    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)

    # Enrichment type
    enrichment_type = Column(String(100), nullable=False)  # gap_filling, external_research, document_integration

    # Configuration
    config = Column(JSON, default={})

    # Status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)

    # Results
    result_version_id = Column(Integer, ForeignKey("chapter_versions.id"))
    additions_summary = Column(JSON, default={})
    error_message = Column(Text)

    # Performance metrics
    processing_time_seconds = Column(Float)
    cost = Column(Float)
    cache_hit_rate = Column(Float)

    # Relationships
    chapter = relationship("Chapter", back_populates="enrichment_requests")

    def __repr__(self):
        return f"<EnrichmentRequest {self.enrichment_type}>"


class GapDetection(BaseModel):
    __tablename__ = "gap_detections"

    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("chapter_versions.id"))

    # Gap information
    gap_title = Column(String(500), nullable=False)
    gap_description = Column(Text, nullable=False)
    priority = Column(String(50), default="medium")  # high, medium, low
    gap_type = Column(String(100))  # missing_topic, thin_coverage, emerging_topic

    # Evidence
    evidence_sources = Column(JSON, default=[])
    user_question_count = Column(Integer, default=0)
    clinical_relevance = Column(String(50))  # high, medium, low

    # Recommendation
    recommended_action = Column(String(200))
    estimated_words = Column(Integer)
    estimated_time_minutes = Column(Float)
    estimated_cost = Column(Float)

    # Status
    status = Column(String(50), default="detected")  # detected, dismissed, in_progress, filled
    filled_in_version_id = Column(Integer, ForeignKey("chapter_versions.id"))

    # Relationships
    chapter = relationship("Chapter", back_populates="gap_detections")

    def __repr__(self):
        return f"<GapDetection {self.gap_title}>"
