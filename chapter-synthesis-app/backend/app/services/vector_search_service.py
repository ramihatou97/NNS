import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.document import DocumentEmbedding, DocumentSection, Document
from app.services.ai_service import AIService


class VectorSearchService:
    """Vector search service using pgvector for semantic search"""

    def __init__(self, db: AsyncSession, ai_service: AIService):
        self.db = db
        self.ai_service = ai_service

    async def search(
        self,
        query: str,
        limit: int = 10,
        similarity_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic vector search

        Args:
            query: Search query text
            limit: Maximum number of results
            similarity_threshold: Minimum cosine similarity (0-1)
            filters: Optional filters (document_id, etc.)

        Returns:
            List of search results with content and metadata
        """
        # Generate embedding for query
        query_embeddings = await self.ai_service.generate_embeddings([query])
        query_embedding = query_embeddings[0]

        # Convert to string format for pgvector
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        # Build query with pgvector similarity search
        query_sql = """
            SELECT
                de.id,
                de.document_id,
                de.section_id,
                de.text_content,
                ds.title as section_title,
                ds.content as section_content,
                ds.chapter_number,
                ds.page_start,
                ds.page_end,
                d.title as document_title,
                1 - (de.embedding <=> :query_embedding::vector) as similarity
            FROM document_embeddings de
            LEFT JOIN document_sections ds ON de.section_id = ds.id
            LEFT JOIN documents d ON de.document_id = d.id
            WHERE d.indexing_status = 'completed'
            AND 1 - (de.embedding <=> :query_embedding::vector) >= :threshold
        """

        # Add filters if provided
        if filters:
            if "document_id" in filters:
                query_sql += f" AND de.document_id = {filters['document_id']}"

        query_sql += """
            ORDER BY de.embedding <=> :query_embedding::vector
            LIMIT :limit
        """

        # Execute query
        result = await self.db.execute(
            text(query_sql),
            {
                "query_embedding": embedding_str,
                "threshold": similarity_threshold,
                "limit": limit
            }
        )

        rows = result.fetchall()

        # Format results
        results = []
        for row in rows:
            results.append({
                "embedding_id": row[0],
                "document_id": row[1],
                "section_id": row[2],
                "text_content": row[3],
                "section_title": row[4],
                "section_content": row[5],
                "chapter_number": row[6],
                "page_start": row[7],
                "page_end": row[8],
                "document_title": row[9],
                "similarity": float(row[10])
            })

        return results

    async def search_by_embedding(
        self,
        embedding: List[float],
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search using a pre-computed embedding"""
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        query_sql = """
            SELECT
                de.id,
                de.document_id,
                de.section_id,
                de.text_content,
                1 - (de.embedding <=> :query_embedding::vector) as similarity
            FROM document_embeddings de
            WHERE 1 - (de.embedding <=> :query_embedding::vector) >= :threshold
            ORDER BY de.embedding <=> :query_embedding::vector
            LIMIT :limit
        """

        result = await self.db.execute(
            text(query_sql),
            {
                "query_embedding": embedding_str,
                "threshold": similarity_threshold,
                "limit": limit
            }
        )

        rows = result.fetchall()
        return [
            {
                "embedding_id": row[0],
                "document_id": row[1],
                "section_id": row[2],
                "text_content": row[3],
                "similarity": float(row[4])
            }
            for row in rows
        ]

    async def get_similar_sections(
        self,
        section_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar sections to a given section"""
        # Get the embedding for the source section
        result = await self.db.execute(
            select(DocumentEmbedding).where(DocumentEmbedding.section_id == section_id)
        )
        source_embedding = result.scalar_one_or_none()

        if not source_embedding or not source_embedding.embedding:
            return []

        # Search for similar sections
        return await self.search_by_embedding(
            embedding=source_embedding.embedding,
            limit=limit + 1  # +1 because result will include source
        )

    async def hybrid_search(
        self,
        query: str,
        keywords: List[str],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector similarity and keyword matching
        """
        # Get vector search results
        vector_results = await self.search(query, limit=limit * 2)

        # Score boost for keyword matches
        for result in vector_results:
            keyword_matches = 0
            content = (result.get("section_content", "") or "").lower()

            for keyword in keywords:
                if keyword.lower() in content:
                    keyword_matches += 1

            # Adjust similarity score based on keyword matches
            keyword_boost = min(0.2, keyword_matches * 0.05)
            result["similarity"] = min(1.0, result["similarity"] + keyword_boost)
            result["keyword_matches"] = keyword_matches

        # Re-sort by adjusted similarity
        vector_results.sort(key=lambda x: x["similarity"], reverse=True)

        return vector_results[:limit]

    async def cluster_search_results(
        self,
        query: str,
        num_clusters: int = 3
    ) -> Dict[str, List[Dict]]:
        """
        Search and cluster results by topic
        Simple clustering based on similarity
        """
        results = await self.search(query, limit=30)

        if not results:
            return {}

        # Simple clustering: group by similarity ranges
        clusters = {
            "highly_relevant": [],
            "relevant": [],
            "somewhat_relevant": []
        }

        for result in results:
            similarity = result["similarity"]
            if similarity >= 0.9:
                clusters["highly_relevant"].append(result)
            elif similarity >= 0.75:
                clusters["relevant"].append(result)
            else:
                clusters["somewhat_relevant"].append(result)

        return clusters

    async def get_document_statistics(self, document_id: int) -> Dict[str, Any]:
        """Get statistics for a document's embeddings"""
        result = await self.db.execute(
            select(DocumentEmbedding).where(DocumentEmbedding.document_id == document_id)
        )
        embeddings = result.scalars().all()

        return {
            "document_id": document_id,
            "total_embeddings": len(embeddings),
            "embedding_dimension": 1536,
            "model": embeddings[0].embedding_model if embeddings else None
        }
