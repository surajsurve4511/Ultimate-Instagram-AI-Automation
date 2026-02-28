"""
Ultimate Instagram Automation System
Main package initialization
"""
__version__ = '1.0.0'
__author__ = 'Ultimate AI Team'

# Import main components for easy access
from .config import SETTINGS
from .orchestration import UltimateCrowdMaster

__all__ = ['SETTINGS', 'UltimateCrowdMaster', '__version__']
