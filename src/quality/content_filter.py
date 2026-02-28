"""
Content quality assessment and filtering module.
"""
import re
from typing import List, Dict, Tuple
from textstat import flesch_reading_ease, flesch_kincaid_grade
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from src.content.categories import ContentItem, ContentCategory
import os

# Download required NLTK data
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

class ContentQualityFilter:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        
        # Quality thresholds
        self.min_readability_score = 60  # Flesch Reading Ease
        self.max_reading_grade = 12      # Flesch-Kincaid Grade Level
        self.min_engagement_potential = 0.6
        
        # Banned words/phrases
        self.banned_words = [
            'scam', 'fake', 'clickbait', 'spam', 'hate', 'violence',
            'misleading', 'false', 'propaganda'
        ]
        
        # High-value keywords for AI content
        self.valuable_keywords = [
            'breakthrough', 'innovation', 'research', 'study', 'discovery',
            'advancement', 'solution', 'improvement', 'efficiency', 'accuracy',
            'free', 'open source', 'tutorial', 'guide', 'course', 'learning'
        ]
    
    def assess_content_quality(self, content_item: ContentItem) -> Dict:
        """Comprehensive content quality assessment"""
        text = f"{content_item.title} {content_item.description}"
        
        assessment = {
            'overall_score': 0.0,
            'readability': self.assess_readability(text),
            'sentiment': self.assess_sentiment(text),
            'relevance': self.assess_relevance(content_item),
            'engagement_potential': self.assess_engagement_potential(content_item),
            'content_safety': self.assess_content_safety(text),
            'freshness': self.assess_freshness(content_item),
            'passes_filter': False
        }
        
        # Calculate overall score
        weights = {
            'readability': 0.15,
            'sentiment': 0.2,
            'relevance': 0.25,
            'engagement_potential': 0.2,
            'content_safety': 0.1,
            'freshness': 0.1
        }
        
        overall_score = sum(
            assessment[key]['score'] * weights[key] 
            for key in weights.keys()
        )
        
        assessment['overall_score'] = overall_score
        assessment['passes_filter'] = overall_score >= 0.7
        
        return assessment
    
    def assess_readability(self, text: str) -> Dict:
        """Assess text readability"""
        try:
            flesch_score = flesch_reading_ease(text)
            grade_level = flesch_kincaid_grade(text)
            
            # Score based on readability (higher = better)
            readability_score = min(flesch_score / 100, 1.0)
            
            # Penalize if too complex
            if grade_level > self.max_reading_grade:
                readability_score *= 0.7
            
            return {
                'score': readability_score,
                'flesch_score': flesch_score,
                'grade_level': grade_level,
                'is_readable': flesch_score >= self.min_readability_score
            }
        except:
            return {'score': 0.5, 'flesch_score': 50, 'grade_level': 10, 'is_readable': True}
    
    def assess_sentiment(self, text: str) -> Dict:
        """Assess content sentiment"""
        try:
            sentiment_scores = self.sia.polarity_scores(text)
            
            # Prefer neutral to positive content
            if sentiment_scores['compound'] >= 0:
                sentiment_score = 0.8 + (sentiment_scores['compound'] * 0.2)
            else:
                sentiment_score = max(0.3, 0.8 + sentiment_scores['compound'])
            
            return {
                'score': min(sentiment_score, 1.0),
                'compound': sentiment_scores['compound'],
                'positive': sentiment_scores['pos'],
                'negative': sentiment_scores['neg'],
                'neutral': sentiment_scores['neu']
            }
        except:
            return {'score': 0.7, 'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    def assess_relevance(self, content_item: ContentItem) -> Dict:
        """Assess content relevance to AI education"""
        text = f"{content_item.title} {content_item.description}".lower()
        
        # AI relevance keywords
        ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'data science', 'algorithm', 'automation',
            'chatbot', 'llm', 'gpt', 'transformer', 'computer vision',
            'nlp', 'natural language processing', 'robotics', 'tech'
        ]
        
        # Educational keywords
        edu_keywords = [
            'course', 'tutorial', 'learn', 'education', 'training',
            'certification', 'skill', 'guide', 'workshop', 'bootcamp'
        ]
        
        # Opportunity keywords
        opportunity_keywords = [
            'job', 'career', 'opportunity', 'hiring', 'internship',
            'scholarship', 'grant', 'competition', 'hackathon'
        ]
        
        ai_score = sum(1 for keyword in ai_keywords if keyword in text) / len(ai_keywords)
        edu_score = sum(1 for keyword in edu_keywords if keyword in text) / len(edu_keywords)
        opp_score = sum(1 for keyword in opportunity_keywords if keyword in text) / len(opportunity_keywords)
        
        # Weight based on content category
        if content_item.category == ContentCategory.AI_NEWS:
            relevance_score = ai_score * 0.8 + edu_score * 0.2
        elif content_item.category in [ContentCategory.EDUCATION, ContentCategory.COURSES]:
            relevance_score = edu_score * 0.6 + ai_score * 0.4
        elif content_item.category == ContentCategory.OPPORTUNITIES:
            relevance_score = opp_score * 0.5 + ai_score * 0.5
        else:
            relevance_score = (ai_score + edu_score + opp_score) / 3
        
        return {
            'score': min(relevance_score * 3, 1.0),  # Amplify good matches
            'ai_relevance': ai_score,
            'educational_value': edu_score,
            'opportunity_value': opp_score
        }
    
    def assess_engagement_potential(self, content_item: ContentItem) -> Dict:
        """Assess potential for social media engagement"""
        text = f"{content_item.title} {content_item.description}".lower()
        
        # High-engagement indicators
        engagement_indicators = [
            'new', 'latest', 'breakthrough', 'revolutionary', 'amazing',
            'incredible', 'must-know', 'trending', 'viral', 'exclusive',
            'free', 'secret', 'ultimate', 'best', 'top', 'essential'
        ]
        
        # Question/discussion starters
        discussion_starters = ['?', 'what do you think', 'opinion', 'thoughts']
        
        engagement_score = content_item.engagement_score
        
        # Boost for engagement words
        engagement_words = sum(1 for word in engagement_indicators if word in text)
        engagement_score += engagement_words * 0.1
        
        # Boost for discussion potential
        discussion_potential = sum(1 for starter in discussion_starters if starter in text)
        engagement_score += discussion_potential * 0.15
        
        # Boost for valuable content
        valuable_content = sum(1 for keyword in self.valuable_keywords if keyword in text)
        engagement_score += valuable_content * 0.05
        
        return {
            'score': min(engagement_score, 1.0),
            'engagement_words': engagement_words,
            'discussion_potential': discussion_potential,
            'valuable_content': valuable_content
        }
    
    def assess_content_safety(self, text: str) -> Dict:
        """Check content safety and appropriateness"""
        text_lower = text.lower()
        
        # Check for banned words
        banned_found = [word for word in self.banned_words if word in text_lower]
        
        # Check for excessive caps (shouting)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        
        safety_score = 1.0
        
        if banned_found:
            safety_score -= len(banned_found) * 0.3
        
        if caps_ratio > 0.3:
            safety_score -= 0.2
        
        return {
            'score': max(safety_score, 0.0),
            'banned_words_found': banned_found,
            'caps_ratio': caps_ratio,
            'is_safe': safety_score > 0.7
        }
    
    def assess_freshness(self, content_item: ContentItem) -> Dict:
        """Assess content freshness"""
        from datetime import datetime, timedelta
        
        try:
            content_date = datetime.fromisoformat(content_item.created_at.replace('Z', '+00:00'))
            now = datetime.now()
            age_hours = (now - content_date).total_seconds() / 3600
            
            # Fresher content scores higher
            if age_hours <= 24:
                freshness_score = 1.0
            elif age_hours <= 72:
                freshness_score = 0.8
            elif age_hours <= 168:  # 1 week
                freshness_score = 0.6
            else:
                freshness_score = 0.4
            
            return {
                'score': freshness_score,
                'age_hours': age_hours,
                'is_fresh': age_hours <= 168
            }
        except:
            return {'score': 0.6, 'age_hours': 48, 'is_fresh': True}
    
    def filter_content(self, content_items: List[ContentItem]) -> List[Tuple[ContentItem, Dict]]:
        """Filter and rank content items by quality"""
        assessed_content = []
        
        for item in content_items:
            assessment = self.assess_content_quality(item)
            if assessment['passes_filter']:
                assessed_content.append((item, assessment))
        
        # Sort by overall score (highest first)
        assessed_content.sort(key=lambda x: x[1]['overall_score'], reverse=True)
        
        return assessed_content

# Global quality filter instance
quality_filter = ContentQualityFilter()
