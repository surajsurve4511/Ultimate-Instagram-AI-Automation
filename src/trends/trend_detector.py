"""
Advanced trend detection and real-time content adaptation system.
"""
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import tweepy
import yfinance as yf
from pytrends.request import TrendReq
from textblob import TextBlob
import asyncio
import aiohttp

class TrendDetector:
    def __init__(self):
        self.trend_sources = {
            "google_trends": self._get_google_trends,
            "twitter_trends": self._get_twitter_trends,
            "reddit_trends": self._get_reddit_trends,
            "news_trends": self._get_news_trends,
            "github_trends": self._get_github_trends,
            "ai_research_trends": self._get_ai_research_trends,
            "crypto_ai_trends": self._get_crypto_ai_trends,
            "job_market_trends": self._get_job_trends
        }
        
        # Initialize trend tracking
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
    async def detect_trending_topics(self) -> Dict[str, List[Dict]]:
        """Detect trending topics from multiple sources"""
        all_trends = {}
        
        for source_name, source_func in self.trend_sources.items():
            try:
                trends = await source_func()
                all_trends[source_name] = trends
            except Exception as e:
                print(f"Error getting trends from {source_name}: {e}")
                all_trends[source_name] = []
        
        # Merge and rank trends
        merged_trends = self._merge_and_rank_trends(all_trends)
        return merged_trends
    
    async def _get_google_trends(self) -> List[Dict]:
        """Get Google Trends data"""
        try:
            # AI-related trending topics
            ai_keywords = ["artificial intelligence", "chatgpt", "machine learning", 
                          "ai tools", "openai", "google ai", "ai jobs"]
            
            trends = []
            for keyword in ai_keywords:
                try:
                    self.pytrends.build_payload([keyword], timeframe='now 7-d')
                    interest_data = self.pytrends.interest_over_time()
                    
                    if not interest_data.empty:
                        current_interest = interest_data[keyword].iloc[-1]
                        trend_score = current_interest / 100.0
                        
                        trends.append({
                            "keyword": keyword,
                            "trend_score": trend_score,
                            "source": "google_trends",
                            "category": "ai_general"
                        })
                except:
                    continue
            
            return trends
        except Exception as e:
            print(f"Google Trends error: {e}")
            return []
    
    async def _get_twitter_trends(self) -> List[Dict]:
        """Get Twitter trending topics (mock implementation)"""
        # Note: Twitter API requires authentication
        # This is a mock implementation
        mock_twitter_trends = [
            {"keyword": "AI breakthrough", "trend_score": 0.9, "source": "twitter", "category": "ai_news"},
            {"keyword": "ChatGPT update", "trend_score": 0.8, "source": "twitter", "category": "ai_tools"},
            {"keyword": "AI jobs", "trend_score": 0.7, "source": "twitter", "category": "careers"}
        ]
        return mock_twitter_trends
    
    async def _get_reddit_trends(self) -> List[Dict]:
        """Get trending topics from AI-related subreddits"""
        try:
            subreddits = ['MachineLearning', 'artificial', 'ChatGPT', 'OpenAI', 'singularity']
            trends = []
            
            for subreddit in subreddits:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                headers = {'User-Agent': 'TrendBot/1.0'}
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for post in data['data']['children']:
                                post_data = post['data']
                                
                                trends.append({
                                    "keyword": post_data['title'][:50],
                                    "trend_score": min(post_data['score'] / 1000, 1.0),
                                    "source": f"reddit_r_{subreddit}",
                                    "category": "community_discussion",
                                    "url": f"https://reddit.com{post_data['permalink']}"
                                })
            
            return trends
        except Exception as e:
            print(f"Reddit trends error: {e}")
            return []
    
    async def _get_news_trends(self) -> List[Dict]:
        """Get trending AI news topics"""
        try:
            # Mock news API call (replace with real news API)
            news_sources = [
                "TechCrunch", "VentureBeat", "Wired", "MIT Technology Review"
            ]
            
            trends = []
            for source in news_sources:
                # Simulate trending AI news
                mock_news = [
                    {"title": "New AI model breaks performance records", "score": 0.85},
                    {"title": "AI startup raises $100M funding", "score": 0.78},
                    {"title": "Google announces new AI features", "score": 0.82}
                ]
                
                for news in mock_news:
                    trends.append({
                        "keyword": news["title"],
                        "trend_score": news["score"],
                        "source": f"news_{source.lower().replace(' ', '_')}",
                        "category": "ai_news"
                    })
            
            return trends
        except Exception as e:
            print(f"News trends error: {e}")
            return []
    
    async def _get_github_trends(self) -> List[Dict]:
        """Get trending AI repositories on GitHub"""
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                "q": "artificial intelligence OR machine learning OR AI",
                "sort": "stars",
                "order": "desc",
                "per_page": 10
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        trends = []
                        
                        for repo in data['items']:
                            trends.append({
                                "keyword": f"{repo['name']} - {repo['description'][:50]}",
                                "trend_score": min(repo['stargazers_count'] / 10000, 1.0),
                                "source": "github",
                                "category": "ai_tools",
                                "url": repo['html_url']
                            })
                        
                        return trends
            
            return []
        except Exception as e:
            print(f"GitHub trends error: {e}")
            return []
    
    async def _get_ai_research_trends(self) -> List[Dict]:
        """Get trending AI research papers and topics"""
        try:
            # Mock ArXiv API call for AI papers
            research_trends = [
                {"topic": "Large Language Models", "score": 0.9, "papers": 15},
                {"topic": "Computer Vision", "score": 0.8, "papers": 12},
                {"topic": "Reinforcement Learning", "score": 0.7, "papers": 8},
                {"topic": "Neural Architecture Search", "score": 0.75, "papers": 6}
            ]
            
            trends = []
            for research in research_trends:
                trends.append({
                    "keyword": f"Latest research in {research['topic']}",
                    "trend_score": research["score"],
                    "source": "ai_research",
                    "category": "research",
                    "paper_count": research["papers"]
                })
            
            return trends
        except Exception as e:
            print(f"AI research trends error: {e}")
            return []
    
    async def _get_crypto_ai_trends(self) -> List[Dict]:
        """Get AI + Crypto trending topics"""
        try:
            # AI tokens and crypto AI projects
            ai_crypto_trends = [
                {"token": "AI trading bots", "score": 0.8},
                {"token": "Blockchain AI integration", "score": 0.7},
                {"token": "Decentralized AI networks", "score": 0.75}
            ]
            
            trends = []
            for trend in ai_crypto_trends:
                trends.append({
                    "keyword": trend["token"],
                    "trend_score": trend["score"],
                    "source": "crypto_ai",
                    "category": "ai_crypto"
                })
            
            return trends
        except Exception as e:
            print(f"Crypto AI trends error: {e}")
            return []
    
    async def _get_job_trends(self) -> List[Dict]:
        """Get AI job market trends"""
        try:
            job_trends = [
                {"role": "AI Engineer", "demand": 0.95, "salary_trend": "up"},
                {"role": "Machine Learning Engineer", "demand": 0.9, "salary_trend": "up"},
                {"role": "AI Product Manager", "demand": 0.8, "salary_trend": "stable"},
                {"role": "Data Scientist", "demand": 0.85, "salary_trend": "up"}
            ]
            
            trends = []
            for job in job_trends:
                trends.append({
                    "keyword": f"{job['role']} demand surging",
                    "trend_score": job["demand"],
                    "source": "job_market",
                    "category": "careers",
                    "salary_trend": job["salary_trend"]
                })
            
            return trends
        except Exception as e:
            print(f"Job trends error: {e}")
            return []
    
    def _merge_and_rank_trends(self, all_trends: Dict) -> List[Dict]:
        """Merge trends from all sources and rank by relevance"""
        merged = []
        
        for source, trends in all_trends.items():
            for trend in trends:
                trend['timestamp'] = datetime.now().isoformat()
                merged.append(trend)
        
        # Sort by trend score
        merged.sort(key=lambda x: x['trend_score'], reverse=True)
        
        # Remove duplicates and similar topics
        unique_trends = []
        seen_keywords = set()
        
        for trend in merged:
            keyword_lower = trend['keyword'].lower()
            is_similar = any(
                self._similarity_score(keyword_lower, seen) > 0.7 
                for seen in seen_keywords
            )
            
            if not is_similar:
                unique_trends.append(trend)
                seen_keywords.add(keyword_lower)
        
        return unique_trends[:20]  # Top 20 trends
    
    def _similarity_score(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0

class RealTimeTrendMonitor:
    def __init__(self):
        self.detector = TrendDetector()
        self.trend_history = []
        
    async def monitor_trends_continuously(self, interval_minutes: int = 30):
        """Continuously monitor trends"""
        while True:
            try:
                trends = await self.detector.detect_trending_topics()
                
                # Store trends with timestamp
                trend_snapshot = {
                    "timestamp": datetime.now().isoformat(),
                    "trends": trends
                }
                self.trend_history.append(trend_snapshot)
                
                # Keep only last 24 hours
                cutoff = datetime.now() - timedelta(hours=24)
                self.trend_history = [
                    snapshot for snapshot in self.trend_history
                    if datetime.fromisoformat(snapshot["timestamp"]) > cutoff
                ]
                
                # Check for emerging trends
                emerging = self._detect_emerging_trends()
                if emerging:
                    print(f"🚨 EMERGING TREND DETECTED: {emerging}")
                
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                print(f"Trend monitoring error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    def _detect_emerging_trends(self) -> Optional[Dict]:
        """Detect rapidly emerging trends"""
        if len(self.trend_history) < 2:
            return None
        
        current_trends = self.trend_history[-1]["trends"]
        previous_trends = self.trend_history[-2]["trends"]
        
        # Look for trends with rapid score increase
        for current in current_trends:
            for previous in previous_trends:
                if (current["keyword"] == previous["keyword"] and 
                    current["trend_score"] > previous["trend_score"] * 1.5):
                    return {
                        "keyword": current["keyword"],
                        "score_increase": current["trend_score"] - previous["trend_score"],
                        "category": current["category"],
                        "urgency": "high"
                    }
        
        return None
    
    def get_hot_trends(self, category: Optional[str] = None) -> List[Dict]:
        """Get currently hot trends"""
        if not self.trend_history:
            return []
        
        latest_trends = self.trend_history[-1]["trends"]
        
        if category:
            latest_trends = [t for t in latest_trends if t.get("category") == category]
        
        # Filter for high-scoring trends
        hot_trends = [t for t in latest_trends if t["trend_score"] > 0.7]
        
        return hot_trends[:10]

# Global trend monitor
trend_monitor = RealTimeTrendMonitor()
