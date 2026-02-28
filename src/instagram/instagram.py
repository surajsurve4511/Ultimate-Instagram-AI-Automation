"""
Advanced Instagram posting module with multiple authentication methods.
"""
import os
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from typing import Optional, Dict
import time
import random
from pathlib import Path

class InstagramPoster:
    def __init__(self):
        self.client = Client()
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.session_file = "instagram_session.json"
        
    def login(self) -> bool:
        """Login to Instagram with session management"""
        try:
            # Try to load existing session
            if os.path.exists(self.session_file):
                self.client.load_settings(self.session_file)
                self.client.login(self.username, self.password)
                
                # Verify session is valid
                try:
                    self.client.user_info_by_username(self.username)
                    print("Logged in using saved session")
                    return True
                except LoginRequired:
                    print("Session expired, logging in fresh")
            
            # Fresh login
            self.client.login(self.username, self.password)
            self.client.dump_settings(self.session_file)
            print("Fresh login successful")
            return True
            
        except Exception as e:
            print(f"Instagram login failed: {e}")
            return False
    
    def post_to_instagram(self, image_path: str, description: str) -> Dict:
        """Post image with description to Instagram"""
        try:
            if not self.login():
                return {"status": "error", "message": "Login failed"}
            
            # Validate image exists
            if not os.path.exists(image_path):
                return {"status": "error", "message": "Image file not found"}
            
            # Add random delay to avoid detection
            time.sleep(random.uniform(5, 15))
            
            # Upload photo
            media = self.client.photo_upload(
                path=Path(image_path),
                caption=description
            )
            
            return {
                "status": "success", 
                "message": "Posted successfully",
                "media_id": media.id,
                "media_url": f"https://instagram.com/p/{media.code}/"
            }
            
        except Exception as e:
            print(f"Instagram posting failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def post_carousel(self, image_paths: list, description: str) -> Dict:
        """Post multiple images as carousel"""
        try:
            if not self.login():
                return {"status": "error", "message": "Login failed"}
            
            # Validate all images exist
            for path in image_paths:
                if not os.path.exists(path):
                    return {"status": "error", "message": f"Image not found: {path}"}
            
            # Add random delay
            time.sleep(random.uniform(10, 20))
            
            # Convert to Path objects
            paths = [Path(path) for path in image_paths]
            
            # Upload album
            media = self.client.album_upload(
                paths=paths,
                caption=description
            )
            
            return {
                "status": "success",
                "message": "Carousel posted successfully", 
                "media_id": media.id,
                "media_url": f"https://instagram.com/p/{media.code}/"
            }
            
        except Exception as e:
            print(f"Carousel posting failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_account_stats(self) -> Dict:
        """Get account statistics"""
        try:
            if not self.login():
                return {"status": "error", "message": "Login failed"}
            
            user_info = self.client.user_info_by_username(self.username)
            
            return {
                "followers": user_info.follower_count,
                "following": user_info.following_count,
                "posts": user_info.media_count,
                "username": user_info.username,
                "full_name": user_info.full_name,
                "biography": user_info.biography
            }
            
        except Exception as e:
            print(f"Error getting account stats: {e}")
            return {"status": "error", "message": str(e)}
    
    def schedule_post(self, image_path: str, description: str, delay_minutes: int = 0) -> Dict:
        """Schedule a post for later (basic implementation)"""
        if delay_minutes > 0:
            print(f"Scheduling post for {delay_minutes} minutes from now")
            time.sleep(delay_minutes * 60)
        
        return self.post_to_instagram(image_path, description)

# Global Instagram poster instance
instagram_poster = InstagramPoster()

def post_to_instagram(image_path: str, description: str) -> Dict:
    """Main function for posting to Instagram"""
    return instagram_poster.post_to_instagram(image_path, description)
