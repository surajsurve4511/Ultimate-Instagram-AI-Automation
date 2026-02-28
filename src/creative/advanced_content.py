"""
Advanced creative content generation using multiple AI models and creative techniques.
"""
import random
from typing import List, Dict, Tuple
from enum import Enum
import requests
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
from datetime import datetime

class CreativeFormat(Enum):
    CAROUSEL = "carousel"
    STORY_SERIES = "story_series"
    INFOGRAPHIC = "infographic"
    MEME = "meme"
    QUOTE_CARD = "quote_card"
    COMPARISON = "comparison"
    TIMELINE = "timeline"
    BEFORE_AFTER = "before_after"
    TUTORIAL_STEPS = "tutorial_steps"
    DATA_VISUALIZATION = "data_viz"

class AdvancedCreativeGenerator:
    def __init__(self):
        self.creative_formats = {
            CreativeFormat.CAROUSEL: self._create_carousel_content,
            CreativeFormat.INFOGRAPHIC: self._create_infographic,
            CreativeFormat.MEME: self._create_meme_content,
            CreativeFormat.COMPARISON: self._create_comparison_content,
            CreativeFormat.TUTORIAL_STEPS: self._create_tutorial_content,
            CreativeFormat.DATA_VISUALIZATION: self._create_data_viz
        }
        
        # Advanced color palettes
        self.color_schemes = {
            "neon_tech": [(255, 20, 147), (0, 255, 255), (50, 205, 50), (255, 69, 0)],
            "ai_future": [(138, 43, 226), (30, 144, 255), (0, 255, 127), (255, 215, 0)],
            "dark_mode": [(18, 18, 18), (45, 45, 45), (0, 173, 181), (255, 255, 255)],
            "gradient_sunset": [(255, 94, 77), (255, 154, 0), (255, 206, 84), (255, 238, 173)],
            "cyberpunk": [(1, 22, 39), (0, 255, 255), (255, 0, 127), (127, 255, 0)]
        }
        
        # Viral content patterns
        self.viral_patterns = [
            "Things nobody tells you about {topic}",
            "I tried {topic} for 30 days - here's what happened",
            "{number} signs you're ready for {topic}",
            "Everyone's doing {topic} wrong (here's how to fix it)",
            "The {topic} mistakes that cost me ${amount}",
            "Why {topic} will change everything in 2025",
            "{topic}: Expectation vs Reality",
            "Rate my {topic} setup 1-10",
            "POV: You just discovered {topic}",
            "Tell me you use {topic} without telling me"
        ]
    
    def generate_creative_content(self, topic: str, format_type: CreativeFormat) -> Dict:
        """Generate creative content in specified format"""
        if format_type in self.creative_formats:
            return self.creative_formats[format_type](topic)
        else:
            return self._create_standard_content(topic)
    
    def _create_carousel_content(self, topic: str) -> Dict:
        """Create multi-slide carousel content"""
        carousel_slides = [
            {
                "slide": 1,
                "title": f"🚀 Everything about {topic}",
                "content": "Swipe for mind-blowing insights →",
                "style": "title_slide"
            },
            {
                "slide": 2,
                "title": "💡 What is it?",
                "content": f"Quick explanation of {topic} in simple terms",
                "style": "explanation_slide"
            },
            {
                "slide": 3,
                "title": "📊 By the numbers",
                "content": "Statistics and data that will shock you",
                "style": "data_slide"
            },
            {
                "slide": 4,
                "title": "🔥 Why it matters",
                "content": "Real-world impact and applications",
                "style": "impact_slide"
            },
            {
                "slide": 5,
                "title": "🎯 Your next step",
                "content": "Actionable advice to get started",
                "style": "action_slide"
            },
            {
                "slide": 6,
                "title": "💬 What do you think?",
                "content": "Share your thoughts in comments!\n\nFollow for more AI insights ✨",
                "style": "engagement_slide"
            }
        ]
        
        return {
            "format": "carousel",
            "slides": carousel_slides,
            "total_slides": len(carousel_slides),
            "hashtags": ["#AICarousel", "#SwipeForMore", "#AIEducation"],
            "engagement_hook": "Swipe to see all slides! Which one surprised you most?"
        }
    
    def _create_infographic(self, topic: str) -> Dict:
        """Create infographic-style content"""
        infographic_elements = {
            "title": f"🔥 {topic.upper()} EXPLAINED",
            "sections": [
                {"icon": "📈", "title": "Growth", "stat": "300% increase in 2024"},
                {"icon": "💰", "title": "Market Value", "stat": "$50B+ industry"},
                {"icon": "🚀", "title": "Applications", "stat": "1000+ use cases"},
                {"icon": "🎯", "title": "Accuracy", "stat": "95%+ success rate"},
                {"icon": "⚡", "title": "Speed", "stat": "10x faster than before"},
                {"icon": "🌍", "title": "Global Impact", "stat": "50M+ users worldwide"}
            ],
            "footer": "Save this for later! 💾",
            "color_scheme": random.choice(list(self.color_schemes.keys()))
        }
        
        return {
            "format": "infographic",
            "elements": infographic_elements,
            "style": "modern_minimal",
            "hashtags": ["#AIInfographic", "#DataVisualization", "#TechStats"],
            "engagement_hook": "Which stat surprised you most? 👇"
        }
    
    def _create_meme_content(self, topic: str) -> Dict:
        """Create viral meme content"""
        meme_templates = [
            {
                "template": "Drake pointing",
                "top_text": f"Using {topic} the old way",
                "bottom_text": f"Using {topic} with AI",
                "style": "preference_meme"
            },
            {
                "template": "Expanding brain",
                "levels": [
                    f"Not knowing about {topic}",
                    f"Learning about {topic}",
                    f"Using {topic} daily",
                    f"Teaching others {topic}"
                ],
                "style": "evolution_meme"
            },
            {
                "template": "This is fine",
                "text": f"Me pretending I understand {topic}",
                "style": "relatable_meme"
            },
            {
                "template": "Galaxy brain",
                "text": f"When you finally understand {topic}",
                "style": "enlightenment_meme"
            }
        ]
        
        selected_meme = random.choice(meme_templates)
        
        return {
            "format": "meme",
            "template": selected_meme,
            "humor_level": "tech_savvy",
            "hashtags": ["#AIMemes", "#TechHumor", "#RelatableContent"],
            "engagement_hook": "Tag someone who needs to see this! 😂"
        }
    
    def _create_comparison_content(self, topic: str) -> Dict:
        """Create before/after or comparison content"""
        comparison_types = [
            {
                "type": "before_after",
                "before": f"Life before {topic}",
                "after": f"Life after {topic}",
                "differences": [
                    "❌ Manual work → ✅ Automated",
                    "❌ Slow process → ✅ Lightning fast",
                    "❌ Error-prone → ✅ Accurate",
                    "❌ Expensive → ✅ Cost-effective"
                ]
            },
            {
                "type": "vs_comparison",
                "option_a": f"Traditional approach",
                "option_b": f"{topic} approach",
                "criteria": ["Speed", "Accuracy", "Cost", "Ease of use"]
            }
        ]
        
        selected_comparison = random.choice(comparison_types)
        
        return {
            "format": "comparison",
            "comparison": selected_comparison,
            "visual_style": "split_screen",
            "hashtags": ["#BeforeAfter", "#Comparison", "#AIImpact"],
            "engagement_hook": "Which side are you on? 🤔"
        }
    
    def _create_tutorial_content(self, topic: str) -> Dict:
        """Create step-by-step tutorial content"""
        tutorial_steps = [
            {
                "step": 1,
                "title": "Getting Started",
                "description": f"First steps with {topic}",
                "icon": "🚀",
                "time": "2 minutes"
            },
            {
                "step": 2,
                "title": "Setup Process",
                "description": "Easy configuration guide",
                "icon": "⚙️",
                "time": "5 minutes"
            },
            {
                "step": 3,
                "title": "Advanced Features",
                "description": "Unlock hidden potential",
                "icon": "🔓",
                "time": "10 minutes"
            },
            {
                "step": 4,
                "title": "Pro Tips",
                "description": "Expert-level techniques",
                "icon": "💡",
                "time": "5 minutes"
            },
            {
                "step": 5,
                "title": "Troubleshooting",
                "description": "Common issues solved",
                "icon": "🔧",
                "time": "3 minutes"
            }
        ]
        
        return {
            "format": "tutorial",
            "steps": tutorial_steps,
            "total_time": "25 minutes",
            "difficulty": "Beginner-friendly",
            "hashtags": ["#AITutorial", "#StepByStep", "#LearnAI"],
            "engagement_hook": "Which step do you want me to explain more? 🤓"
        }
    
    def _create_data_viz(self, topic: str) -> Dict:
        """Create data visualization content"""
        viz_types = [
            {
                "type": "progress_chart",
                "title": f"{topic} Adoption Over Time",
                "data_points": [
                    {"year": "2020", "value": 15},
                    {"year": "2021", "value": 35},
                    {"year": "2022", "value": 58},
                    {"year": "2023", "value": 78},
                    {"year": "2024", "value": 92}
                ]
            },
            {
                "type": "pie_chart",
                "title": f"Top {topic} Use Cases",
                "segments": [
                    {"label": "Business Automation", "value": 35},
                    {"label": "Personal Productivity", "value": 25},
                    {"label": "Creative Projects", "value": 20},
                    {"label": "Education", "value": 15},
                    {"label": "Research", "value": 5}
                ]
            }
        ]
        
        selected_viz = random.choice(viz_types)
        
        return {
            "format": "data_visualization",
            "visualization": selected_viz,
            "style": "modern_clean",
            "color_palette": random.choice(list(self.color_schemes.keys())),
            "hashtags": ["#DataVisualization", "#AIStats", "#TechData"],
            "engagement_hook": "What's your primary use case? 📊"
        }
    
    def create_viral_image(self, content: Dict, dimensions: Tuple[int, int] = (1080, 1080)) -> Image.Image:
        """Create viral-optimized image based on content format"""
        width, height = dimensions
        
        # Select color scheme
        color_scheme_name = content.get('color_scheme', random.choice(list(self.color_schemes.keys())))
        colors = self.color_schemes[color_scheme_name]
        
        # Create base image with gradient
        img = Image.new('RGB', dimensions, colors[0])
        
        # Add gradient background
        for y in range(height):
            progress = y / height
            color = self._interpolate_color(colors[0], colors[1], progress)
            for x in range(width):
                img.putpixel((x, y), color)
        
        # Add creative elements based on format
        if content.get('format') == 'meme':
            img = self._add_meme_elements(img, content)
        elif content.get('format') == 'infographic':
            img = self._add_infographic_elements(img, content)
        elif content.get('format') == 'comparison':
            img = self._add_comparison_elements(img, content)
        
        # Add viral indicators
        img = self._add_viral_indicators(img)
        
        return img
    
    def _interpolate_color(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Interpolate between two colors"""
        return tuple(int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3))
    
    def _add_viral_indicators(self, img: Image.Image) -> Image.Image:
        """Add viral indicators like trending arrows, fire emojis, etc."""
        draw = ImageDraw.Draw(img)
        
        # Add trending indicator
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Add "VIRAL" or "TRENDING" text
        viral_text = random.choice(["🔥 VIRAL", "📈 TRENDING", "⚡ HOT"])
        draw.text((50, 50), viral_text, font=font, fill='white')
        
        return img
    
    def _add_meme_elements(self, img: Image.Image, content: Dict) -> Image.Image:
        """Add meme-specific elements"""
        # This would add meme template overlays
        return img
    
    def _add_infographic_elements(self, img: Image.Image, content: Dict) -> Image.Image:
        """Add infographic elements"""
        # This would add charts, icons, and data visualization
        return img
    
    def _add_comparison_elements(self, img: Image.Image, content: Dict) -> Image.Image:
        """Add comparison elements"""
        # This would add split-screen or before/after layouts
        return img
    
    def generate_viral_hook(self, topic: str) -> str:
        """Generate viral opening hook"""
        viral_hooks = [
            f"POV: You just discovered {topic} 🤯",
            f"Everyone's sleeping on {topic} (here's why you shouldn't)",
            f"I used {topic} for 30 days and this happened...",
            f"The {topic} secret that nobody talks about:",
            f"Rate my {topic} setup from 1-10 💯",
            f"Tell me you use {topic} without telling me you use {topic}",
            f"Things I wish I knew before starting with {topic}:",
            f"Plot twist: {topic} isn't what you think it is",
            f"Why {topic} will be everywhere in 2025:",
            f"The {topic} trend that's taking over TikTok"
        ]
        
        return random.choice(viral_hooks)
    
    def _create_standard_content(self, topic: str) -> Dict:
        """Fallback for standard content creation"""
        return {
            "format": "standard",
            "title": topic,
            "viral_hook": self.generate_viral_hook(topic),
            "hashtags": ["#AI", "#Technology", "#Innovation"],
            "engagement_hook": "What are your thoughts on this? 💭"
        }

# Global creative generator
creative_generator = AdvancedCreativeGenerator()
