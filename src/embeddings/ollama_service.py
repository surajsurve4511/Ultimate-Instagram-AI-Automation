"""
Local embeddings service using Ollama with nomic-embed-text model.
This replaces OpenAI embeddings with free local embeddings.
"""
import aiohttp
import asyncio
import numpy as np
from typing import List, Dict, Optional
import logging
from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)

class OllamaEmbeddingService:
    """Local embedding service using Ollama"""
    
    def __init__(self):
        self.base_url = SETTINGS.OLLAMA_BASE_URL
        self.model = SETTINGS.OLLAMA_EMBEDDING_MODEL
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def initialize(self):
        """Initialize the embedding service"""
        try:
            # Check if Ollama is running
            await self._check_ollama_status()
            
            # Ensure the embedding model is available
            await self._ensure_model_available()
            
            logger.info("✅ Ollama embedding service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama embedding service: {str(e)}")
            logger.error("💡 Make sure Ollama is running with: ollama serve")
            logger.error(f"💡 And the model is installed with: ollama pull {self.model}")
            return False
    
    async def _check_ollama_status(self):
        """Check if Ollama server is running"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    logger.info("✅ Ollama server is running")
                    return True
                else:
                    raise Exception(f"Ollama server returned status {response.status}")
        
        except Exception as e:
            raise Exception(f"Ollama server is not running or not accessible: {str(e)}")
    
    async def _ensure_model_available(self):
        """Ensure the embedding model is available"""
        try:
            # List available models
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    available_models = [model['name'] for model in data.get('models', [])]
                    
                    if self.model not in available_models:
                        logger.warning(f"🔍 Model {self.model} not found. Available models: {available_models}")
                        logger.info(f"📥 Attempting to pull {self.model}...")
                        await self._pull_model()
                    else:
                        logger.info(f"✅ Model {self.model} is available")
                        
        except Exception as e:
            logger.error(f"❌ Error checking model availability: {str(e)}")
            raise
    
    async def _pull_model(self):
        """Pull the embedding model if not available"""
        try:
            pull_data = {"name": self.model}
            
            async with self.session.post(
                f"{self.base_url}/api/pull", 
                json=pull_data
            ) as response:
                if response.status == 200:
                    logger.info(f"✅ Successfully pulled {self.model}")
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to pull model: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Error pulling model {self.model}: {str(e)}")
            raise
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            embeddings = []
            
            for text in texts:
                embedding = await self._get_single_embedding(text)
                embeddings.append(embedding)
                
                # Small delay to avoid overwhelming the local server
                await asyncio.sleep(0.1)
            
            logger.info(f"✅ Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {str(e)}")
            raise
    
    async def _get_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            # Prepare the request data
            request_data = {
                "model": self.model,
                "prompt": text
            }
            
            # Make the request to Ollama
            async with self.session.post(
                f"{self.base_url}/api/embeddings",
                json=request_data
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    embedding = data.get('embedding', [])
                    
                    if not embedding:
                        raise Exception("No embedding returned from Ollama")
                    
                    return embedding
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Error generating single embedding: {str(e)}")
            raise
    
    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text (convenience method)"""
        embeddings = await self.get_embeddings([text])
        return embeddings[0]
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"❌ Error calculating similarity: {str(e)}")
            return 0.0
    
    async def find_similar_texts(self, query_text: str, text_embeddings: Dict[str, List[float]], 
                               threshold: float = 0.8) -> List[Dict]:
        """Find texts similar to query text"""
        try:
            # Get embedding for query text
            query_embedding = await self.get_embedding(query_text)
            
            # Calculate similarities
            similarities = []
            for text, embedding in text_embeddings.items():
                similarity = self.calculate_similarity(query_embedding, embedding)
                
                if similarity >= threshold:
                    similarities.append({
                        'text': text,
                        'similarity': similarity,
                        'embedding': embedding
                    })
            
            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities
            
        except Exception as e:
            logger.error(f"❌ Error finding similar texts: {str(e)}")
            return []

# Convenience functions for easy usage
embedding_service = OllamaEmbeddingService()

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Convenience function to get embeddings"""
    async with OllamaEmbeddingService() as service:
        await service.initialize()
        return await service.get_embeddings(texts)

async def get_embedding(text: str) -> List[float]:
    """Convenience function to get single embedding"""
    async with OllamaEmbeddingService() as service:
        await service.initialize()
        return await service.get_embedding(text)

async def calculate_text_similarity(text1: str, text2: str) -> float:
    """Convenience function to calculate similarity between two texts"""
    async with OllamaEmbeddingService() as service:
        await service.initialize()
        
        embeddings = await service.get_embeddings([text1, text2])
        return service.calculate_similarity(embeddings[0], embeddings[1])

# Test function
async def test_embeddings():
    """Test the embedding service"""
    try:
        print("🧪 Testing Ollama embedding service...")
        
        async with OllamaEmbeddingService() as service:
            # Initialize service
            success = await service.initialize()
            if not success:
                print("❌ Failed to initialize embedding service")
                return
            
            # Test single embedding
            test_text = "Artificial intelligence is transforming the world"
            embedding = await service.get_embedding(test_text)
            print(f"✅ Generated embedding with {len(embedding)} dimensions")
            
            # Test similarity
            text1 = "Machine learning algorithms are powerful"
            text2 = "AI models can learn from data"
            text3 = "I love pizza and pasta"
            
            embeddings = await service.get_embeddings([text1, text2, text3])
            
            sim_12 = service.calculate_similarity(embeddings[0], embeddings[1])
            sim_13 = service.calculate_similarity(embeddings[0], embeddings[2])
            
            print(f"✅ Similarity between AI texts: {sim_12:.3f}")
            print(f"✅ Similarity between AI and food text: {sim_13:.3f}")
            
            print("🎉 Ollama embedding service test completed successfully!")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_embeddings())
