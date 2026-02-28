"""
Advanced web scraping module for collecting AI-related content.
"""
import requests
import feedparser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import time
from typing import List, Dict
from src.content.categories import ContentSource, ContentItem, ContentCategory
import hashlib
from datetime import datetime
import os

class ContentScraper:
    def __init__(self):
        self.setup_selenium()
        
    def setup_selenium(self):
        """Setup headless Chrome for web scraping"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def scrape_rss_feed(self, source: ContentSource) -> List[ContentItem]:
        """Scrape RSS feeds for content"""
        try:
            feed = feedparser.parse(source.url)
            items = []
            
            for entry in feed.entries[:5]:  # Get latest 5 items
                content_hash = hashlib.md5(entry.title.encode()).hexdigest()
                
                item = ContentItem(
                    title=entry.title,
                    description=entry.summary if hasattr(entry, 'summary') else entry.title,
                    category=source.category,
                    source_url=entry.link,
                    content_hash=content_hash,
                    engagement_score=0.8,  # Default score, will be updated
                    created_at=datetime.now().isoformat(),
                    tags=self.extract_tags(entry.title + " " + getattr(entry, 'summary', ''))
                )
                items.append(item)
                
            return items
        except Exception as e:
            print(f"Error scraping RSS {source.name}: {e}")
            return []
    
    def scrape_reddit_api(self, source: ContentSource) -> List[ContentItem]:
        """Scrape Reddit API for trending content"""
        try:
            headers = {'User-Agent': 'AI-Instagram-Bot/1.0'}
            response = requests.get(source.url, headers=headers)
            data = response.json()
            
            items = []
            for post in data['data']['children'][:3]:  # Top 3 posts
                post_data = post['data']
                content_hash = hashlib.md5(post_data['title'].encode()).hexdigest()
                
                item = ContentItem(
                    title=post_data['title'],
                    description=post_data.get('selftext', '')[:200] + "...",
                    category=source.category,
                    source_url=f"https://reddit.com{post_data['permalink']}",
                    content_hash=content_hash,
                    engagement_score=min(post_data['score'] / 1000, 1.0),  # Normalize score
                    created_at=datetime.now().isoformat(),
                    tags=self.extract_tags(post_data['title'])
                )
                items.append(item)
                
            return items
        except Exception as e:
            print(f"Error scraping Reddit {source.name}: {e}")
            return []
    
    def scrape_website(self, source: ContentSource) -> List[ContentItem]:
        """Scrape websites using Selenium"""
        try:
            self.driver.get(source.url)
            time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            items = []
            
            # Generic scraping logic - customize per site
            if "coursera" in source.url.lower():
                items = self.scrape_coursera(soup, source)
            elif "producthunt" in source.url.lower():
                items = self.scrape_producthunt(soup, source)
            elif "github" in source.url.lower():
                items = self.scrape_github_trending(soup, source)
            
            return items
        except Exception as e:
            print(f"Error scraping website {source.name}: {e}")
            return []
    
    def scrape_coursera(self, soup: BeautifulSoup, source: ContentSource) -> List[ContentItem]:
        """Scrape Coursera for free AI courses"""
        items = []
        course_cards = soup.find_all('div', class_='cds-CommonCard-container')[:3]
        
        for card in course_cards:
            try:
                title_elem = card.find('h3')
                title = title_elem.text.strip() if title_elem else "AI Course"
                
                link_elem = card.find('a')
                link = "https://coursera.org" + link_elem['href'] if link_elem else source.url
                
                content_hash = hashlib.md5(title.encode()).hexdigest()
                
                item = ContentItem(
                    title=f"Free AI Course: {title}",
                    description=f"Learn {title} on Coursera - Free enrollment available!",
                    category=ContentCategory.COURSES,
                    source_url=link,
                    content_hash=content_hash,
                    engagement_score=0.9,
                    created_at=datetime.now().isoformat(),
                    tags=["course", "free", "ai", "learning"]
                )
                items.append(item)
            except Exception as e:
                continue
                
        return items
    
    def scrape_producthunt(self, soup: BeautifulSoup, source: ContentSource) -> List[ContentItem]:
        """Scrape Product Hunt for AI tools"""
        items = []
        product_cards = soup.find_all('div', attrs={'data-test': 'post-item'})[:3]
        
        for card in product_cards:
            try:
                title_elem = card.find('h3')
                title = title_elem.text.strip() if title_elem else "AI Tool"
                
                desc_elem = card.find('p')
                description = desc_elem.text.strip() if desc_elem else "New AI tool launched!"
                
                content_hash = hashlib.md5(title.encode()).hexdigest()
                
                item = ContentItem(
                    title=f"🚀 New AI Tool: {title}",
                    description=description,
                    category=ContentCategory.TOOLS,
                    source_url=source.url,
                    content_hash=content_hash,
                    engagement_score=0.8,
                    created_at=datetime.now().isoformat(),
                    tags=["tool", "ai", "productivity", "launch"]
                )
                items.append(item)
            except Exception as e:
                continue
                
        return items
    
    def scrape_github_trending(self, soup: BeautifulSoup, source: ContentSource) -> List[ContentItem]:
        """Scrape GitHub trending for AI repositories"""
        items = []
        repo_cards = soup.find_all('article', class_='Box-row')[:2]
        
        for card in repo_cards:
            try:
                title_elem = card.find('h2')
                if title_elem:
                    repo_name = title_elem.find('a').text.strip()
                    
                desc_elem = card.find('p')
                description = desc_elem.text.strip() if desc_elem else "Trending AI repository"
                
                content_hash = hashlib.md5(repo_name.encode()).hexdigest()
                
                item = ContentItem(
                    title=f"🔥 Trending: {repo_name}",
                    description=description,
                    category=ContentCategory.TOOLS,
                    source_url=f"https://github.com/{repo_name}",
                    content_hash=content_hash,
                    engagement_score=0.85,
                    created_at=datetime.now().isoformat(),
                    tags=["github", "opensource", "trending", "ai"]
                )
                items.append(item)
            except Exception as e:
                continue
                
        return items
    
    def extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text"""
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 
                      'neural network', 'llm', 'gpt', 'chatbot', 'automation', 'data science']
        
        text_lower = text.lower()
        tags = []
        
        for keyword in ai_keywords:
            if keyword in text_lower:
                tags.append(keyword.replace(' ', ''))
                
        return tags[:5]  # Limit to 5 tags
    
    def close(self):
        """Close selenium driver"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def collect_all_content() -> List[ContentItem]:
    """Collect content from all sources"""
    scraper = ContentScraper()
    all_content = []
    
    try:
        from src.content.categories import CONTENT_SOURCES
        
        for source in CONTENT_SOURCES:
            if not source.is_active:
                continue
                
            print(f"Scraping {source.name}...")
            
            if source.scrape_method == 'rss':
                items = scraper.scrape_rss_feed(source)
            elif source.scrape_method == 'api':
                items = scraper.scrape_reddit_api(source)
            elif source.scrape_method == 'scrape':
                items = scraper.scrape_website(source)
            else:
                continue
                
            all_content.extend(items)
            time.sleep(2)  # Rate limiting
            
    finally:
        scraper.close()
    
    return all_content
