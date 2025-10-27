from sqlalchemy import Column, String, Text, JSON, Integer, DateTime, Index
from datetime import datetime, timedelta
from .base import BaseModel


class CacheEntry(BaseModel):
    __tablename__ = "cache_entries"

    # Cache key (hashed from request parameters)
    cache_key = Column(String(255), unique=True, index=True, nullable=False)
    cache_type = Column(String(100), nullable=False, index=True)  # embedding, synthesis, search, etc.

    # Cached data
    cached_data = Column(JSON, nullable=False)
    metadata = Column(JSON, default={})

    # Usage tracking
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    # TTL (Time To Live)
    expires_at = Column(DateTime, nullable=False)

    # Size tracking
    size_bytes = Column(Integer)

    # Performance metrics
    original_generation_time_seconds = Column(Integer)
    cost_saved = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_cache_type_expires', 'cache_type', 'expires_at'),
    )

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def increment_hit(self):
        self.hit_count += 1
        self.last_accessed = datetime.utcnow()

    @staticmethod
    def calculate_expiry(cache_type: str) -> datetime:
        """Calculate expiry time based on cache type"""
        ttl_map = {
            "embedding": timedelta(days=90),
            "synthesis_structure": timedelta(days=30),
            "search_results": timedelta(days=7),
            "analysis": timedelta(days=14),
        }
        ttl = ttl_map.get(cache_type, timedelta(days=7))
        return datetime.utcnow() + ttl

    def __repr__(self):
        return f"<CacheEntry {self.cache_type}:{self.cache_key[:20]}>"
