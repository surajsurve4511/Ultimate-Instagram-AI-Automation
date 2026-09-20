"""
Main entry point for the Instagram AI automation system.
"""
import sys
import os
import argparse
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.orchestrator.scheduler import instagram_scheduler
from src.orchestrator.main import daily_content_flow, emergency_post_flow
from src.monitoring.dashboard import app as dashboard_app
from src.monitoring.logger import log_event
from src.vectordb.content_db import vector_db

def main():
    parser = argparse.ArgumentParser(description='Instagram AI Content Automation System')
    parser.add_argument('command', choices=['run', 'schedule', 'dashboard', 'post', 'stats'], 
                       help='Command to execute')
    parser.add_argument('--topic', type=str, help='Topic for emergency post')
    parser.add_argument('--port', type=int, default=5000, help='Port for dashboard')
    
    args = parser.parse_args()
    
    print("🤖 Instagram AI Content Automation System")
    print("=" * 50)
    
    if args.command == 'run':
        print("🚀 Running daily content flow...")
        log_event("Manual daily content flow started")
        daily_content_flow()
        print("✅ Daily content flow completed")
        
    elif args.command == 'schedule':
        print("⏰ Starting automated scheduler...")
        print("📅 Posts scheduled for: 9 AM, 2 PM, 6 PM daily")
        print("📊 Weekly analytics: Sundays at 10 AM")
        print("🔥 Trending content: Every 4 hours")
        print("\nPress Ctrl+C to stop...")
        
        try:
            instagram_scheduler.start_scheduler()
            while True:
                import time
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n🛑 Stopping scheduler...")
            instagram_scheduler.stop_scheduler()
            print("✅ Scheduler stopped")
            
    elif args.command == 'dashboard':
        print(f"📊 Starting web dashboard on port {args.port}...")
        print(f"🌐 Access at: http://localhost:{args.port}")
        print("\nPress Ctrl+C to stop...")
        
        try:
            dashboard_app.run(debug=False, host='0.0.0.0', port=args.port)
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped")
            
    elif args.command == 'post':
        if not args.topic:
            print("❌ Error: --topic required for emergency post")
            return
            
        print(f"📱 Creating emergency post about: {args.topic}")
        result = emergency_post_flow(args.topic)
        
        if result.get('status') == 'success':
            print("✅ Emergency post created successfully!")
        else:
            print(f"❌ Emergency post failed: {result.get('message', 'Unknown error')}")
            
    elif args.command == 'stats':
        print("📈 System Statistics")
        print("-" * 30)
        
        # Database stats
        db_stats = vector_db.get_stats()
        print(f"Total content items: {db_stats.get('total_content', 0)}")
        print(f"Last updated: {db_stats.get('last_updated', 'Unknown')}")
        
        if 'category_breakdown' in db_stats:
            print("\nContent by category:")
            for category, count in db_stats['category_breakdown'].items():
                print(f"  {category}: {count}")
        
        # Recent content
        recent = vector_db.get_recent_content(days=7)
        print(f"\nContent posted in last 7 days: {len(recent)}")
        
        # Performance analysis
        from src.content.curator import content_curator
        analysis = content_curator.analyze_performance()
        
        if 'recommendations' in analysis:
            print("\nRecommendations:")
            for rec in analysis['recommendations']:
                print(f"  • {rec}")
    
    print("\n🎯 System ready for AI-powered Instagram automation!")

if __name__ == '__main__':
    main()
