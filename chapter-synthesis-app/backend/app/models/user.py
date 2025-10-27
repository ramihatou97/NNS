from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # User preferences for chapter generation
    preferences = Column(JSON, default={
        "auto_enrich": True,
        "enable_caching": True,
        "enable_streaming": True,
        "default_quality_level": "comprehensive"
    })

    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    chapters = relationship("Chapter", back_populates="owner", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"
