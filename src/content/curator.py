"""
Content curation and intelligent selection system.
"""
from typing import List, Tuple, Dict
from src.content.categories import ContentItem, ContentCategory
from src.scraping.content_scraper import collect_all_content
from src.vectordb.content_db import vector_db
from src.quality.content_filter import quality_filter
from datetime import datetime, timedelta
import random

class ContentCurator:
    def __init__(self):
        self.daily_post_limit = 3
        self.category_weights = {
            ContentCategory.AI_NEWS: 0.3,
            ContentCategory.EDUCATION: 0.25,
            ContentCategory.TOOLS: 0.2,
            ContentCategory.OPPORTUNITIES: 0.15,
            ContentCategory.COURSES: 0.1
        }
    
    def curate_daily_content(self) -> List[Tuple[ContentItem, Dict]]:
        """Curate the best content for today's posts"""
        print("Starting daily content curation...")
        
        # 1. Collect fresh content from all sources
        print("Collecting content from sources...")
        raw_content = collect_all_content()
        print(f"Collected {len(raw_content)} raw content items")
        
        # 2. Filter out duplicates and low-quality content
        print("Filtering content quality...")
        filtered_content = quality_filter.filter_content(raw_content)
        print(f"Filtered to {len(filtered_content)} high-quality items")
        
        # 3. Remove content already posted (check vector DB)
        print("Checking for duplicates in vector DB...")
        unique_content = []
        for item, assessment in filtered_content:
            if not vector_db.is_duplicate(item.content_hash) and \
               not vector_db.check_similarity(item, threshold=0.8):
                unique_content.append((item, assessment))
        
        print(f"Found {len(unique_content)} unique content items")
        
        # 4. Diversify by category
        print("Diversifying content by category...")
        diverse_content = self.diversify_content(unique_content)
        
        # 5. Select best content for posting
        selected_content = diverse_content[:self.daily_post_limit]
        
        # 6. Add to vector DB to prevent future duplicates
        for item, _ in selected_content:
            vector_db.add_content(item)
        
        print(f"Selected {len(selected_content)} items for posting")
        return selected_content
    
    def diversify_content(self, content_list: List[Tuple[ContentItem, Dict]]) -> List[Tuple[ContentItem, Dict]]:
        """Ensure diverse content across categories"""
        categorized_content = {}
        
        # Group by category
        for item, assessment in content_list:
            category = item.category
            if category not in categorized_content:
                categorized_content[category] = []
            categorized_content[category].append((item, assessment))
        
        # Sort each category by quality score
        for category in categorized_content:
            categorized_content[category].sort(
                key=lambda x: x[1]['overall_score'], 
                reverse=True
            )
        
        # Select diverse content based on weights
        diverse_selection = []
        total_slots = self.daily_post_limit * 2  # Get more for buffer
        
        for category, weight in self.category_weights.items():
            if category in categorized_content:
                slots_for_category = max(1, int(total_slots * weight))
                category_items = categorized_content[category][:slots_for_category]
                diverse_selection.extend(category_items)
        
        # Sort final selection by overall score
        diverse_selection.sort(key=lambda x: x[1]['overall_score'], reverse=True)
        
        return diverse_selection
    
    def get_trending_topics(self) -> List[str]:
        """Get trending AI topics for proactive content creation"""
        # This could integrate with Twitter API, Google Trends, etc.
        trending_topics = [
            "ChatGPT updates",
            "AI coding assistants", 
            "Machine learning courses",
            "AI job opportunities",
            "New AI tools",
            "AI ethics",
            "Generative AI",
            "AI in healthcare",
            "AI startups",
            "Open source AI"
        ]
        
        # Add some randomness and current relevance
        current_trends = random.sample(trending_topics, 3)
        return current_trends
    
    def emergency_content_fallback(self) -> List[Tuple[ContentItem, Dict]]:
        """Generate fallback content when scraping fails"""
        fallback_topics = [
            "10 Free AI Courses You Should Take This Week",
            "Latest AI Tools Every Developer Should Know",
            "AI Job Market: What Skills Are In Demand?",
            "How AI is Transforming Education",
            "Best Practices for Learning Machine Learning"
        ]
        
        fallback_content = []
        for topic in fallback_topics[:self.daily_post_limit]:
            from src.content.categories import ContentItem
            import hashlib
            
            item = ContentItem(
                title=topic,
                description=f"Educational content about {topic}. Perfect for anyone interested in AI and technology.",
                category=ContentCategory.EDUCATION,
                source_url="https://example.com",
                content_hash=hashlib.md5(topic.encode()).hexdigest(),
                engagement_score=0.7,
                created_at=datetime.now().isoformat(),
                tags=["ai", "education", "learning"]
            )
            
            assessment = {
                'overall_score': 0.75,
                'passes_filter': True
            }
            
            fallback_content.append((item, assessment))
        
        return fallback_content
    
    def analyze_performance(self) -> Dict:
        """Analyze content performance and optimize strategy"""
        try:
            recent_content = vector_db.get_recent_content(days=30)
            
            if not recent_content:
                return {"message": "No recent content to analyze"}
            
            # Analyze category performance
            category_performance = {}
            for content in recent_content:
                category = content['category']
                engagement = float(content.get('engagement_score', 0))
                
                if category not in category_performance:
                    category_performance[category] = {'total_score': 0, 'count': 0}
                
                category_performance[category]['total_score'] += engagement
                category_performance[category]['count'] += 1
            
            # Calculate averages
            for category in category_performance:
                avg_score = category_performance[category]['total_score'] / category_performance[category]['count']
                category_performance[category]['average_engagement'] = avg_score
            
            # Get best performing category
            best_category = max(category_performance.keys(), 
                              key=lambda x: category_performance[x]['average_engagement'])
            
            return {
                "total_posts": len(recent_content),
                "category_performance": category_performance,
                "best_performing_category": best_category,
                "recommendations": self.generate_recommendations(category_performance)
            }
            
        except Exception as e:
            print(f"Error analyzing performance: {e}")
            return {"error": str(e)}
    
    def generate_recommendations(self, performance_data: Dict) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Find underperforming categories
        avg_scores = [data['average_engagement'] for data in performance_data.values()]
        overall_avg = sum(avg_scores) / len(avg_scores) if avg_scores else 0
        
        for category, data in performance_data.items():
            if data['average_engagement'] < overall_avg * 0.8:
                recommendations.append(f"Consider reducing {category} content - below average performance")
            elif data['average_engagement'] > overall_avg * 1.2:
                recommendations.append(f"Increase {category} content - performing well")
        
        if not recommendations:
            recommendations.append("Content performance is balanced across categories")
        
        return recommendations

# Global content curator instance
content_curator = ContentCurator()
