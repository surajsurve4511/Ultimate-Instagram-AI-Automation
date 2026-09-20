# 🚀 QUICK START GUIDE
## For Gemini API + Perplexity API + Local Ollama Setup

### 📋 STEP-BY-STEP SETUP

#### 1. 🔑 Get Your API Keys

**Gemini API Key:**
- Go to: https://aistudio.google.com/app/apikey
- Click "Create API Key" 
- Copy the key

**Perplexity API Key:**
- Go to: https://www.perplexity.ai/settings/api
- Since you have Perplexity Premium, you should see API access
- Generate a new API key
- Copy the key

#### 2. 🤖 Install Ollama (for local embeddings)

**Download Ollama:**
- Windows: https://ollama.com/download/windows
- Install and run it

**Install the embedding model:**
```bash
ollama pull nomic-embed-text
```

**Start Ollama server:**
```bash
ollama serve
```

#### 3. ⚙️ Configure Your Credentials

Edit the `.env` file in the project root and add your keys:

```env
# Your API Keys
GEMINI_API_KEY=your_actual_gemini_key_here
PERPLEXITY_API_KEY=your_actual_perplexity_key_here

# Your Instagram Account
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
```

#### 4. 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

#### 5. 🧪 Test Your Setup

**Test Ollama embeddings:**
```bash
python src/embeddings/ollama_service.py
```

**Test Perplexity research:**
```bash
python src/research/perplexity.py
```

#### 6. 🚀 Run the Ultimate System

```bash
python run_ultimate_automation.py
```

### 🎯 WHAT YOUR SYSTEM WILL DO

#### **With Gemini API:**
- Generate viral content with AI personas
- Create engaging captions and hooks
- Generate image prompts for posts
- Multi-modal content creation

#### **With Perplexity Premium:**
- Real-time trend research and analysis
- Competitor analysis and insights
- Fact-checking and content verification
- Advanced research for viral topics

#### **With Local Ollama:**
- Free embeddings for content deduplication
- Local AI processing (no external API costs)
- Content similarity detection
- Vector database operations

### 📊 EXPECTED RESULTS

**Performance Targets:**
- 📈 **15%+ Engagement Rate** (vs 1-3% industry average)
- 👥 **2000+ New Followers/Month**
- 🚀 **2.0x Viral Coefficient**
- 💾 **10%+ Save Rate**
- 🔄 **8%+ Share Rate**

### 🎪 CROWD ATTRACTION FEATURES

Your system includes 10 advanced crowd magnet strategies:

1. **🔮 Mystery Reveals** - "The AI secret that tech giants don't want you to know"
2. **👥 Exclusive Clubs** - Limited access communities with application process
3. **🏆 Viral Challenges** - "30-Day AI Mastery Challenge"
4. **🤫 Insider Access** - Behind-the-scenes content and industry secrets
5. **📺 Interactive Series** - Multi-part content journeys
6. **🎪 Community Building** - Engagement optimization and retention
7. **🎮 Gamification** - Points, badges, leaderboards
8. **⚡ Scarcity & Urgency** - Limited time offers and access
9. **🤝 User Collaboration** - Community-generated viral content
10. **🎬 Behind-the-Scenes** - Exclusive development insights

### 🛠️ TROUBLESHOOTING

**If Ollama isn't working:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama server
ollama serve

# Install the embedding model
ollama pull nomic-embed-text
```

**If Gemini API fails:**
- Check your API key in .env file
- Verify you have credits/quota available
- Check the API key permissions

**If Perplexity API fails:**
- Verify your Premium subscription includes API access
- Check your API key in .env file
- Monitor your usage limits

### 🎉 READY TO DOMINATE INSTAGRAM!

Once setup is complete, your system will:
- ✅ Automatically research trending AI topics
- ✅ Generate viral content with psychological triggers
- ✅ Create engaging multi-format posts
- ✅ Optimize posting times for maximum reach
- ✅ Build engaged communities through crowd attraction
- ✅ Scale to massive follower growth

**Your competitive advantage:**
- Premium AI research with Perplexity
- Advanced content generation with Gemini
- Free local embeddings with Ollama
- Revolutionary crowd psychology strategies
- Real-time trend adaptation
- ML-powered engagement optimization

🚀 **Let's make your Instagram account go viral!**
