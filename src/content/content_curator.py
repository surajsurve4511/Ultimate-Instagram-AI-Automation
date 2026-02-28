"""
Content curation module for gathering and filtering AI content from multiple sources.
"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup
import feedparser

from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)

class ContentCurator:
    """Curate high-quality AI content from various sources"""
    
    def __init__(self):
        self.sources = {
            'rss_feeds': [
                'https://www.technologyreview.com/feed/',
                'https://techcrunch.com/feed/',
                'https://venturebeat.com/category/ai/feed/',
                'https://www.theverge.com/rss/ai-artificial-intelligence/index.xml',
                'https://www.artificialintelligence-news.com/feed/',
            ],
            'news_sites': [
                'https://news.ycombinator.com/',
                'https://www.reddit.com/r/MachineLearning/.json',
                'https://www.reddit.com/r/artificial/.json',
            ]
        }
        
        self.session = None
    
    async def initialize(self):
        """Initialize the content curator"""
        self.session = aiohttp.ClientSession()
        logger.info("✅ Content curator initialized")
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
    
    async def curate_content_from_sources(self) -> List[Dict]:
        """Curate content from all configured sources"""
        try:
            all_content = []
            
            # Fetch from RSS feeds
            rss_content = await self._fetch_rss_content()
            all_content.extend(rss_content)
            
            # Fetch from news sites
            news_content = await self._fetch_news_content()
            all_content.extend(news_content)
            
            # Filter and score content
            filtered_content = self._filter_content(all_content)
            
            logger.info(f"✅ Curated {len(filtered_content)} pieces of content")
            return filtered_content
            
        except Exception as e:
            logger.error(f"❌ Error curating content: {str(e)}")
            return []
    
    async def _fetch_rss_content(self) -> List[Dict]:
        """Fetch content from RSS feeds"""
        content_items = []
        
        for feed_url in self.sources['rss_feeds']:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:5]:  # Get latest 5 from each feed
                    content_items.append({
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', ''),
                        'url': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'source': feed_url,
                        'type': 'rss'
                    })
                
                logger.info(f"✅ Fetched {len(feed.entries[:5])} items from {feed_url}")
                
            except Exception as e:
                logger.error(f"❌ Error fetching RSS feed {feed_url}: {str(e)}")
        
        return content_items
    
    async def _fetch_news_content(self) -> List[Dict]:
        """Fetch content from news sites"""
        content_items = []
        
        for news_url in self.sources['news_sites']:
            try:
                if 'reddit.com' in news_url:
                    items = await self._fetch_reddit_content(news_url)
                    content_items.extend(items)
                elif 'news.ycombinator.com' in news_url:
                    items = await self._fetch_hackernews_content()
                    content_items.extend(items)
                
            except Exception as e:
                logger.error(f"❌ Error fetching news from {news_url}: {str(e)}")
        
        return content_items
    
    async def _fetch_reddit_content(self, url: str) -> List[Dict]:
        """Fetch content from Reddit"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    items = []
                    for post in data.get('data', {}).get('children', [])[:10]:
                        post_data = post.get('data', {})
                        items.append({
                            'title': post_data.get('title', ''),
                            'description': post_data.get('selftext', '')[:500],
                            'url': f"https://reddit.com{post_data.get('permalink', '')}",
                            'score': post_data.get('score', 0),
                            'source': 'reddit',
                            'type': 'reddit'
                        })
                    
                    return items
        except Exception as e:
            logger.error(f"❌ Error fetching Reddit content: {str(e)}")
        
        return []
    
    async def _fetch_hackernews_content(self) -> List[Dict]:
        """Fetch content from Hacker News"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Fetch top stories
            async with self.session.get('https://hacker-news.firebaseio.com/v0/topstories.json') as response:
                if response.status == 200:
                    story_ids = await response.json()
                    
                    items = []
                    for story_id in story_ids[:10]:
                        async with self.session.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json') as story_response:
                            if story_response.status == 200:
                                story = await story_response.json()
                                items.append({
                                    'title': story.get('title', ''),
                                    'description': story.get('text', ''),
                                    'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                                    'score': story.get('score', 0),
                                    'source': 'hackernews',
                                    'type': 'hackernews'
                                })
                    
                    return items
        except Exception as e:
            logger.error(f"❌ Error fetching Hacker News content: {str(e)}")
        
        return []
    
    def _filter_content(self, content_items: List[Dict]) -> List[Dict]:
        """Filter and score content based on quality metrics"""
        filtered = []
        
        for item in content_items:
            # Basic quality checks
            if not item.get('title') or len(item.get('title', '')) < 10:
                continue
            
            # Calculate engagement score
            score = item.get('score', 0)
            engagement_score = min(score / 100, 1.0) if score else 0.5
            
            item['engagement_score'] = engagement_score
            
            if engagement_score >= SETTINGS.MIN_ENGAGEMENT_SCORE:
                filtered.append(item)
        
        # Sort by engagement score
        filtered.sort(key=lambda x: x.get('engagement_score', 0), reverse=True)
        
        return filtered[:20]  # Return top 20 items

# Global instance
content_curator = ContentCurator()