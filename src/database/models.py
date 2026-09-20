"""
Database models for the Ultimate Instagram AI Automation System.
Multi-user architecture with per-account brain, content, and analytics.

Uses SQLAlchemy 2.0+ async-compatible declarative models.
Docs: https://docs.sqlalchemy.org/en/20/orm/quickstart.html
"""

import enum
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, Enum, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)


# ========== Base ==========

class Base(DeclarativeBase):
    """Base class for all models"""
    pass


# ========== Enums ==========

class ContentType(str, enum.Enum):
    """Instagram content types supported by Graph API"""
    IMAGE = "IMAGE"
    CAROUSEL = "CAROUSEL"
    REELS = "REELS"
    STORIES = "STORIES"


class ContentStatus(str, enum.Enum):
    """Content lifecycle status"""
    DRAFT = "DRAFT"              # Generated, not yet approved
    APPROVED = "APPROVED"        # Approved for scheduling
    SCHEDULED = "SCHEDULED"      # Placed on content calendar
    UPLOADING = "UPLOADING"      # Image being uploaded to media host
    CONTAINER_CREATED = "CONTAINER_CREATED"  # IG container created
    PUBLISHING = "PUBLISHING"    # Publish request sent
    PUBLISHED = "PUBLISHED"      # Successfully published to Instagram
    FAILED = "FAILED"            # Publishing failed
    ARCHIVED = "ARCHIVED"        # Removed from active use


class FunnelStage(str, enum.Enum):
    """Marketing funnel stages"""
    TOFU = "TOFU"          # Top of Funnel — awareness, reach
    MOFU = "MOFU"          # Middle of Funnel — engagement, education
    BOFU = "BOFU"          # Bottom of Funnel — conversion, action
    RETENTION = "RETENTION"  # Retention — community, loyalty


# ========== User & Auth Models ==========

