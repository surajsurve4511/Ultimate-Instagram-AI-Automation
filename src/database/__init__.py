"""
Database package for the Instagram AI Automation System.

Exports the key components needed by the rest of the application:
- Base: SQLAlchemy declarative base for model definitions
- All model classes for imports
- get_session: async context manager for database sessions
- get_db_session: FastAPI dependency for database sessions
- init_db: create all tables (development use)
"""

from src.database.models import (
    Base,
    User,
    InstagramAccount,
    UserProfile,
    KnowledgeEntry,
    GeneratedContent,
    PublishedPost,
    PostMetrics,
    ContentCalendarEntry,
    TrendSnapshot,
    ContentType,
    ContentStatus,
    FunnelStage,
)
from src.database.connection import (
    get_session,
    get_db_session,
    init_db,
    drop_db,
    engine,
)

__all__ = [
    # Base
    "Base",
    # Models
    "User",
    "InstagramAccount",
    "UserProfile",
    "KnowledgeEntry",
    "GeneratedContent",
    "PublishedPost",
    "PostMetrics",
    "ContentCalendarEntry",
    "TrendSnapshot",
    # Enums
    "ContentType",
    "ContentStatus",
    "FunnelStage",
    # Database utilities
    "get_session",
    "get_db_session",
    "init_db",
    "drop_db",
    "engine",
]
