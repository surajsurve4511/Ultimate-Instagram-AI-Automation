"""
Advanced orchestrator for the automated Instagram AI content pipeline.
Uses Prefect for scheduling and flow management.
"""
from prefect import flow, task
from src.generation.gemini import GeminiContentGenerator
from src.instagram.instagram import post_to_instagram
from src.monitoring.logger import log_event
from src.content.curator import content_curator
from src.vectordb.content_db import vector_db
from typing import List, Dict
import time
import random

@task
def curate_content() -> List:
    """Task to curate daily content"""
    log_event("Starting content curation")
    try:
        curated_content = content_curator.curate_daily_content()
        log_event(f"Curated {len(curated_content)} content items")
        return curated_content
    except Exception as e:
        log_event(f"Content curation failed: {e}")
        # Use fallback content
        fallback_content = content_curator.emergency_content_fallback()
        log_event(f"Using {len(fallback_content)} fallback content items")
        return fallback_content

@task
def generate_post_content(content_item, assessment) -> Dict:
    """Task to generate Instagram post content"""
    try:
        generator = GeminiContentGenerator()
        post_content = generator.generate_post_content(content_item)
        log_event(f"Generated content for: {content_item.title}")
        return post_content
    except Exception as e:
        log_event(f"Content generation failed: {e}")
        return generator.create_fallback_content(content_item)

@task
def create_post_image(content_item, post_content) -> str:
    """Task to create post image"""
    try:
        generator = GeminiContentGenerator()
        
        # Create image with text overlay
        colors = [(64, 123, 255), (123, 64, 255), (255, 64, 123), (64, 255, 123)]
        background_color = colors[hash(content_item.title) % len(colors)]
        
        # Use title for image text
        image_text = content_item.title
        if len(image_text) > 80:
            image_text = image_text[:77] + "..."
        
        img = generator.create_text_overlay_image(background_color, image_text)
        
        # Save with unique filename
        import hashlib
        image_filename = f"post_{hashlib.md5(content_item.title.encode()).hexdigest()[:8]}.png"
        img.save(image_filename)
        
        log_event(f"Created image: {image_filename}")
        return image_filename
        
    except Exception as e:
        log_event(f"Image creation failed: {e}")
        # Create simple fallback image
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (1080, 1080), (64, 123, 255))
        draw = ImageDraw.Draw(img)
        draw.text((100, 500), "AI Content", fill='white')
        fallback_name = "fallback_image.png"
        img.save(fallback_name)
        return fallback_name

@task
def post_to_instagram_task(image_path: str, caption: str) -> Dict:
    """Task to post content to Instagram"""
    try:
        # Add random delay between posts (30-60 minutes)
        delay = random.randint(1800, 3600)  # 30-60 minutes in seconds
        log_event(f"Waiting {delay//60} minutes before posting...")
        time.sleep(delay)
        
        result = post_to_instagram(image_path, caption)
        log_event(f"Posted to Instagram: {result}")
        return result
    except Exception as e:
        log_event(f"Instagram posting failed: {e}")
        return {"status": "error", "message": str(e)}

@task
def update_performance_metrics(content_item, post_result):
    """Task to update performance metrics"""
    try:
        if post_result.get("status") == "success":
            # Update engagement score based on successful posting
            vector_db.update_engagement_score(content_item.content_hash, 0.9)
            log_event(f"Updated metrics for: {content_item.title}")
    except Exception as e:
        log_event(f"Metrics update failed: {e}")

@task
def cleanup_old_data():
    """Task to cleanup old data"""
    try:
        vector_db.cleanup_old_content(days=30)
        log_event("Cleaned up old content from database")
    except Exception as e:
        log_event(f"Cleanup failed: {e}")

@flow
def daily_content_flow():
    """Main flow for daily content posting"""
    log_event("Starting daily content flow")
    
    try:
        # 1. Curate content
        curated_content = curate_content()
        
        if not curated_content:
            log_event("No content to post today")
            return
        
        # 2. Process each content item
        for content_item, assessment in curated_content:
            log_event(f"Processing: {content_item.title}")
            
            # Generate post content
            post_content = generate_post_content(content_item, assessment)
            
            # Create image
            image_path = create_post_image(content_item, post_content)
            
            # Format final caption
            final_caption = f"{post_content['caption']}\n\n{post_content['question']}\n\n{' '.join(post_content['hashtags'])}"
            
            # Post to Instagram
            post_result = post_to_instagram_task(image_path, final_caption)
            
            # Update metrics
            update_performance_metrics(content_item, post_result)
            
            # Log success
            if post_result.get("status") == "success":
                log_event(f"Successfully posted: {content_item.title}")
            else:
                log_event(f"Failed to post: {content_item.title}")
        
        # 3. Cleanup
        cleanup_old_data()
        
        log_event("Daily content flow completed")
        
    except Exception as e:
        log_event(f"Daily content flow failed: {e}")

@flow
def weekly_analytics_flow():
    """Weekly analytics and optimization flow"""
    log_event("Starting weekly analytics flow")
    
    try:
        # Analyze performance
        analysis = content_curator.analyze_performance()
        log_event(f"Performance analysis: {analysis}")
        
        # Get database stats
        stats = vector_db.get_stats()
        log_event(f"Database stats: {stats}")
        
        # Log recommendations
        if 'recommendations' in analysis:
            for rec in analysis['recommendations']:
                log_event(f"Recommendation: {rec}")
        
        log_event("Weekly analytics flow completed")
        
    except Exception as e:
        log_event(f"Weekly analytics flow failed: {e}")

@flow
def emergency_post_flow(topic: str):
    """Emergency flow for manual content posting"""
    log_event(f"Starting emergency post for topic: {topic}")
    
    try:
        from src.generation.gemini import generate_image_and_description
        
        # Generate content
        image_path, description = generate_image_and_description(topic)
        
        # Post to Instagram
        result = post_to_instagram(image_path, description)
        
        log_event(f"Emergency post result: {result}")
        return result
        
    except Exception as e:
        log_event(f"Emergency post failed: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Run daily content flow
    daily_content_flow()
