import json
import hashlib
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.cache import CacheEntry
from app.core.config import settings


class CacheService:
    """Smart caching service for reusing common structures and reducing costs"""

    def __init__(self, redis_client: redis.Redis, db_session: AsyncSession):
        self.redis = redis_client
        self.db = db_session

    def _generate_cache_key(self, cache_type: str, params: Dict) -> str:
        """Generate a deterministic cache key from parameters"""
        params_str = json.dumps(params, sort_keys=True)
        hash_obj = hashlib.sha256(f"{cache_type}:{params_str}".encode())
        return hash_obj.hexdigest()

    async def get(self, cache_type: str, params: Dict) -> Optional[Any]:
        """Get cached data if available"""
        cache_key = self._generate_cache_key(cache_type, params)

        # Try Redis first (fast lookup)
        redis_key = f"cache:{cache_type}:{cache_key}"
        cached_data = await self.redis.get(redis_key)

        if cached_data:
            # Update hit count in background
            await self._increment_hit_count(cache_key)
            return json.loads(cached_data)

        # Fallback to database
        result = await self.db.execute(
            select(CacheEntry).where(CacheEntry.cache_key == cache_key)
        )
        entry = result.scalar_one_or_none()

        if entry and not entry.is_expired():
            # Update Redis cache
            ttl = int((entry.expires_at - datetime.utcnow()).total_seconds())
            await self.redis.setex(redis_key, ttl, json.dumps(entry.cached_data))

            # Update hit count
            entry.increment_hit()
            await self.db.commit()

            return entry.cached_data

        return None

    async def set(
        self,
        cache_type: str,
        params: Dict,
        data: Any,
        ttl: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """Store data in cache"""
        cache_key = self._generate_cache_key(cache_type, params)

        # Calculate expiry
        if ttl:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        else:
            expires_at = CacheEntry.calculate_expiry(cache_type)

        # Store in Redis
        redis_key = f"cache:{cache_type}:{cache_key}"
        ttl_seconds = int((expires_at - datetime.utcnow()).total_seconds())
        await self.redis.setex(redis_key, ttl_seconds, json.dumps(data))

        # Store in database for persistence
        result = await self.db.execute(
            select(CacheEntry).where(CacheEntry.cache_key == cache_key)
        )
        entry = result.scalar_one_or_none()

        if entry:
            # Update existing entry
            entry.cached_data = data
            entry.expires_at = expires_at
            entry.metadata = metadata or {}
            entry.updated_at = datetime.utcnow()
        else:
            # Create new entry
            entry = CacheEntry(
                cache_key=cache_key,
                cache_type=cache_type,
                cached_data=data,
                metadata=metadata or {},
                expires_at=expires_at,
                size_bytes=len(json.dumps(data).encode())
            )
            self.db.add(entry)

        await self.db.commit()

    async def _increment_hit_count(self, cache_key: str):
        """Increment cache hit count"""
        result = await self.db.execute(
            select(CacheEntry).where(CacheEntry.cache_key == cache_key)
        )
        entry = result.scalar_one_or_none()
        if entry:
            entry.increment_hit()
            await self.db.commit()

    async def get_cache_stats(self, cache_type: Optional[str] = None) -> Dict:
        """Get cache statistics"""
        query = select(CacheEntry)
        if cache_type:
            query = query.where(CacheEntry.cache_type == cache_type)

        result = await self.db.execute(query)
        entries = result.scalars().all()

        total_entries = len(entries)
        total_hits = sum(e.hit_count for e in entries)
        total_size = sum(e.size_bytes or 0 for e in entries)
        expired_count = sum(1 for e in entries if e.is_expired())

        return {
            "total_entries": total_entries,
            "total_hits": total_hits,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "expired_count": expired_count,
            "active_count": total_entries - expired_count,
            "avg_hits_per_entry": round(total_hits / total_entries, 2) if total_entries > 0 else 0
        }

    async def clear_expired(self) -> int:
        """Clear expired cache entries"""
        result = await self.db.execute(
            select(CacheEntry).where(CacheEntry.expires_at < datetime.utcnow())
        )
        expired_entries = result.scalars().all()

        count = len(expired_entries)
        for entry in expired_entries:
            await self.db.delete(entry)

        await self.db.commit()
        return count

    async def calculate_similarity(self, params1: Dict, params2: Dict) -> float:
        """Calculate similarity between two parameter sets for smart caching"""
        # Simple implementation - can be enhanced with ML
        keys1 = set(params1.keys())
        keys2 = set(params2.keys())

        if not keys1 or not keys2:
            return 0.0

        common_keys = keys1.intersection(keys2)
        all_keys = keys1.union(keys2)

        # Jaccard similarity
        key_similarity = len(common_keys) / len(all_keys)

        # Value similarity for common keys
        value_matches = 0
        for key in common_keys:
            if params1[key] == params2[key]:
                value_matches += 1

        value_similarity = value_matches / len(common_keys) if common_keys else 0

        # Combined similarity
        return (key_similarity + value_similarity) / 2
