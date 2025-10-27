from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, Float, LargeBinary
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"

    title = Column(String(500), nullable=False, index=True)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    total_pages = Column(Integer)
    total_chapters = Column(Integer, default=0)

    # Indexing status
    indexing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    indexing_progress = Column(Float, default=0.0)
    error_message = Column(Text)

    # Metadata extracted during indexing
    metadata = Column(JSON, default={})

    # Performance metrics
    indexing_time_seconds = Column(Float)
    cache_hit_rate = Column(Float)

    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="documents")
    sections = relationship("DocumentSection", back_populates="document", cascade="all, delete-orphan")
    embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document {self.title}>"


class DocumentSection(BaseModel):
    __tablename__ = "document_sections"

    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chapter_number = Column(Integer)
    section_number = Column(String(50))
    title = Column(String(500))
    content = Column(Text, nullable=False)
    page_start = Column(Integer)
    page_end = Column(Integer)
    word_count = Column(Integer)

    # Extracted metadata
    section_type = Column(String(100))  # introduction, methodology, results, etc.
    medical_concepts = Column(JSON, default=[])  # NER extracted concepts
    citations = Column(JSON, default=[])

    # Relevance scoring
    importance_score = Column(Float)

    # Foreign Keys
    document = relationship("Document", back_populates="sections")
    embeddings = relationship("DocumentEmbedding", back_populates="section", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DocumentSection {self.title}>"


class DocumentEmbedding(BaseModel):
    __tablename__ = "document_embeddings"

    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("document_sections.id"))

    # Vector embedding (1536 dimensions for OpenAI text-embedding-3-large)
    embedding = Column(Vector(1536))

    # Text that was embedded
    text_content = Column(Text)
    embedding_model = Column(String(100), default="text-embedding-3-large")

    # Relationships
    document = relationship("Document", back_populates="embeddings")
    section = relationship("DocumentSection", back_populates="embeddings")

    def __repr__(self):
        return f"<DocumentEmbedding doc={self.document_id} section={self.section_id}>"
