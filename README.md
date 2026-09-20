# 🚀 InstaAutomate — AI-Powered Instagram Automation

> Multi-user SaaS product that uses Gemini AI to research trends, generate content (text + images), schedule, and publish to Instagram — all via official APIs.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your .env file
cp .env.example .env
# Add your GEMINI_API_KEY (required), META_APP_ID/SECRET (for publishing)

# 3. Initialize the database
alembic upgrade head

# 4. Start the server
python -m uvicorn src.api.main:app --reload

# 5. Open the dashboard
# → http://localhost:8000
```

## Architecture

```
src/
├── ai/                    # Gemini brain (ALL AI calls)
│   ├── gemini_brain.py    # 15 methods: text, image, search, embeddings, function calling
│   ├── prompts.py         # All system prompts
│   └── schemas.py         # Structured output schemas
├── analytics/             # Performance tracking
│   ├── analytics_engine.py
│   ├── insights_collector.py   # Instagram Graph API metrics
│   ├── marketing_engine.py
│   ├── performance_analyzer.py # Gemini-powered pattern analysis
│   └── report_generator.py     # Weekly/monthly AI reports
├── api/                   # FastAPI backend (10 routers)
│   ├── main.py
│   └── routes/            # auth, accounts, profile, content, calendar,
│                          # campaigns, instagram, analytics
├── auth/                  # JWT authentication
├── brain/                 # Per-user AI intelligence
│   ├── user_brain.py      # Profile understanding, conversation history
│   ├── memory_store.py    # ChromaDB long-term memory
│   └── goal_tracker.py    # Goal tracking & progress
├── config/settings.py     # Environment-based config
├── content_gen/           # Content creation pipeline
│   ├── text_generator.py  # Captions, hashtags, CTAs
│   ├── image_generator.py # Nano Banana image gen
│   ├── carousel_builder.py
│   └── content_factory.py # Full pipeline + quality check
├── core/logging_config.py # Advanced logging system
├── database/              # SQLAlchemy + Alembic (9 tables)
├── instagram/             # Official Instagram Graph API
│   ├── graph_api_client.py
│   ├── auth_flow.py       # Meta OAuth2
│   └── media_host.py      # Public URL hosting
├── marketing/             # Marketing psychology
│   ├── funnel_mapper.py   # TOFU/MOFU/BOFU classification
│   └── campaign_engine.py # Multi-day campaigns
├── research/              # Trend & niche research
│   ├── trend_engine.py    # Google Search grounding
│   └── niche_researcher.py
└── scheduler/             # APScheduler background jobs
    ├── content_calendar.py
    ├── publisher.py
    └── job_runner.py

frontend/                  # Dashboard UI (HTML + CSS + JS)
├── index.html
├── styles.css             # Dark theme design system
└── app.js                 # SPA with 5 pages
```

## Tech Stack

| Layer | Technology |
|---|---|
| **AI** | Gemini 2.5 Flash (reasoning) + Flash-Lite (bulk) + Nano Banana (images) |
| **Web Research** | Gemini + Google Search Grounding |
| **Embeddings** | Gemini Embeddings (gemini-embedding-001) |
| **Instagram** | Official Instagram Graph API |
| **Backend** | FastAPI + SQLAlchemy + Alembic |
| **Scheduler** | APScheduler (3 background jobs) |
| **Vector DB** | ChromaDB (per-user collections) |
| **Frontend** | Vanilla HTML/CSS/JS (dark theme SPA) |

## Environment Variables

```env
# Required
GEMINI_API_KEY=your_gemini_api_key

# Instagram (for publishing)
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret

# Auth & Security
JWT_SECRET=generate_with_secrets_token_hex
ENCRYPTION_KEY=generate_with_fernet

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/automation.db
```

## API Endpoints

| Group | Prefix | Endpoints |
|---|---|---|
| Auth | `/api/auth` | register, login |
| Accounts | `/api/accounts` | connect-url, callback, refresh-token, verify |
| Profile | `/api/profile` | set-profile, get-profile, update, analyze, learn, adapt-voice |
| Content | `/api/content` | generate, suggest-topics |
| Calendar | `/api/calendar` | entries, generate-week |
| Campaigns | `/api/campaigns` | create, classify-topic, analyze-distribution, plan-week |
| Instagram | `/api/instagram` | publish, status |
| Analytics | `/api/analytics` | report, insights |
| System | `/health`, `/debug/errors` | health check, error tracking |

Full API docs at `http://localhost:8000/docs` (Swagger UI)

## License

MIT