class User(Base):
    """
    Application user (the person running the automation).
    One user can manage multiple Instagram accounts.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    instagram_accounts: Mapped[List["InstagramAccount"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class InstagramAccount(Base):
    """
    An Instagram Business/Creator account connected via Meta OAuth.
    Stores Graph API credentials and account metadata.

    Ref: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api
    """
    __tablename__ = "instagram_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Instagram Graph API identifiers
    ig_user_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    facebook_page_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # OAuth tokens (encrypted with Fernet before storage)
    encrypted_access_token: Mapped[str] = mapped_column(Text, nullable=False)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Account metadata
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_username: Mapped[Optional[str]] = mapped_column(String(100))
    niche_description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="instagram_accounts")
    profile: Mapped[Optional["UserProfile"]] = relationship(
        back_populates="instagram_account", cascade="all, delete-orphan", uselist=False
    )
    generated_content: Mapped[List["GeneratedContent"]] = relationship(
        back_populates="instagram_account", cascade="all, delete-orphan"
    )
    published_posts: Mapped[List["PublishedPost"]] = relationship(
        back_populates="instagram_account", cascade="all, delete-orphan"
    )
    calendar_entries: Mapped[List["ContentCalendarEntry"]] = relationship(
        back_populates="instagram_account", cascade="all, delete-orphan"
    )
    knowledge_entries: Mapped[List["KnowledgeEntry"]] = relationship(
        back_populates="instagram_account", cascade="all, delete-orphan"
    )
    trend_snapshots: Mapped[List["TrendSnapshot"]] = relationship(
        back_populates="instagram_account", cascade="all, delete-orphan"
    )


# ========== User Brain Models ==========

class UserProfile(Base):
    """
    The 'brain context' for an Instagram account.
    Describes brand voice, audience, goals — used as context in every Gemini call.
    """
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instagram_account_id: Mapped[int] = mapped_column(
        ForeignKey("instagram_accounts.id"), unique=True, nullable=False
    )

    # Brand identity (generated by Gemini from user's description)
    brand_voice: Mapped[Optional[str]] = mapped_column(Text)  # e.g., "Professional but approachable, tech-savvy educator"
    content_pillars: Mapped[Optional[dict]] = mapped_column(JSON)  # e.g., ["AI tutorials", "tool reviews", "industry news"]
    target_audience: Mapped[Optional[str]] = mapped_column(Text)  # e.g., "Aspiring AI engineers, age 20-35"
    tone_keywords: Mapped[Optional[list]] = mapped_column(JSON)  # e.g., ["innovative", "helpful", "cutting-edge"]
    forbidden_words: Mapped[Optional[list]] = mapped_column(JSON)  # Words to never use
    emoji_style: Mapped[Optional[str]] = mapped_column(String(50))  # e.g., "moderate", "heavy", "minimal"

    # Goals
    primary_goal: Mapped[Optional[str]] = mapped_column(Text)  # e.g., "Grow to 10K followers in 3 months"
    follower_target: Mapped[Optional[int]] = mapped_column(Integer)
    engagement_target: Mapped[Optional[float]] = mapped_column(Float)  # Target engagement rate %
    posting_frequency: Mapped[int] = mapped_column(Integer, default=3)  # Posts per day

    # Funnel distribution (overrides defaults)
    funnel_distribution: Mapped[Optional[dict]] = mapped_column(JSON)  # e.g., {"TOFU": 0.4, "MOFU": 0.3, ...}

    # Strategy notes (updated by the AI over time)
    strategy_notes: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    instagram_account: Mapped["InstagramAccount"] = relationship(back_populates="profile")


class KnowledgeEntry(Base):
    """
    Long-term memory entry for an Instagram account.
    Knowledge the AI has learned about the account's niche, audience, and patterns.
    Stored with Gemini embeddings in ChromaDB for similarity search.
    """
    __tablename__ = "knowledge_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instagram_account_id: Mapped[int] = mapped_column(
        ForeignKey("instagram_accounts.id"), nullable=False, index=True
    )

    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(255))  # Where this knowledge came from
    embedding_id: Mapped[Optional[str]] = mapped_column(String(255))  # ChromaDB document ID
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    instagram_account: Mapped["InstagramAccount"] = relationship(back_populates="knowledge_entries")

    __table_args__ = (
        Index("ix_knowledge_account_topic", "instagram_account_id", "topic"),
    )


# ========== Content Models ==========

class GeneratedContent(Base):
    """
    Content generated by the AI system.
    Tracks the full lifecycle from DRAFT → PUBLISHED.
    """
    __tablename__ = "generated_content"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instagram_account_id: Mapped[int] = mapped_column(
        ForeignKey("instagram_accounts.id"), nullable=False, index=True
    )

    # Content
    caption: Mapped[str] = mapped_column(Text, nullable=False)
    hashtags: Mapped[Optional[list]] = mapped_column(JSON)  # List of hashtags
    call_to_action: Mapped[Optional[str]] = mapped_column(Text)
    alt_text: Mapped[Optional[str]] = mapped_column(Text)  # Accessibility

    # Media
    content_type: Mapped[ContentType] = mapped_column(
        Enum(ContentType), default=ContentType.IMAGE
    )
    image_paths: Mapped[Optional[list]] = mapped_column(JSON)  # Local paths to generated images
    image_urls: Mapped[Optional[list]] = mapped_column(JSON)  # Public URLs after upload
    image_prompt: Mapped[Optional[str]] = mapped_column(Text)  # The prompt used for image gen

    # Strategy
    funnel_stage: Mapped[Optional[FunnelStage]] = mapped_column(Enum(FunnelStage))
    topic: Mapped[Optional[str]] = mapped_column(String(500))
    content_category: Mapped[Optional[str]] = mapped_column(String(100))
    psychology_trigger: Mapped[Optional[str]] = mapped_column(String(100))

    # Quality
    quality_score: Mapped[Optional[float]] = mapped_column(Float)  # AI-assessed quality 0-1
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus), default=ContentStatus.DRAFT, index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    instagram_account: Mapped["InstagramAccount"] = relationship(back_populates="generated_content")
    published_post: Mapped[Optional["PublishedPost"]] = relationship(
        back_populates="generated_content", uselist=False
    )


class PublishedPost(Base):
    """
    A post that was successfully published to Instagram via Graph API.

    Ref: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/content-publishing
    """
    __tablename__ = "published_posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instagram_account_id: Mapped[int] = mapped_column(
        ForeignKey("instagram_accounts.id"), nullable=False, index=True
    )
    generated_content_id: Mapped[int] = mapped_column(
        ForeignKey("generated_content.id"), nullable=False, unique=True
    )

    # Instagram Graph API data
    ig_media_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    ig_container_id: Mapped[Optional[str]] = mapped_column(String(100))
    permalink: Mapped[Optional[str]] = mapped_column(String(500))

    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    instagram_account: Mapped["InstagramAccount"] = relationship(back_populates="published_posts")
    generated_content: Mapped["GeneratedContent"] = relationship(back_populates="published_post")
    metrics: Mapped[List["PostMetrics"]] = relationship(
        back_populates="published_post", cascade="all, delete-orphan"
    )


class PostMetrics(Base):
    """
    Engagement metrics for a published post.
    Fetched from Instagram Insights API at intervals (e.g., 24h, 7d after posting).

    Ref: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-media/insights
    """
    __tablename__ = "post_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    published_post_id: Mapped[int] = mapped_column(
        ForeignKey("published_posts.id"), nullable=False, index=True
    )

    # Engagement metrics
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    saves: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    reach: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)

    # Engagement rate = (likes + comments + saves + shares) / reach
    engagement_rate: Mapped[Optional[float]] = mapped_column(Float)

    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    published_post: Mapped["PublishedPost"] = relationship(back_populates="metrics")


# ========== Scheduling Models ==========

class ContentCalendarEntry(Base):
    """
    A slot in the content calendar.
    Can be empty (needs content generation) or linked to generated content.
    """
    __tablename__ = "content_calendar"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instagram_account_id: Mapped[int] = mapped_column(
        ForeignKey("instagram_accounts.id"), nullable=False, index=True
    )

    # Schedule
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    content_type: Mapped[ContentType] = mapped_column(
        Enum(ContentType), default=ContentType.IMAGE
    )
    funnel_stage: Mapped[Optional[FunnelStage]] = mapped_column(Enum(FunnelStage))

    # Topic suggestion (populated before content generation)
    suggested_topic: Mapped[Optional[str]] = mapped_column(String(500))

    # Link to content (populated after generation)
    generated_content_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("generated_content.id")
    )

    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    instagram_account: Mapped["InstagramAccount"] = relationship(back_populates="calendar_entries")

    __table_args__ = (
        Index("ix_calendar_schedule", "instagram_account_id", "scheduled_at"),
    )


# ========== Research Models ==========

class TrendSnapshot(Base):
    """
    Captured trend data at a point in time.
    Populated by Gemini + Google Search grounding.
    """
    __tablename__ = "trend_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instagram_account_id: Mapped[int] = mapped_column(
        ForeignKey("instagram_accounts.id"), nullable=False, index=True
    )

    trend_name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.5)
    suggested_angles: Mapped[Optional[list]] = mapped_column(JSON)  # Content angle ideas
    source_urls: Mapped[Optional[list]] = mapped_column(JSON)  # Source references
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)

    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    instagram_account: Mapped["InstagramAccount"] = relationship(back_populates="trend_snapshots")
