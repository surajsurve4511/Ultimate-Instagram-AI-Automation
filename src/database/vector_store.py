"""
Vector store module for content deduplication using ChromaDB and Ollama embeddings.
"""
import asyncio
import logging
from typing import Dict, List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from pathlib import Path

from src.config.settings import SETTINGS
from src.embeddings.ollama_service import OllamaEmbeddingService

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for content deduplication and similarity search"""
    
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.embedding_service = None
        self.persist_directory = Path(SETTINGS.CHROMA_PERSIST_DIRECTORY)
    
    async def initialize(self):
        """Initialize the vector store"""
        try:
            # Create persist directory if it doesn't exist
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.Client(ChromaSettings(
                persist_directory=str(self.persist_directory),
                anonymized_telemetry=False
            ))
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="instagram_content",
                metadata={"description": "Instagram content for deduplication"}
            )
            
            # Initialize embedding service
            self.embedding_service = OllamaEmbeddingService()
            await self.embedding_service.initialize()
            
            logger.info("✅ Vector store initialized successfully")
            logger.info(f"📊 Collection contains {self.collection.count()} documents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing vector store: {str(e)}")
            return False
    
    async def add_content(self, content_id: str, content_text: str, metadata: Dict = None) -> bool:
        """Add content to the vector store"""
        try:
            # Generate embedding
            embedding = await self.embedding_service.get_embedding(content_text)
            
            # Add to ChromaDB
            self.collection.add(
                ids=[content_id],
                embeddings=[embedding],
                documents=[content_text],
                metadatas=[metadata or {}]
            )
            
            logger.info(f"✅ Added content to vector store: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding content to vector store: {str(e)}")
            return False
    
    async def check_duplicate(self, content_text: str, threshold: float = 0.85) -> Optional[Dict]:
        """Check if content is a duplicate"""
        try:
            # Generate embedding for query
            query_embedding = await self.embedding_service.get_embedding(content_text)
            
            # Search for similar content
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=1
            )
            
            if results['ids'] and len(results['ids'][0]) > 0:
                # Check similarity score (ChromaDB returns distance, convert to similarity)
                distance = results['distances'][0][0]
                similarity = 1 - distance  # Convert distance to similarity
                
                if similarity >= threshold:
                    return {
                        'is_duplicate': True,
                        'similarity': similarity,
                        'existing_id': results['ids'][0][0],
                        'existing_content': results['documents'][0][0]
                    }
            
            return {
                'is_duplicate': False,
                'similarity': 0.0
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking for duplicates: {str(e)}")
            return None
    
    async def find_similar_content(self, content_text: str, n_results: int = 5) -> List[Dict]:
        """Find similar content in the vector store"""
        try:
            # Generate embedding
            query_embedding = await self.embedding_service.get_embedding(content_text)
            
            # Search for similar content
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            similar_items = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    distance = results['distances'][0][i]
                    similarity = 1 - distance
                    
                    similar_items.append({
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'similarity': similarity,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                    })
            
            logger.info(f"✅ Found {len(similar_items)} similar items")
            return similar_items
            
        except Exception as e:
            logger.error(f"❌ Error finding similar content: {str(e)}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content from the vector store"""
        try:
            self.collection.delete(ids=[content_id])
            logger.info(f"✅ Deleted content from vector store: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting content: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            
            return {
                'total_documents': count,
                'persist_directory': str(self.persist_directory),
                'collection_name': self.collection.name
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {str(e)}")
            return {}
    
    async def clear_collection(self):
        """Clear all content from the collection"""
        try:
            # Delete the collection and recreate it
            self.chroma_client.delete_collection(name="instagram_content")
            self.collection = self.chroma_client.create_collection(
                name="instagram_content",
                metadata={"description": "Instagram content for deduplication"}
            )
            
            logger.info("✅ Cleared vector store collection")
            
        except Exception as e:
            logger.error(f"❌ Error clearing collection: {str(e)}")

# Global instance
vector_store = VectorStore()