"""
Vector database integration using ChromaDB for content deduplication and similarity search.
"""
import chromadb
from chromadb.config import Settings
import hashlib
import os
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from src.content.categories import ContentItem
from datetime import datetime, timedelta

class ContentVectorDB:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection("instagram_content")
        except:
            self.collection = self.client.create_collection(
                name="instagram_content",
                metadata={"description": "Instagram AI content posts"}
            )
        
        # Initialize sentence transformer for embeddings
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_content(self, content_item: ContentItem) -> bool:
        """Add content item to vector database"""
        try:
            # Create embedding for content
            text_to_embed = f"{content_item.title} {content_item.description}"
            embedding = self.encoder.encode(text_to_embed).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding],
                documents=[text_to_embed],
                metadatas=[{
                    "title": content_item.title,
                    "category": content_item.category.value,
                    "source_url": content_item.source_url,
                    "engagement_score": content_item.engagement_score,
                    "created_at": content_item.created_at,
                    "tags": ",".join(content_item.tags),
                    "content_hash": content_item.content_hash
                }],
                ids=[content_item.content_hash]
            )
            return True
        except Exception as e:
            print(f"Error adding content to vector DB: {e}")
            return False
    
    def check_similarity(self, content_item: ContentItem, threshold: float = 0.8) -> bool:
        """Check if similar content already exists"""
        try:
            text_to_check = f"{content_item.title} {content_item.description}"
            query_embedding = self.encoder.encode(text_to_check).tolist()
            
            # Query similar content
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=5,
                include=['metadatas', 'distances']
            )
            
            if results['distances'] and len(results['distances'][0]) > 0:
                min_distance = min(results['distances'][0])
                similarity = 1 - min_distance  # Convert distance to similarity
                
                if similarity > threshold:
                    print(f"Similar content found with similarity: {similarity:.2f}")
                    return True
            
            return False
        except Exception as e:
            print(f"Error checking similarity: {e}")
            return False
    
    def is_duplicate(self, content_hash: str) -> bool:
        """Check if content with same hash already exists"""
        try:
            results = self.collection.get(ids=[content_hash])
            return len(results['ids']) > 0
        except:
            return False
    
    def get_recent_content(self, days: int = 7) -> List[Dict]:
        """Get content posted in last N days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get all content (ChromaDB doesn't support date filtering directly)
            results = self.collection.get(include=['metadatas'])
            
            recent_content = []
            for metadata in results['metadatas']:
                if metadata['created_at'] > cutoff_date:
                    recent_content.append(metadata)
            
            return recent_content
        except Exception as e:
            print(f"Error getting recent content: {e}")
            return []
    
    def get_content_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Get content by category"""
        try:
            results = self.collection.get(
                where={"category": category},
                limit=limit,
                include=['metadatas']
            )
            return results['metadatas']
        except Exception as e:
            print(f"Error getting content by category: {e}")
            return []
    
    def update_engagement_score(self, content_hash: str, engagement_score: float):
        """Update engagement score for a content item"""
        try:
            self.collection.update(
                ids=[content_hash],
                metadatas=[{"engagement_score": engagement_score}]
            )
        except Exception as e:
            print(f"Error updating engagement score: {e}")
    
    def cleanup_old_content(self, days: int = 30):
        """Remove content older than N days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get all content
            results = self.collection.get(include=['metadatas'])
            
            old_ids = []
            for i, metadata in enumerate(results['metadatas']):
                if metadata['created_at'] < cutoff_date:
                    old_ids.append(results['ids'][i])
            
            if old_ids:
                self.collection.delete(ids=old_ids)
                print(f"Cleaned up {len(old_ids)} old content items")
                
        except Exception as e:
            print(f"Error cleaning up old content: {e}")
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            all_content = self.collection.get(include=['metadatas'])
            total_count = len(all_content['ids'])
            
            category_counts = {}
            for metadata in all_content['metadatas']:
                category = metadata['category']
                category_counts[category] = category_counts.get(category, 0) + 1
            
            return {
                "total_content": total_count,
                "category_breakdown": category_counts,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

# Global instance
vector_db = ContentVectorDB()
