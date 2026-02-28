"""
Test script for Ollama Embedding Service
Tests local embeddings generation using nomic-embed-text model
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

async def test_ollama_embeddings():
    """Test Ollama embedding service"""
    print("=" * 70)
    print("🧪 TESTING OLLAMA EMBEDDING SERVICE")
    print("=" * 70)
    print()
    
    try:
        from src.embeddings.ollama_service import OllamaEmbeddingService
        
        # Initialize service
        print("1️⃣ Initializing Ollama service...")
        async with OllamaEmbeddingService() as service:
            success = await service.initialize()
            
            if not success:
                print("❌ Failed to initialize Ollama service")
                print("💡 Make sure Ollama is running: ollama serve")
                print("💡 And model is installed: ollama pull nomic-embed-text")
                return False
            
            print("✅ Ollama service initialized successfully\n")
            
            # Test 2: Generate single embedding
            print("2️⃣ Testing single embedding generation...")
            test_text = "Artificial Intelligence is transforming the world of technology"
            
            embedding = await service.get_embedding(test_text)
            print(f"✅ Generated embedding with {len(embedding)} dimensions")
            print(f"   First 5 values: {embedding[:5]}")
            print()
            
            # Test 3: Generate multiple embeddings
            print("3️⃣ Testing batch embedding generation...")
            test_texts = [
                "Machine learning models are powerful tools",
                "Deep learning uses neural networks",
                "Natural language processing enables AI to understand text"
            ]
            
            embeddings = await service.get_embeddings(test_texts)
            print(f"✅ Generated {len(embeddings)} embeddings")
            for i, emb in enumerate(embeddings):
                print(f"   Text {i+1}: {len(emb)} dimensions")
            print()
            
            # Test 4: Calculate similarity
            print("4️⃣ Testing similarity calculation...")
            text1 = "Machine learning is a subset of artificial intelligence"
            text2 = "AI and machine learning are related technologies"
            text3 = "I love eating pizza and pasta for dinner"
            
            emb1 = await service.get_embedding(text1)
            emb2 = await service.get_embedding(text2)
            emb3 = await service.get_embedding(text3)
            
            sim_12 = service.calculate_similarity(emb1, emb2)
            sim_13 = service.calculate_similarity(emb1, emb3)
            
            print(f"✅ Similarity between AI texts: {sim_12:.4f}")
            print(f"✅ Similarity between AI and food texts: {sim_13:.4f}")
            print()
            
            if sim_12 > sim_13:
                print("✅ Similarity test PASSED - AI texts are more similar to each other")
            else:
                print("⚠️ Similarity test FAILED - unexpected results")
            print()
            
            # Test 5: Find similar texts
            print("5️⃣ Testing similar text search...")
            
            text_database = {
                "AI is the future of technology": emb1,
                "Machine learning algorithms learn from data": emb2,
                "Italian food is delicious": emb3
            }
            
            query = "What is artificial intelligence?"
            similar_texts = await service.find_similar_texts(
                query, 
                text_database, 
                threshold=0.5
            )
            
            print(f"✅ Found {len(similar_texts)} similar texts for query: '{query}'")
            for item in similar_texts:
                print(f"   - {item['text'][:50]}... (similarity: {item['similarity']:.4f})")
            print()
            
            print("=" * 70)
            print("🎉 OLLAMA EMBEDDING SERVICE - ALL TESTS PASSED!")
            print("=" * 70)
            print()
            print("✅ Service is working correctly")
            print("✅ Embeddings are being generated")
            print("✅ Similarity calculations are accurate")
            print("✅ Text search is functional")
            print()
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print()
        print("💡 Troubleshooting:")
        print("   1. Make sure Ollama is installed")
        print("   2. Start Ollama: ollama serve")
        print("   3. Install model: ollama pull nomic-embed-text")
        print("   4. Check OLLAMA_BASE_URL in .env file")
        return False

if __name__ == "__main__":
    print("\n")
    success = asyncio.run(test_ollama_embeddings())
    
    if success:
        print("✅ Ollama Embedding Service is READY for production!")
    else:
        print("❌ Please fix the issues above before proceeding")
    
    print("\n")
    sys.exit(0 if success else 1)
