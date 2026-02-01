"""
Configuration settings for X Automation Bot
Loads environment variables and provides configuration constants
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# X (Twitter) API Credentials
X_API_KEY = os.getenv("X_API_KEY", "")
X_API_SECRET = os.getenv("X_API_SECRET", "")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN", "")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET", "")

# Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Bot Settings
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
POST_HOUR = int(os.getenv("POST_HOUR", "19"))
POST_MINUTE = int(os.getenv("POST_MINUTE", "0"))

# RSS Feed Sources for AI and Development News
RSS_FEEDS = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "AI"
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "category": "AI"
    },
    {
        "name": "The Verge Tech",
        "url": "https://www.theverge.com/rss/tech/index.xml",
        "category": "Tech"
    },
    {
        "name": "Dev.to AI",
        "url": "https://dev.to/feed/tag/ai",
        "category": "Development"
    },
    {
        "name": "Hacker News Best",
        "url": "https://hnrss.org/best",
        "category": "Tech"
    }
]

# Groq Model Configuration
GROQ_MODEL = "llama-3.1-8b-instant"  # Fast and free

def validate_config():
    """Validate that all required configuration is present"""
    errors = []
    
    if not X_API_KEY:
        errors.append("X_API_KEY is not set")
    if not X_API_SECRET:
        errors.append("X_API_SECRET is not set")
    if not X_ACCESS_TOKEN:
        errors.append("X_ACCESS_TOKEN is not set")
    if not X_ACCESS_TOKEN_SECRET:
        errors.append("X_ACCESS_TOKEN_SECRET is not set")
    if not GROQ_API_KEY:
        errors.append("GROQ_API_KEY is not set")
    
    return errors
