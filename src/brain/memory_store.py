"""
Memory Store — Long-term knowledge management using ChromaDB + Gemini Embeddings.

Each user account gets an isolated ChromaDB collection.
Knowledge entries are embedded with Gemini Embeddings and retrieved via similarity search.
"""

import logging
from typing import Optional

import chromadb

from src.ai.gemini_brain import GeminiBrain
from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)


class MemoryStore:
    """
    Per-account long-term memory backed by ChromaDB.
    
    Uses Gemini Embeddings (gemini-embedding-001) for vector storage.
    Each account has its own ChromaDB collection.
    """

    def __init__(
        self,
        gemini: Optional[GeminiBrain] = None,
        collection_name: str = "default_memory",
    ):
        self._gemini = gemini or GeminiBrain()
        self._chroma = chromadb.PersistentClient(path=SETTINGS.CHROMA_PERSIST_DIRECTORY)
        self._collection = self._chroma.get_or_create_collection(
            name=collection_name,
            metadata={"description": f"Memory for {collection_name}"},
        )

    def add_knowledge(
        self,
        topic: str,
        content: str,
        *,
        source: str = "system",
        doc_id: Optional[str] = None,
    ) -> str:
        """
        Store a knowledge entry with its Gemini embedding.
        
        Args:
            topic: Knowledge topic
            content: The knowledge content
            source: Where this came from
            doc_id: Custom document ID (auto-generated if not provided)
            
        Returns:
            Document ID
        """
        import time

        if not doc_id:
            doc_id = f"{topic[:50]}_{int(time.time())}"

        full_text = f"{topic}: {content}"

        try:
            embedding = self._gemini.embed_text(full_text)
            self._collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[full_text],
                metadatas=[{"topic": topic, "source": source}],
            )
            logger.debug(f"Stored knowledge: {topic} (id={doc_id})")
            return doc_id

        except Exception as e:
            logger.error(f"Failed to store knowledge: {e}")
            # Fallback: store without embedding
            self._collection.upsert(
                ids=[doc_id],
                documents=[full_text],
                metadatas=[{"topic": topic, "source": source}],
            )
            return doc_id

    def search(self, query: str, *, top_k: int = 5) -> list[dict]:
        """
        Find relevant knowledge entries via similarity search.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of dicts with 'topic', 'content', 'source', 'distance'
        """
        try:
            query_embedding = self._gemini.embed_text(query)
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self._collection.count() or 1),
            )
        except Exception:
            # Fallback to text search
            results = self._collection.query(
                query_texts=[query],
                n_results=min(top_k, max(self._collection.count(), 1)),
            )

        entries = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                entries.append({
                    "topic": meta.get("topic", ""),
                    "content": doc,
                    "source": meta.get("source", ""),
                    "distance": distance,
                })
        return entries

    def count(self) -> int:
        """Return the number of knowledge entries."""
        return self._collection.count()

    def clear(self) -> None:
        """Clear all knowledge entries. Use with caution."""
        ids = self._collection.get()["ids"]
        if ids:
            self._collection.delete(ids=ids)
        logger.info(f"Cleared {len(ids)} knowledge entries")
