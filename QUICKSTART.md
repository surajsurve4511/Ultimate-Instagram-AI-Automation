# Instagram AI Content Automation

## Quick Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Setup Environment
```bash
cp src/config/.env.example .env
# Edit .env with your API keys
```

### Run System

#### Manual Content Generation
```bash
python main.py run
```

#### Start Automated Scheduler  
```bash
python main.py schedule
```

#### Launch Web Dashboard
```bash
python main.py dashboard
```

#### Emergency Post
```bash
python main.py post --topic "Breaking AI News"
```

#### View Statistics
```bash
python main.py stats
```

### Dashboard Access
- URL: http://localhost:5000
- Features: System monitoring, manual posting, analytics

### Required API Keys
- GEMINI_API_KEY: Google Gemini API
- INSTAGRAM_USERNAME: Instagram account
- INSTAGRAM_PASSWORD: Instagram password
- OPENAI_API_KEY: For embeddings (optional)

### Content Sources
- TechCrunch AI, VentureBeat AI
- Reddit r/MachineLearning, r/artificial  
- Coursera, Product Hunt, GitHub Trending
- AI news sites and educational platforms

### Features
✅ Multi-source content scraping  
✅ AI-powered quality filtering  
✅ Vector database deduplication  
✅ Gemini content generation  
✅ Automated Instagram posting  
✅ Smart scheduling system  
✅ Performance analytics  
✅ Web dashboard monitoring  

Built for intelligent AI education content automation 🤖✨
