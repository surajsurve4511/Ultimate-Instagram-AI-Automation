"""
Ultimate Instagram AI Automation System
Main package initialization — Multi-User Product Architecture
"""

__version__ = "2.0.0"
__author__ = "Ultimate AI Team"

# Note: We don't import heavy modules here to avoid circular imports
# and to keep startup fast. Import what you need directly:
#
#   from src.config.settings import SETTINGS
#   from src.database import User, InstagramAccount, get_session
#   from src.auth.auth_service import create_access_token

__all__ = ["__version__"]
