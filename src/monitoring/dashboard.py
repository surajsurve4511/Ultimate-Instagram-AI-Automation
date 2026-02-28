"""
Simple dashboard for monitoring and managing the Instagram automation system.
"""
from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from src.vectordb.content_db import vector_db
from src.content.curator import content_curator
from src.orchestrator.scheduler import instagram_scheduler
from src.orchestrator.main import emergency_post_flow
from src.instagram.instagram import instagram_poster

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        # Get system stats
        db_stats = vector_db.get_stats()
        performance_analysis = content_curator.analyze_performance()
        next_runs = instagram_scheduler.get_next_runs()
        
        # Get account stats
        account_stats = instagram_poster.get_account_stats()
        
        dashboard_data = {
            "db_stats": db_stats,
            "performance": performance_analysis,
            "next_runs": next_runs,
            "account_stats": account_stats,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/content')
def recent_content():
    """Get recent content"""
    try:
        days = request.args.get('days', 7, type=int)
        recent_content = vector_db.get_recent_content(days=days)
        return jsonify({"content": recent_content})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/content/category/<category>')
def content_by_category(category):
    """Get content by category"""
    try:
        limit = request.args.get('limit', 10, type=int)
        content = vector_db.get_content_by_category(category, limit=limit)
        return jsonify({"content": content})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/post/emergency', methods=['POST'])
def emergency_post():
    """Trigger emergency post"""
    try:
        data = request.get_json()
        topic = data.get('topic', 'AI Technology Update')
        
        result = emergency_post_flow(topic)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/scheduler/status')
def scheduler_status():
    """Get scheduler status"""
    try:
        return jsonify({
            "is_running": instagram_scheduler.is_running,
            "next_runs": instagram_scheduler.get_next_runs()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/scheduler/start', methods=['POST'])
def start_scheduler():
    """Start the scheduler"""
    try:
        instagram_scheduler.start_scheduler()
        return jsonify({"status": "Scheduler started"})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler"""
    try:
        instagram_scheduler.stop_scheduler()
        return jsonify({"status": "Scheduler stopped"})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/trending')
def trending_topics():
    """Get trending topics"""
    try:
        trends = content_curator.get_trending_topics()
        return jsonify({"trends": trends})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/cleanup', methods=['POST'])
def cleanup_old_data():
    """Cleanup old data"""
    try:
        days = request.args.get('days', 30, type=int)
        vector_db.cleanup_old_content(days=days)
        return jsonify({"status": f"Cleaned up content older than {days} days"})
        
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
