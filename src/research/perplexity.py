"""
Perplexity API integration for advanced research and trend analysis.
Uses your Perplexity Premium subscription for real-time information.
"""
import aiohttp
import asyncio
import json
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)

class PerplexityResearchService:
    """Enhanced research service using Perplexity API for real-time insights"""
    
    def __init__(self):
        self.api_key = SETTINGS.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = SETTINGS.PERPLEXITY_MODEL
        self.session = None
        
        # Rate limiting
        self.requests_per_minute = SETTINGS.PERPLEXITY_REQUESTS_PER_MINUTE
        self.last_request_time = None
        self.request_count = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = datetime.now()
        
        if self.last_request_time is None:
            self.last_request_time = current_time
            self.request_count = 1
            return
        
        # Reset counter if a minute has passed
        if (current_time - self.last_request_time).seconds >= 60:
            self.request_count = 1
            self.last_request_time = current_time
            return
        
        # Check if we've exceeded the rate limit
        if self.request_count >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.last_request_time).seconds
            logger.info(f"⏳ Rate limit reached, waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            self.request_count = 1
            self.last_request_time = datetime.now()
        else:
            self.request_count += 1
    
    async def _make_request(self, messages: List[Dict], temperature: float = None) -> Dict:
        """Make request to Perplexity API"""
        await self._rate_limit()
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or SETTINGS.PERPLEXITY_TEMPERATURE,
            "max_tokens": SETTINGS.PERPLEXITY_MAX_TOKENS
        }
        
        try:
            async with self.session.post(
                self.base_url,
                headers=headers,
                json=payload
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Perplexity API error ({response.status}): {error_text}")
                    raise Exception(f"API request failed: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Error making Perplexity request: {str(e)}")
            raise
    
    async def research_trending_topics(self, topic_area: str = "artificial intelligence") -> List[Dict]:
        """Research trending topics in a specific area"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert trend analyst. Provide current, accurate information about trending topics."
                },
                {
                    "role": "user",
                    "content": f"""
                    Research the top 10 trending topics in {topic_area} right now. 
                    Focus on:
                    - Latest breakthroughs and developments
                    - Emerging technologies and tools
                    - Industry discussions and debates
                    - Recent research papers or announcements
                    - Popular discussions on social media
                    
                    For each trending topic, provide:
                    1. Topic name
                    2. Brief description (2-3 sentences)
                    3. Why it's trending now
                    4. Potential for viral content
                    5. Key hashtags or keywords
                    
                    Format as JSON with this structure:
                    {{
                        "trending_topics": [
                            {{
                                "topic": "Topic name",
                                "description": "Brief description",
                                "trend_reason": "Why it's trending",
                                "viral_potential": "High/Medium/Low",
                                "keywords": ["keyword1", "keyword2"],
                                "content_angle": "Suggested content approach"
                            }}
                        ]
                    }}
                    """
                }
            ]
            
            response = await self._make_request(messages, temperature=0.3)
            content = response['choices'][0]['message']['content']
            
            # Try to parse JSON from response
            try:
                # Extract JSON from the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                json_str = content[start_idx:end_idx]
                
                trending_data = json.loads(json_str)
                topics = trending_data.get('trending_topics', [])
                
                logger.info(f"✅ Found {len(topics)} trending topics in {topic_area}")
                return topics
                
            except json.JSONDecodeError:
                # If JSON parsing fails, extract topics manually
                logger.warning("⚠️ Could not parse JSON, extracting topics manually")
                return self._extract_topics_manually(content)
                
        except Exception as e:
            logger.error(f"❌ Error researching trending topics: {str(e)}")
            return []
    
    async def research_content_ideas(self, topic: str, content_type: str = "Instagram post") -> List[Dict]:
        """Generate content ideas based on current trends and research"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a viral content strategist and AI expert. Create engaging, shareable content ideas based on current information."
                },
                {
                    "role": "user",
                    "content": f"""
                    Research and create 5 viral {content_type} ideas about {topic}.
                    
                    For each idea, provide:
                    1. A catchy hook or headline
                    2. Main content points (3-5 bullet points)
                    3. Call-to-action
                    4. Relevant hashtags
                    5. Why it would go viral
                    6. Best posting time
                    
                    Make sure the content is:
                    - Based on current, real information
                    - Engaging and shareable
                    - Educational but entertaining
                    - Optimized for social media
                    
                    Format as JSON:
                    {{
                        "content_ideas": [
                            {{
                                "hook": "Catchy headline",
                                "content_points": ["point1", "point2", "point3"],
                                "call_to_action": "What action to take",
                                "hashtags": ["#hashtag1", "#hashtag2"],
                                "viral_potential": "Why it would go viral",
                                "best_time": "Optimal posting time",
                                "engagement_strategy": "How to maximize engagement"
                            }}
                        ]
                    }}
                    """
                }
            ]
            
            response = await self._make_request(messages, temperature=0.7)
            content = response['choices'][0]['message']['content']
            
            try:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                json_str = content[start_idx:end_idx]
                
                ideas_data = json.loads(json_str)
                ideas = ideas_data.get('content_ideas', [])
                
                logger.info(f"✅ Generated {len(ideas)} content ideas for {topic}")
                return ideas
                
            except json.JSONDecodeError:
                logger.warning("⚠️ Could not parse content ideas JSON")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error generating content ideas: {str(e)}")
            return []
    
    async def research_competitor_analysis(self, topic: str) -> Dict:
        """Analyze what competitors are doing in the space"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a competitive intelligence analyst specializing in social media and content strategy."
                },
                {
                    "role": "user",
                    "content": f"""
                    Analyze the current competitive landscape for {topic} content on social media.
                    
                    Research and provide:
                    1. Top content creators/accounts in this space
                    2. Most popular content formats being used
                    3. Common themes and topics
                    4. Content gaps and opportunities
                    5. Emerging trends in the space
                    6. Engagement strategies that work
                    7. Recommendations for differentiation
                    
                    Focus on Instagram, but include other platforms if relevant.
                    """
                }
            ]
            
            response = await self._make_request(messages, temperature=0.4)
            content = response['choices'][0]['message']['content']
            
            analysis = {
                'topic': topic,
                'analysis': content,
                'timestamp': datetime.now().isoformat(),
                'recommendations': self._extract_recommendations(content)
            }
            
            logger.info(f"✅ Completed competitor analysis for {topic}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error in competitor analysis: {str(e)}")
            return {}
    
    async def research_viral_content_patterns(self) -> Dict:
        """Research current viral content patterns and strategies"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a viral content expert who studies what makes content go viral on social media."
                },
                {
                    "role": "user",
                    "content": """
                    Research and analyze the latest viral content patterns on Instagram and other social platforms.
                    
                    Focus on:
                    1. What types of content are going viral right now
                    2. Common characteristics of viral posts
                    3. Trending formats (carousels, reels, stories)
                    4. Psychological triggers being used
                    5. Timing patterns for viral content
                    6. Hashtag strategies that work
                    7. Engagement techniques that drive virality
                    
                    Provide actionable insights for AI/tech content creators.
                    """
                }
            ]
            
            response = await self._make_request(messages, temperature=0.5)
            content = response['choices'][0]['message']['content']
            
            patterns = {
                'analysis': content,
                'timestamp': datetime.now().isoformat(),
                'key_insights': self._extract_key_insights(content),
                'actionable_tips': self._extract_actionable_tips(content)
            }
            
            logger.info("✅ Completed viral content patterns research")
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Error researching viral patterns: {str(e)}")
            return {}
    
    async def fact_check_content(self, content: str) -> Dict:
        """Fact-check content for accuracy"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a fact-checker with access to current information. Verify the accuracy of the provided content."
                },
                {
                    "role": "user",
                    "content": f"""
                    Please fact-check the following content for accuracy:
                    
                    {content}
                    
                    Provide:
                    1. Overall accuracy rating (High/Medium/Low)
                    2. Any factual errors found
                    3. Corrections or clarifications needed
                    4. Sources or evidence for claims
                    5. Suggestions for improvement
                    """
                }
            ]
            
            response = await self._make_request(messages, temperature=0.2)
            fact_check_result = response['choices'][0]['message']['content']
            
            return {
                'original_content': content,
                'fact_check_result': fact_check_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error fact-checking content: {str(e)}")
            return {}
    
    def _extract_topics_manually(self, content: str) -> List[Dict]:
        """Manually extract topics if JSON parsing fails"""
        # This is a fallback method - implement basic extraction
        topics = []
        lines = content.split('\n')
        
        current_topic = {}
        for line in lines:
            line = line.strip()
            if line.startswith('1.') or line.startswith('Topic:'):
                if current_topic:
                    topics.append(current_topic)
                current_topic = {'topic': line, 'viral_potential': 'Medium'}
        
        if current_topic:
            topics.append(current_topic)
        
        return topics[:10]  # Return max 10 topics
    
    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from analysis content"""
        recommendations = []
        lines = content.split('\n')
        
        for line in lines:
            if 'recommend' in line.lower() or 'suggest' in line.lower():
                recommendations.append(line.strip())
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _extract_key_insights(self, content: str) -> List[str]:
        """Extract key insights from viral patterns analysis"""
        insights = []
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['key', 'important', 'trend', 'pattern']):
                insights.append(line.strip())
        
        return insights[:7]  # Return top 7 insights
    
    def _extract_actionable_tips(self, content: str) -> List[str]:
        """Extract actionable tips from content"""
        tips = []
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['tip', 'action', 'strategy', 'use', 'try']):
                tips.append(line.strip())
        
        return tips[:5]  # Return top 5 tips

