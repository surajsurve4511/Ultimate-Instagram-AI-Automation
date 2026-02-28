"""
Advanced analytics and engagement optimization system.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import json

class EngagementPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Feature weights for engagement prediction
        self.feature_importance = {
            'post_time_hour': 0.15,
            'hashtag_count': 0.12,
            'content_length': 0.10,
            'sentiment_score': 0.18,
            'viral_score': 0.25,
            'trend_relevance': 0.20
        }
    
    def predict_engagement(self, post_data: Dict) -> float:
        """Predict engagement score for a post"""
        features = self._extract_features(post_data)
        
        if not self.is_trained:
            # Use heuristic scoring if model not trained
            return self._heuristic_scoring(features)
        
        # Use ML model prediction
        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict(features_scaled)[0]
        
        return max(0, min(1, prediction))  # Clamp between 0 and 1
    
    def _extract_features(self, post_data: Dict) -> List[float]:
        """Extract numerical features from post data"""
        return [
            post_data.get('post_time_hour', 12),  # Hour of posting
            len(post_data.get('hashtags', [])),   # Number of hashtags
            len(post_data.get('caption', '')),    # Caption length
            post_data.get('sentiment_score', 0.5), # Sentiment score
            post_data.get('viral_score', 0.5),    # Viral potential
            post_data.get('trend_relevance', 0.5) # Trend relevance
        ]
    
    def _heuristic_scoring(self, features: List[float]) -> float:
        """Heuristic scoring when ML model not available"""
        score = 0
        
        # Optimal posting time (9 AM, 2 PM, 6 PM get higher scores)
        hour = features[0]
        if hour in [9, 14, 18]:
            score += 0.2
        elif hour in [8, 10, 13, 15, 17, 19]:
            score += 0.1
        
        # Hashtag count (5-10 hashtags optimal)
        hashtag_count = features[1]
        if 5 <= hashtag_count <= 10:
            score += 0.15
        elif hashtag_count > 0:
            score += 0.05
        
        # Content length (150-300 chars optimal)
        content_length = features[2]
        if 150 <= content_length <= 300:
            score += 0.1
        elif content_length > 0:
            score += 0.05
        
        # Sentiment, viral, and trend scores
        score += features[3] * 0.18  # Sentiment
        score += features[4] * 0.25  # Viral potential
        score += features[5] * 0.20  # Trend relevance
        
        return min(score, 1.0)

class ContentOptimizer:
    def __init__(self):
        self.engagement_predictor = EngagementPredictor()
        self.performance_history = []
        
        # Optimal posting times by day of week
        self.optimal_times = {
            'monday': [9, 14, 18],
            'tuesday': [9, 14, 18],
            'wednesday': [8, 13, 17],
            'thursday': [9, 14, 18],
            'friday': [8, 14, 17],
            'saturday': [10, 15, 19],
            'sunday': [11, 16, 20]
        }
        
        # Content type performance multipliers
        self.content_multipliers = {
            'carousel': 1.3,
            'meme': 1.5,
            'infographic': 1.2,
            'tutorial': 1.1,
            'comparison': 1.25,
            'viral': 1.4
        }
    
    def optimize_post_timing(self, content_type: str = 'standard') -> Dict:
        """Optimize posting time for maximum engagement"""
        now = datetime.now()
        day_name = now.strftime('%A').lower()
        
        optimal_hours = self.optimal_times.get(day_name, [9, 14, 18])
        multiplier = self.content_multipliers.get(content_type, 1.0)
        
        # Find next optimal time
        current_hour = now.hour
        next_optimal = None
        
        for hour in optimal_hours:
            if hour > current_hour:
                next_optimal = hour
                break
        
        if not next_optimal:
            # Use first optimal time tomorrow
            next_optimal = optimal_hours[0]
            now = now + timedelta(days=1)
        
        optimal_time = now.replace(hour=next_optimal, minute=0, second=0)
        
        return {
            'optimal_time': optimal_time.isoformat(),
            'engagement_boost': multiplier,
            'reasoning': f"Optimal for {content_type} content on {day_name}",
            'confidence': 0.85
        }
    
    def optimize_hashtags(self, content: str, category: str) -> List[str]:
        """Optimize hashtag selection for maximum reach"""
        base_hashtags = {
            'ai_news': ['#AI', '#ArtificialIntelligence', '#TechNews', '#Innovation', '#MachineLearning'],
            'education': ['#AIEducation', '#LearnAI', '#TechSkills', '#OnlineLearning', '#SkillUp'],
            'tools': ['#AITools', '#Productivity', '#TechTools', '#Automation', '#Innovation'],
            'opportunities': ['#AIJobs', '#TechCareers', '#CareerGrowth', '#Hiring', '#TechOpportunities']
        }
        
        # Get base hashtags for category
        hashtags = base_hashtags.get(category, base_hashtags['ai_news']).copy()
        
        # Add trending hashtags
        trending = ['#Viral', '#TechTrend', '#AIRevolution', '#FutureTech', '#DigitalTransformation']
        hashtags.extend(trending[:3])
        
        # Add content-specific hashtags
        content_lower = content.lower()
        if 'chatgpt' in content_lower:
            hashtags.append('#ChatGPT')
        if 'openai' in content_lower:
            hashtags.append('#OpenAI')
        if 'google' in content_lower:
            hashtags.append('#GoogleAI')
        
        # Ensure optimal count (5-10 hashtags)
        return hashtags[:10]
    
    def generate_engagement_hooks(self, content_type: str) -> List[str]:
        """Generate engagement-optimized hooks"""
        hooks_by_type = {
            'question': [
                "What's your take on this? 🤔",
                "Which option would you choose? 💭",
                "Have you tried this yet? Share your experience! 👇",
                "What am I missing? Let me know! 💬",
                "Agree or disagree? Defend your answer! ⚔️"
            ],
            'call_to_action': [
                "Save this for later! 💾",
                "Share with someone who needs this! 👥",
                "Tag a friend who would love this! 🏷️",
                "Double-tap if you found this useful! ❤️",
                "Follow for more AI insights! ✨"
            ],
            'controversial': [
                "Hot take: This will be huge in 2025! 🔥",
                "Unpopular opinion: Everyone's doing this wrong! ⚡",
                "Plot twist: This changes everything! 🌪️",
                "Controversial but true: The old way is dead! 💀",
                "Bold prediction: Mark my words! 🎯"
            ]
        }
        
        all_hooks = []
        for hook_type, hooks in hooks_by_type.items():
            all_hooks.extend(hooks)
        
        return all_hooks
    
    def analyze_competitor_content(self, competitor_data: List[Dict]) -> Dict:
        """Analyze competitor content for insights"""
        if not competitor_data:
            return {"message": "No competitor data available"}
        
        # Analyze posting patterns
        posting_times = [post.get('hour', 12) for post in competitor_data]
        popular_times = {}
        for hour in posting_times:
            popular_times[hour] = popular_times.get(hour, 0) + 1
        
        # Analyze content types
        content_types = [post.get('type', 'standard') for post in competitor_data]
        type_performance = {}
        for content_type in content_types:
            type_performance[content_type] = type_performance.get(content_type, 0) + 1
        
        # Find content gaps
        our_categories = ['ai_news', 'education', 'tools', 'opportunities']
        competitor_categories = [post.get('category', 'other') for post in competitor_data]
        
        gaps = []
        for category in our_categories:
            if category not in competitor_categories:
                gaps.append(category)
        
        return {
            'popular_posting_times': sorted(popular_times.items(), key=lambda x: x[1], reverse=True)[:3],
            'top_content_types': sorted(type_performance.items(), key=lambda x: x[1], reverse=True)[:3],
            'content_gaps': gaps,
            'opportunities': self._identify_opportunities(competitor_data)
        }
    
    def _identify_opportunities(self, competitor_data: List[Dict]) -> List[str]:
        """Identify content opportunities"""
        opportunities = []
        
        # Check for underexplored topics
        topics = [post.get('topic', '').lower() for post in competitor_data]
        emerging_topics = ['ai agents', 'multimodal ai', 'ai governance', 'quantum ai']
        
        for topic in emerging_topics:
            if not any(topic in t for t in topics):
                opportunities.append(f"Create content about {topic} - underexplored by competitors")
        
        # Check for format gaps
        formats = [post.get('format', 'standard') for post in competitor_data]
        if 'carousel' not in formats:
            opportunities.append("Use carousel format - high engagement potential")
        if 'meme' not in formats:
            opportunities.append("Create meme content - viral potential")
        
        return opportunities

class PersonalizationEngine:
    def __init__(self):
        self.user_segments = {}
        self.content_preferences = {}
    
    def segment_audience(self, engagement_data: List[Dict]) -> Dict:
        """Segment audience based on engagement patterns"""
        if not engagement_data:
            return {"segments": []}
        
        # Create feature matrix
        features = []
        for data in engagement_data:
            features.append([
                data.get('likes', 0),
                data.get('comments', 0),
                data.get('shares', 0),
                data.get('saves', 0),
                data.get('time_spent', 0)
            ])
        
        # Perform clustering
        if len(features) >= 3:
            kmeans = KMeans(n_clusters=min(3, len(features)), random_state=42)
            clusters = kmeans.fit_predict(features)
            
            segments = {}
            for i, cluster in enumerate(clusters):
                if cluster not in segments:
                    segments[cluster] = []
                segments[cluster].append(engagement_data[i])
            
            return {"segments": segments}
        
        return {"segments": {"general": engagement_data}}
    
    def personalize_content(self, content: Dict, user_segment: str) -> Dict:
        """Personalize content for specific user segment"""
        segment_preferences = {
            'tech_enthusiasts': {
                'tone': 'technical',
                'hashtags': ['#TechDeep', '#AdvancedAI', '#Developers'],
                'content_depth': 'detailed'
            },
            'beginners': {
                'tone': 'friendly',
                'hashtags': ['#AIBasics', '#BeginnerFriendly', '#EasyAI'],
                'content_depth': 'simplified'
            },
            'business_users': {
                'tone': 'professional',
                'hashtags': ['#AIBusiness', '#ProductivityAI', '#BusinessAI'],
                'content_depth': 'practical'
            }
        }
        
        preferences = segment_preferences.get(user_segment, segment_preferences['beginners'])
        
        # Modify content based on preferences
        personalized_content = content.copy()
        personalized_content['tone'] = preferences['tone']
        personalized_content['hashtags'].extend(preferences['hashtags'])
        personalized_content['complexity'] = preferences['content_depth']
        
        return personalized_content

# Global instances
content_optimizer = ContentOptimizer()
personalization_engine = PersonalizationEngine()
