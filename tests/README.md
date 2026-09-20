# Test Suite Documentation

## Overview
This folder contains all test files for the Instagram AI Automation system. Each test validates a specific component to ensure it works correctly before integration.

## Test Files

### 1. test_environment.py
**Purpose:** Verify all required packages and modules are installed  
**What it tests:**
- Python packages (google-generativeai, chromadb, instagrapi, etc.)
- Custom modules (config, embeddings, research, etc.)
- Environment variables (.env configuration)

**Run:** `python test_environment.py`

---

### 2. test_ollama.py
**Purpose:** Test local embedding generation using Ollama  
**What it tests:**
- Ollama server connectivity (localhost:11434)
- nomic-embed-text model availability
- Embedding generation for text
- Similarity calculations
- Similar text finding

**Prerequisites:** 
- Ollama must be installed
- Run `ollama serve` in a separate terminal
- Pull the model: `ollama pull nomic-embed-text`

**Run:** `python test_ollama.py`

---

### 3. test_perplexity.py
**Purpose:** Test AI-powered research using Perplexity API  
**What it tests:**
- API connectivity and authentication
- Trending topics research
- Content ideas generation
- Viral content pattern analysis
- Fact-checking capabilities

**Prerequisites:**
- Valid PERPLEXITY_API_KEY in .env file

**Run:** `python test_perplexity.py`

---

### 4. test_viral_content.py
**Purpose:** Test viral content generation strategies  
**What it tests:**
- 5 viral strategies (Controversy, Insider Secrets, Predictions, Challenges, Debunking)
- Hook generation
- Engagement prediction
- Content scoring
- Strategy effectiveness

**Prerequisites:**
- Valid GEMINI_API_KEY in .env file

**Run:** `python test_viral_content.py`

---

### 5. test_content_curator.py
**Purpose:** Test multi-source content curation  
**What it tests:**
- RSS feed parsing (TechCrunch, VentureBeat, etc.)
- Reddit content fetching
- Hacker News API integration
- Content filtering and scoring
- Source diversity

**Prerequisites:**
- Internet connection for API calls

**Run:** `python test_content_curator.py`

---

### 6. test_vector_store.py
**Purpose:** Test ChromaDB vector database with Ollama embeddings  
**What it tests:**
- Database initialization
- Content storage
- Duplicate detection
- Similar content finding
- Deduplication logic

**Prerequisites:**
- Ollama server running (`ollama serve`)
- nomic-embed-text model available

**Run:** `python test_vector_store.py`

---

## Running All Tests

### Option 1: Run Master Test Suite
```powershell
python run_all_tests.py
```

This will:
- Run all tests sequentially
- Show real-time output for each test
- Generate a comprehensive summary
- Report pass/fail status

### Option 2: Run Individual Tests
```powershell
cd tests
python test_environment.py
python test_ollama.py
python test_perplexity.py
python test_viral_content.py
python test_content_curator.py
python test_vector_store.py
```

## Prerequisites Before Testing

### 1. Install Dependencies
```powershell
conda activate aiav
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create `.env` file in the root directory:
```
GEMINI_API_KEY=your_gemini_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
```

### 3. Start Ollama Server
In a separate terminal:
```powershell
ollama serve
```

Then pull the embedding model:
```powershell
ollama pull nomic-embed-text
```

## Expected Results

✅ **All tests should pass with:**
- Environment test: 16/16 packages, 13/13 modules
- Ollama test: Embeddings generated, similarity calculations working
- Perplexity test: Research responses received, valid JSON format
- Viral content test: Content generated for all 5 strategies
- Content curator test: Content fetched from multiple sources
- Vector store test: Content stored, duplicates detected

## Troubleshooting

### Test Failures

**Ollama tests failing?**
- Ensure `ollama serve` is running
- Check if nomic-embed-text model is installed: `ollama list`
- Verify localhost:11434 is accessible

**Perplexity tests failing?**
- Check PERPLEXITY_API_KEY in .env
- Verify API key has credits remaining
- Check internet connection

**Viral content tests failing?**
- Check GEMINI_API_KEY in .env
- Verify API key is valid
- Check Gemini API quota

**Content curator tests failing?**
- Check internet connection
- Some RSS feeds may be temporarily unavailable
- Reddit API may have rate limits

**Vector store tests failing?**
- Ensure Ollama is running
- Check ChromaDB directory permissions
- Verify nomic-embed-text model availability

## Test Coverage

- ✅ Environment setup and dependencies
- ✅ Local AI embeddings (Ollama)
- ✅ Cloud AI research (Perplexity)
- ✅ Content generation (Gemini)
- ✅ Multi-source content curation
- ✅ Vector database and deduplication
- ⏳ Instagram posting (manual test required)
- ⏳ End-to-end automation flow

## Next Steps

After all tests pass:
1. Test Instagram posting manually (to avoid spam)
2. Run the complete automation system: `python run_ultimate_automation.py`
3. Monitor the dashboard for analytics
4. Review generated content quality
5. Adjust settings in `src/config/settings.py` as needed