# Convenience functions
async def research_ai_trends() -> List[Dict]:
    """Quick function to research AI trends"""
    async with PerplexityResearchService() as service:
        return await service.research_trending_topics("artificial intelligence and machine learning")

async def generate_content_ideas(topic: str) -> List[Dict]:
    """Quick function to generate content ideas"""
    async with PerplexityResearchService() as service:
        return await service.research_content_ideas(topic)

async def analyze_viral_patterns() -> Dict:
    """Quick function to analyze viral patterns"""
    async with PerplexityResearchService() as service:
        return await service.research_viral_content_patterns()

# Test function
async def test_perplexity_service():
    """Test the Perplexity research service"""
    try:
        print("🧪 Testing Perplexity research service...")
        
        async with PerplexityResearchService() as service:
            # Test trending topics research
            print("🔍 Researching AI trends...")
            trends = await service.research_trending_topics("artificial intelligence")
            print(f"✅ Found {len(trends)} trending topics")
            
            # Test content ideas generation
            print("💡 Generating content ideas...")
            ideas = await service.research_content_ideas("machine learning breakthroughs")
            print(f"✅ Generated {len(ideas)} content ideas")
            
            # Test viral patterns research
            print("🚀 Analyzing viral patterns...")
            patterns = await service.research_viral_content_patterns()
            print("✅ Completed viral patterns analysis")
            
            print("🎉 Perplexity service test completed successfully!")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("💡 Make sure your PERPLEXITY_API_KEY is set in the .env file")

if __name__ == "__main__":
    asyncio.run(test_perplexity_service())