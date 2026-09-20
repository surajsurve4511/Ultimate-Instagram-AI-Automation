"""
Configuration settings for the Ultimate Instagram AI Automation System.

Rebuilt for:
- Gemini-only AI (no Perplexity, no Ollama)
- Official Instagram Graph API (no instagrapi)
- Multi-user product architecture

All configuration is loaded from environment variables via .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Centralized configuration for the automation system.
    All values come from environment variables with sensible defaults.
    """

    # ========== GEMINI AI CONFIGURATION ==========
    # Docs: https://ai.google.dev/gemini-api/docs
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Model selection — use best free-tier models
    # Reasoning model for content generation, strategy, analysis
    GEMINI_REASONING_MODEL: str = os.getenv("GEMINI_REASONING_MODEL", "gemini-2.5-flash")
    
    # Lite model for high-volume, low-cost tasks (hashtag scoring, quick checks)
    GEMINI_LITE_MODEL: str = os.getenv("GEMINI_LITE_MODEL", "gemini-2.5-flash-lite")
    
    # Image generation model (Nano Banana)
    # Docs: https://ai.google.dev/gemini-api/docs/image-generation
    GEMINI_IMAGE_MODEL: str = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    
    # Embeddings model for vector storage / memory
    # Docs: https://ai.google.dev/gemini-api/docs/models/gemini-embedding-001
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    
    # Temperature settings for different tasks
    GEMINI_CREATIVE_TEMPERATURE: float = float(os.getenv("GEMINI_CREATIVE_TEMPERATURE", "0.9"))
    GEMINI_ANALYSIS_TEMPERATURE: float = float(os.getenv("GEMINI_ANALYSIS_TEMPERATURE", "0.3"))
    GEMINI_DEFAULT_TEMPERATURE: float = float(os.getenv("GEMINI_DEFAULT_TEMPERATURE", "0.7"))
    GEMINI_MAX_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))
    
    # Rate limiting for Gemini API
    GEMINI_REQUESTS_PER_MINUTE: int = int(os.getenv("GEMINI_REQUESTS_PER_MINUTE", "15"))

    # ========== META / INSTAGRAM GRAPH API ==========
    # Docs: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api
    
    # Meta App credentials (from developers.facebook.com)
    META_APP_ID: str = os.getenv("META_APP_ID", "")
    META_APP_SECRET: str = os.getenv("META_APP_SECRET", "")
    
    # Instagram Graph API host
    INSTAGRAM_GRAPH_API_HOST: str = "https://graph.instagram.com"
    INSTAGRAM_GRAPH_API_VERSION: str = os.getenv("INSTAGRAM_GRAPH_API_VERSION", "v25.0")
    
    # Rate limit: 100 API-published posts per 24 hours per account
    INSTAGRAM_MAX_POSTS_PER_DAY: int = int(os.getenv("INSTAGRAM_MAX_POSTS_PER_DAY", "3"))
    
    # Public URL where generated images are served for Instagram to fetch
    # Instagram cURLs the image_url, so it must be publicly accessible
    MEDIA_UPLOAD_BASE_URL: str = os.getenv("MEDIA_UPLOAD_BASE_URL", "http://localhost:8000/media")

    # ========== DATABASE ==========
    
    # SQLite for development, PostgreSQL for production
    # SQLite async: sqlite+aiosqlite:///./data/automation.db
    # PostgreSQL:   postgresql+asyncpg://user:pass@host/dbname
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./data/automation.db"
    )
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"

    # ========== AUTHENTICATION ==========
    
    # JWT secret for multi-user auth (CHANGE THIS IN PRODUCTION!)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-secret-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", "24"))
    
    # Fernet key for encrypting stored access tokens
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")

    # ========== STORAGE PATHS ==========
    
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")
    CONTENT_STORAGE_PATH: str = os.getenv("CONTENT_STORAGE_PATH", "./data/content")
    IMAGES_STORAGE_PATH: str = os.getenv("IMAGES_STORAGE_PATH", "./data/images")

    # ========== CONTENT DEFAULTS ==========
    
    # Default posting schedule (can be overridden per user)
    DEFAULT_POSTING_TIMES: list = ["09:00", "14:00", "18:00"]
    DEFAULT_POSTING_DAYS: list = [0, 1, 2, 3, 4]  # Mon-Fri
    DEFAULT_POSTS_PER_DAY: int = 3
    
    # Content quality threshold (0-1)
    MIN_QUALITY_SCORE: float = float(os.getenv("MIN_QUALITY_SCORE", "0.7"))
    
    # Default funnel distribution
    DEFAULT_FUNNEL_DISTRIBUTION: dict = {
        "TOFU": 0.40,
        "MOFU": 0.30,
        "BOFU": 0.15,
        "RETENTION": 0.15,
    }

    # ========== APPLICATION ==========
    
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ========== VALIDATION ==========

    @classmethod
    def validate_required(cls) -> list[str]:
        """
        Validate that critical settings are present.
        Returns list of missing settings (empty = all good).
        """
        required = {
            "GEMINI_API_KEY": cls.GEMINI_API_KEY,
        }
        
        missing = [name for name, value in required.items() if not value]
        return missing

    @classmethod
    def validate_instagram_ready(cls) -> list[str]:
        """
        Validate settings needed for Instagram publishing.
        These aren't required at startup, but are needed before publishing.
        """
        required = {
            "META_APP_ID": cls.META_APP_ID,
            "META_APP_SECRET": cls.META_APP_SECRET,
        }
        
        missing = [name for name, value in required.items() if not value]
        return missing

    @classmethod
    def create_directories(cls) -> None:
        """Create all required storage directories."""
        directories = [
            cls.CONTENT_STORAGE_PATH,
            cls.IMAGES_STORAGE_PATH,
            cls.CHROMA_PERSIST_DIRECTORY,
            "./logs",
            "./data",
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_gemini_config(cls) -> dict:
        """Get Gemini AI configuration dictionary."""
        return {
            "api_key": cls.GEMINI_API_KEY,
            "reasoning_model": cls.GEMINI_REASONING_MODEL,
            "lite_model": cls.GEMINI_LITE_MODEL,
            "image_model": cls.GEMINI_IMAGE_MODEL,
            "embedding_model": cls.GEMINI_EMBEDDING_MODEL,
            "creative_temperature": cls.GEMINI_CREATIVE_TEMPERATURE,
            "analysis_temperature": cls.GEMINI_ANALYSIS_TEMPERATURE,
            "default_temperature": cls.GEMINI_DEFAULT_TEMPERATURE,
            "max_tokens": cls.GEMINI_MAX_TOKENS,
        }


# ========== Global Instance ==========

SETTINGS = Settings()

# Create directories on import
SETTINGS.create_directories()

# Validate critical settings
_missing = SETTINGS.validate_required()
if _missing:
    print(f"[WARNING] Missing required settings: {', '.join(_missing)}")
    print("[INFO] Please check your .env file.")
else:
    print("[OK] Configuration loaded successfully!")
