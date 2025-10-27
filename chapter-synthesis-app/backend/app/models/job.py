from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel


class Job(BaseModel):
    __tablename__ = "jobs"

    # Job identification
    job_type = Column(String(100), nullable=False, index=True)  # indexing, generation, enrichment
    job_id = Column(String(100), unique=True, index=True, nullable=False)

    # Status tracking
    status = Column(String(50), default="pending", index=True)  # pending, running, completed, failed, cancelled
    progress = Column(Float, default=0.0)
    current_stage = Column(String(200))
    stage_progress = Column(Float, default=0.0)

    # Results
    result = Column(JSON)
    error_message = Column(Text)
    error_traceback = Column(Text)

    # Performance metrics
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    total_time_seconds = Column(Float)
    estimated_time_remaining_seconds = Column(Float)

    # Cost tracking
    total_cost = Column(Float, default=0.0)
    estimated_total_cost = Column(Float)

    # Cache metrics
    cache_hit_rate = Column(Float)
    cache_savings = Column(Float)

    # Configuration
    config = Column(JSON, default={})

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Related entities
    document_id = Column(Integer, ForeignKey("documents.id"))
    chapter_id = Column(Integer, ForeignKey("chapters.id"))

    # Relationships
    user = relationship("User", back_populates="jobs")
    stages = relationship("JobStage", back_populates="job", cascade="all, delete-orphan", order_by="JobStage.stage_number")

    def __repr__(self):
        return f"<Job {self.job_type}:{self.job_id}>"

    def update_progress(self, progress: float, stage: str = None):
        self.progress = progress
        if stage:
            self.current_stage = stage
        self.updated_at = datetime.utcnow()


class JobStage(BaseModel):
    __tablename__ = "job_stages"

    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    stage_number = Column(Integer, nullable=False)
    stage_name = Column(String(200), nullable=False)

    # Status
    status = Column(String(50), default="pending")  # pending, running, completed, failed, skipped
    progress = Column(Float, default=0.0)

    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)

    # Results
    result = Column(JSON)
    error_message = Column(Text)

    # Metrics
    items_processed = Column(Integer, default=0)
    items_total = Column(Integer)
    cost = Column(Float, default=0.0)

    # Relationships
    job = relationship("Job", back_populates="stages")

    def __repr__(self):
        return f"<JobStage {self.stage_name}>"

    def start(self):
        self.status = "running"
        self.started_at = datetime.utcnow()

    def complete(self, result: dict = None):
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        if result:
            self.result = result
        self.progress = 100.0

    def fail(self, error: str):
        self.status = "failed"
        self.error_message = error
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
