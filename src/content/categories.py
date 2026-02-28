"""
Content categories and sources for AI education Instagram account.
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional

class ContentCategory(Enum):
    AI_NEWS = "ai_news"
    EDUCATION = "education"
    OPPORTUNITIES = "opportunities"
    TOOLS = "tools"
    COURSES = "courses"
    JOBS = "jobs"
    EVENTS = "events"
    TUTORIALS = "tutorials"

@dataclass
class ContentSource:
    name: str
    url: str
    category: ContentCategory
    scrape_method: str  # 'rss', 'api', 'scrape'
    is_active: bool = True

@dataclass
class ContentItem:
    title: str
    description: str
    category: ContentCategory
    source_url: str
    content_hash: str
    engagement_score: float
    created_at: str
    tags: List[str]
    image_url: Optional[str] = None

# Content sources configuration
CONTENT_SOURCES = [
    # AI News
    ContentSource("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", 
                 ContentCategory.AI_NEWS, "rss"),
    ContentSource("VentureBeat AI", "https://venturebeat.com/ai/feed/", 
                 ContentCategory.AI_NEWS, "rss"),
    ContentSource("AI News", "https://artificialintelligence-news.com/feed/", 
                 ContentCategory.AI_NEWS, "rss"),
    
    # Educational Content
    ContentSource("Coursera", "https://www.coursera.org/browse/data-science/machine-learning", 
                 ContentCategory.COURSES, "scrape"),
    ContentSource("edX", "https://www.edx.org/search?q=artificial+intelligence", 
                 ContentCategory.COURSES, "scrape"),
    ContentSource("Google AI Education", "https://ai.google/education/", 
                 ContentCategory.EDUCATION, "scrape"),
    
    # Tools and Platforms
    ContentSource("Product Hunt AI", "https://www.producthunt.com/topics/artificial-intelligence", 
                 ContentCategory.TOOLS, "scrape"),
    ContentSource("GitHub Trending", "https://github.com/trending?l=python&since=weekly", 
                 ContentCategory.TOOLS, "scrape"),
    
    # Jobs and Opportunities
    ContentSource("LinkedIn AI Jobs", "https://www.linkedin.com/jobs/search/?keywords=artificial%20intelligence", 
                 ContentCategory.JOBS, "scrape"),
    ContentSource("AngelList AI", "https://angel.co/jobs?keywords=AI", 
                 ContentCategory.JOBS, "scrape"),
    
    # Reddit for community insights
    ContentSource("r/MachineLearning", "https://www.reddit.com/r/MachineLearning/.json", 
                 ContentCategory.AI_NEWS, "api"),
    ContentSource("r/artificial", "https://www.reddit.com/r/artificial/.json", 
                 ContentCategory.AI_NEWS, "api"),
]

# Content templates for different categories
CONTENT_TEMPLATES = {
    ContentCategory.AI_NEWS: {
        "hashtags": ["#AI", "#MachineLearning", "#Technology", "#Innovation", "#ArtificialIntelligence"],
        "template": "🚀 AI News Alert!\n\n{title}\n\n{description}\n\n💡 What do you think about this development?\n\n{hashtags}\n\n🔗 {source_url}"
    },
    ContentCategory.EDUCATION: {
        "hashtags": ["#AIEducation", "#Learning", "#Tech", "#Skills", "#Development"],
        "template": "📚 Learn AI Today!\n\n{title}\n\n{description}\n\n🎯 Perfect for beginners and experts alike!\n\n{hashtags}\n\n🔗 {source_url}"
    },
    ContentCategory.OPPORTUNITIES: {
        "hashtags": ["#AIJobs", "#TechCareers", "#Opportunities", "#Hiring", "#CareerGrowth"],
        "template": "💼 AI Opportunity Alert!\n\n{title}\n\n{description}\n\n🌟 Apply now and level up your career!\n\n{hashtags}\n\n🔗 {source_url}"
    },
    ContentCategory.TOOLS: {
        "hashtags": ["#AITools", "#Productivity", "#TechTools", "#Innovation", "#Development"],
        "template": "🛠️ New AI Tool Alert!\n\n{title}\n\n{description}\n\n⚡ Boost your productivity today!\n\n{hashtags}\n\n🔗 {source_url}"
    },
    ContentCategory.COURSES: {
        "hashtags": ["#FreeCourses", "#AILearning", "#Education", "#Skills", "#OnlineLearning"],
        "template": "🎓 Free Course Alert!\n\n{title}\n\n{description}\n\n📖 Start learning today - it's FREE!\n\n{hashtags}\n\n🔗 {source_url}"
    }
}
