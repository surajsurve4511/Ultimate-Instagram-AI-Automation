"""
Scheduler for automated Instagram posting using various scheduling methods.
"""
import schedule
import time
from datetime import datetime, timedelta
import threading
import os
from src.orchestrator.main import daily_content_flow, weekly_analytics_flow, emergency_post_flow
from src.monitoring.logger import log_event

class InstagramScheduler:
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
        
    def setup_schedule(self):
        """Setup the posting schedule"""
        # Daily content posting at 9 AM, 2 PM, and 6 PM
        schedule.every().day.at("09:00").do(self.run_daily_content)
        schedule.every().day.at("14:00").do(self.run_daily_content)
        schedule.every().day.at("18:00").do(self.run_daily_content)
        
        # Weekly analytics on Sundays at 10 AM
        schedule.every().sunday.at("10:00").do(self.run_weekly_analytics)
        
        # Trending content check every 4 hours
        schedule.every(4).hours.do(self.check_trending_content)
        
        log_event("Schedule setup completed")
    
    def run_daily_content(self):
        """Run the daily content flow"""
        try:
            log_event("Scheduled daily content flow starting")
            daily_content_flow()
        except Exception as e:
            log_event(f"Scheduled daily content flow failed: {e}")
    
    def run_weekly_analytics(self):
        """Run the weekly analytics flow"""
        try:
            log_event("Scheduled weekly analytics starting")
            weekly_analytics_flow()
        except Exception as e:
            log_event(f"Scheduled weekly analytics failed: {e}")
    
    def check_trending_content(self):
        """Check for trending content and post if relevant"""
        try:
            from src.content.curator import content_curator
            trending_topics = content_curator.get_trending_topics()
            
            # Post about the most relevant trending topic
            if trending_topics:
                topic = trending_topics[0]
                log_event(f"Posting trending content: {topic}")
                emergency_post_flow(topic)
                
        except Exception as e:
            log_event(f"Trending content check failed: {e}")
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        if self.is_running:
            log_event("Scheduler already running")
            return
        
        self.setup_schedule()
        self.is_running = True
        
        def run_scheduler():
            log_event("Instagram scheduler started")
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        log_event("Instagram scheduler stopped")
    
    def get_next_runs(self):
        """Get information about next scheduled runs"""
        jobs = schedule.get_jobs()
        next_runs = []
        
        for job in jobs:
            next_runs.append({
                "job": str(job.job_func),
                "next_run": job.next_run.strftime("%Y-%m-%d %H:%M:%S") if job.next_run else "Not scheduled"
            })
        
        return next_runs

# Global scheduler instance
instagram_scheduler = InstagramScheduler()

if __name__ == "__main__":
    # Start the scheduler
    instagram_scheduler.start_scheduler()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        instagram_scheduler.stop_scheduler()
        print("Scheduler stopped.")
