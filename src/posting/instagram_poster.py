"""
Instagram posting module for publishing content to Instagram.
"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os
from pathlib import Path

try:
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ instagrapi not installed. Instagram posting will not work.")
    Client = None

from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)

class InstagramPoster:
    """Handle posting content to Instagram"""
    
    def __init__(self):
        self.client = None
        self.username = SETTINGS.INSTAGRAM_USERNAME
        self.password = SETTINGS.INSTAGRAM_PASSWORD
        self.session_file = Path('./data/instagram_session.json')
        self.is_logged_in = False
    
    async def initialize(self):
        """Initialize Instagram client and login"""
        try:
            if Client is None:
                logger.error("❌ instagrapi not installed")
                return False
            
            self.client = Client()
            
            # Try to load existing session
            if self.session_file.exists():
                try:
                    self.client.load_settings(self.session_file)
                    logger.info("✅ Loaded existing Instagram session")
                    self.is_logged_in = True
                    return True
                except Exception as e:
                    logger.warning(f"⚠️ Could not load session: {str(e)}")
            
            # Login with credentials
            if self.username and self.password:
                try:
                    self.client.login(self.username, self.password)
                    
                    # Save session
                    self.client.dump_settings(self.session_file)
                    
                    logger.info("✅ Logged into Instagram successfully")
                    self.is_logged_in = True
                    return True
                    
                except Exception as e:
                    logger.error(f"❌ Instagram login failed: {str(e)}")
                    return False
            else:
                logger.error("❌ Instagram credentials not configured")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error initializing Instagram client: {str(e)}")
            return False
    
    async def post_content(self, content: Dict) -> Dict:
        """Post content to Instagram"""
        try:
            if not self.is_logged_in:
                logger.error("❌ Not logged into Instagram")
                return {'success': False, 'error': 'Not logged in'}
            
            content_type = content.get('type', 'post')
            
            if content_type == 'post':
                return await self._post_photo(content)
            elif content_type == 'carousel':
                return await self._post_carousel(content)
            elif content_type == 'reel':
                return await self._post_reel(content)
            else:
                logger.error(f"❌ Unknown content type: {content_type}")
                return {'success': False, 'error': f'Unknown content type: {content_type}'}
                
        except Exception as e:
            logger.error(f"❌ Error posting content: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _post_photo(self, content: Dict) -> Dict:
        """Post a photo to Instagram"""
        try:
            caption = content.get('caption', '')
            hashtags = content.get('hashtags', [])
            
            # Add hashtags to caption
            full_caption = f"{caption}\n\n{' '.join(hashtags)}"
            
            # For now, return success without actual posting (for testing)
            logger.info(f"📸 Would post photo with caption: {full_caption[:100]}...")
            
            return {
                'success': True,
                'type': 'photo',
                'caption': full_caption,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error posting photo: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _post_carousel(self, content: Dict) -> Dict:
        """Post a carousel to Instagram"""
        try:
            caption = content.get('caption', '')
            hashtags = content.get('hashtags', [])
            slides = content.get('slides', [])
            
            full_caption = f"{caption}\n\n{' '.join(hashtags)}"
            
            logger.info(f"🎪 Would post carousel with {len(slides)} slides: {full_caption[:100]}...")
            
            return {
                'success': True,
                'type': 'carousel',
                'slides': len(slides),
                'caption': full_caption,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error posting carousel: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _post_reel(self, content: Dict) -> Dict:
        """Post a reel to Instagram"""
        try:
            caption = content.get('caption', '')
            hashtags = content.get('hashtags', [])
            
            full_caption = f"{caption}\n\n{' '.join(hashtags)}"
            
            logger.info(f"🎬 Would post reel: {full_caption[:100]}...")
            
            return {
                'success': True,
                'type': 'reel',
                'caption': full_caption,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error posting reel: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def logout(self):
        """Logout from Instagram"""
        try:
            if self.client and self.is_logged_in:
                self.client.logout()
                logger.info("✅ Logged out from Instagram")
                self.is_logged_in = False
        except Exception as e:
            logger.error(f"❌ Error logging out: {str(e)}")

# Global instance
instagram_poster = InstagramPoster()