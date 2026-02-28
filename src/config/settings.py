"""
Configuration settings for the Ultimate Instagram AI Automation System.
Upgraded for Gemini 2.0 Flash, marketing psychology engine,
and advanced content pipeline.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Settings:
    """Configuration settings for the automation system"""
    
    # ========== API CREDENTIALS ==========
    
    # Gemini AI (Primary AI for content generation)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Perplexity API (Premium research and trend analysis)
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    
    # Instagram credentials
    INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
    INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
    
    # ========== LOCAL AI MODELS ==========
    
    # Ollama configuration for local embeddings
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_EMBEDDING_MODEL = os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
    
    # ========== DATABASE & STORAGE ==========
    
    # ChromaDB configuration
    CHROMA_PERSIST_DIRECTORY = os.getenv('CHROMA_PERSIST_DIRECTORY', './data/chroma_db')
    
    # Content storage
    CONTENT_STORAGE_PATH = os.getenv('CONTENT_STORAGE_PATH', './data/content')
    IMAGES_STORAGE_PATH = os.getenv('IMAGES_STORAGE_PATH', './data/images')
    
    # ========== CONTENT SETTINGS ==========
    
    # Quality filters
    MIN_ENGAGEMENT_SCORE = float(os.getenv('MIN_ENGAGEMENT_SCORE', '0.7'))
    MAX_CONTENT_AGE_DAYS = int(os.getenv('MAX_CONTENT_AGE_DAYS', '7'))
    
    # Content generation
    MAX_POSTS_PER_DAY = int(os.getenv('MAX_POSTS_PER_DAY', '3'))
    MIN_TIME_BETWEEN_POSTS = int(os.getenv('MIN_TIME_BETWEEN_POSTS', '4'))  # hours
    
    # ========== AI MODEL CONFIGURATIONS ==========
    
    # Gemini model settings (Upgraded to 2.0 Flash)
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
    GEMINI_TEMPERATURE = float(os.getenv('GEMINI_TEMPERATURE', '0.7'))
    GEMINI_MAX_TOKENS = int(os.getenv('GEMINI_MAX_TOKENS', '4096'))
    GEMINI_CREATIVE_TEMPERATURE = float(os.getenv('GEMINI_CREATIVE_TEMPERATURE', '0.9'))
    GEMINI_ANALYSIS_TEMPERATURE = float(os.getenv('GEMINI_ANALYSIS_TEMPERATURE', '0.3'))
    
    # Perplexity model settings
    PERPLEXITY_MODEL = os.getenv('PERPLEXITY_MODEL', 'llama-3.1-sonar-huge-128k-online')
    PERPLEXITY_TEMPERATURE = float(os.getenv('PERPLEXITY_TEMPERATURE', '0.3'))
    PERPLEXITY_MAX_TOKENS = int(os.getenv('PERPLEXITY_MAX_TOKENS', '1024'))
    
    # ========== TREND DETECTION ==========
    
    # Available trend sources (no API keys required)
    TREND_SOURCES = {
        'google_trends': True,  # No API key needed
        'reddit_trending': True,  # Using public API
        'hacker_news': True,  # Public API
        'github_trending': True,  # Public API
        'perplexity_research': True,  # Using your Perplexity API
    }
    
    # ========== POSTING SCHEDULE ==========
    
    # Optimal posting times (24-hour format)
    POSTING_TIMES = [
        '09:00',  # Morning engagement
        '14:00',  # Afternoon peak
        '18:00',  # Evening prime time
    ]
    
    # Days of week to post (0=Monday, 6=Sunday)
    POSTING_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday
    
    # ========== SAFETY & RATE LIMITING ==========
    
    # Instagram rate limiting
    MAX_ACTIONS_PER_HOUR = int(os.getenv('MAX_ACTIONS_PER_HOUR', '10'))
    DELAY_BETWEEN_ACTIONS = int(os.getenv('DELAY_BETWEEN_ACTIONS', '30'))  # seconds
    
    # API rate limiting
    GEMINI_REQUESTS_PER_MINUTE = int(os.getenv('GEMINI_REQUESTS_PER_MINUTE', '15'))
    PERPLEXITY_REQUESTS_PER_MINUTE = int(os.getenv('PERPLEXITY_REQUESTS_PER_MINUTE', '20'))
    
    # ========== CONTENT CATEGORIES ==========
    
    CONTENT_CATEGORIES = {
        'ai_news': {
            'weight': 0.25,  # 25% of content
            'hashtags': ['#AI', '#MachineLearning', '#AINews', '#TechNews', '#Innovation'],
            'funnel_stage': 'tofu'
        },
        'ai_education': {
            'weight': 0.25,  # 25% of content
            'hashtags': ['#AILearning', '#MachineLearning', '#TechEducation', '#AITutorial', '#LearnAI'],
            'funnel_stage': 'mofu'
        },
        'ai_tools': {
            'weight': 0.20,  # 20% of content
            'hashtags': ['#AITools', '#ProductivityAI', '#AIApps', '#TechTools', '#AIProductivity'],
            'funnel_stage': 'bofu'
        },
        'ai_careers': {
            'weight': 0.10,  # 10% of content
            'hashtags': ['#AICareers', '#TechJobs', '#AIJobs', '#MachineLearningJobs', '#TechCareer'],
            'funnel_stage': 'bofu'
        },
        'viral_content': {
            'weight': 0.15,  # 15% viral for growth
            'hashtags': ['#AIFuture', '#TechTrends', '#Innovation', '#FutureofAI', '#TechLife'],
            'funnel_stage': 'tofu'
        },
        'community': {
            'weight': 0.05,  # 5% community retention
            'hashtags': ['#AIMultiverse', '#AICommunity', '#TechCommunity', '#LearnTogether'],
            'funnel_stage': 'retention'
        }
    }
    
    # ========== MARKETING PSYCHOLOGY ==========
    
    # Cialdini's 6 principles — weight distribution for content
    PSYCHOLOGY_TRIGGERS = {
        'reciprocity': 0.20,       # Give value first → they engage back
        'commitment': 0.10,        # Small public pledges → build loyalty
        'social_proof': 0.25,      # Show community engagement → attract more
        'authority': 0.20,         # Expert positioning → trust
        'liking': 0.10,            # Relatable personas → connection
        'scarcity': 0.15,          # Limited access → urgency
    }
    
    # Sales funnel content distribution
    FUNNEL_DISTRIBUTION = {
        'tofu': 0.40,    # Top of funnel: awareness, reach (40%)
        'mofu': 0.30,    # Middle: engagement, education (30%)
        'bofu': 0.15,    # Bottom: conversion, action (15%)
        'retention': 0.15 # Retention: community, loyalty (15%)
    }
    
    # ========== A/B TESTING ==========
    
    AB_TEST_ENABLED = os.getenv('AB_TEST_ENABLED', 'true').lower() == 'true'
    AB_TEST_MIN_SAMPLE_SIZE = int(os.getenv('AB_TEST_MIN_SAMPLE_SIZE', '100'))
    AB_TEST_CONFIDENCE_LEVEL = float(os.getenv('AB_TEST_CONFIDENCE_LEVEL', '0.95'))
    
    # ========== CAMPAIGN MANAGEMENT ==========
    
    MAX_ACTIVE_CAMPAIGNS = int(os.getenv('MAX_ACTIVE_CAMPAIGNS', '3'))
    DEFAULT_CAMPAIGN_DURATION = int(os.getenv('DEFAULT_CAMPAIGN_DURATION', '7'))
    CAMPAIGN_STORAGE_PATH = os.getenv('CAMPAIGN_STORAGE_PATH', './data/campaigns')
    
    # ========== VALIDATION ==========
    
    @classmethod
    def validate_required_settings(cls):
        """Validate that all required settings are present"""
        required_settings = [
            'GEMINI_API_KEY',
            'PERPLEXITY_API_KEY',
            'INSTAGRAM_USERNAME',
            'INSTAGRAM_PASSWORD'
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not getattr(cls, setting):
                missing_settings.append(setting)
        
        if missing_settings:
            raise ValueError(f"Missing required settings: {', '.join(missing_settings)}")
        
        return True
    
    @classmethod
    def get_ai_config(cls):
        """Get AI configuration for content generation"""
        return {
            'gemini': {
                'api_key': cls.GEMINI_API_KEY,
                'model': cls.GEMINI_MODEL,
                'temperature': cls.GEMINI_TEMPERATURE,
                'max_tokens': cls.GEMINI_MAX_TOKENS
            },
            'perplexity': {
                'api_key': cls.PERPLEXITY_API_KEY,
                'model': cls.PERPLEXITY_MODEL,
                'temperature': cls.PERPLEXITY_TEMPERATURE,
                'max_tokens': cls.PERPLEXITY_MAX_TOKENS
            },
            'ollama': {
                'base_url': cls.OLLAMA_BASE_URL,
                'embedding_model': cls.OLLAMA_EMBEDDING_MODEL
            }
        }
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        directories = [
            cls.CONTENT_STORAGE_PATH,
            cls.IMAGES_STORAGE_PATH,
            cls.CHROMA_PERSIST_DIRECTORY,
            cls.CAMPAIGN_STORAGE_PATH,
            './logs',
            './data',
            './data/ab_tests',
            './data/campaigns',
            './data/analytics',
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

# Create global settings instance
SETTINGS = Settings()

# Validate settings on import
try:
    SETTINGS.validate_required_settings()
    SETTINGS.create_directories()
    print("✅ Configuration loaded successfully!")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    print("📝 Please check your .env file and ensure all required API keys are set.")
