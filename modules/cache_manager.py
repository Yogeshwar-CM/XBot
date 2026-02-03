"""
Cache Manager Module
Tracks posted content to prevent duplicates
"""

import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "posted_content.json"
MAX_CACHE_ENTRIES = 100  # Keep last 100 posts


def _ensure_cache_dir():
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(exist_ok=True)


def _generate_content_hash(text: str) -> str:
    """
    Generate a hash of the content to check for duplicates.

    Args:
        text: Tweet text

    Returns:
        SHA256 hash (first 16 chars)
    """
    return hashlib.sha256(text.lower().strip().encode()).hexdigest()[:16]


def load_cache() -> Dict:
    """
    Load posted content cache from disk.

    Returns:
        Dict with 'posts' list
    """
    _ensure_cache_dir()

    if not CACHE_FILE.exists():
        logger.info("📂 Cache file not found, creating new one")
        return {"posts": []}

    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
            logger.info(f"📂 Loaded cache with {len(cache.get('posts', []))} entries")
            return cache
    except Exception as e:
        logger.warning(f"Error loading cache: {e}, starting fresh")
        return {"posts": []}


def save_cache(cache: Dict):
    """
    Save posted content cache to disk.

    Args:
        cache: Cache dict to save
    """
    _ensure_cache_dir()

    # Trim cache if too large
    posts = cache.get("posts", [])
    if len(posts) > MAX_CACHE_ENTRIES:
        cache["posts"] = posts[-MAX_CACHE_ENTRIES:]
        logger.info(f"🗑️ Trimmed cache to last {MAX_CACHE_ENTRIES} entries")

    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
        logger.info(f"💾 Saved cache with {len(cache.get('posts', []))} entries")
    except Exception as e:
        logger.error(f"Error saving cache: {e}")


def is_duplicate(tweet: str, cache: Optional[Dict] = None) -> bool:
    """
    Check if tweet content is a duplicate of recently posted content.

    Args:
        tweet: Tweet text to check
        cache: Optional cache dict (will load if not provided)

    Returns:
        True if duplicate, False otherwise
    """
    if cache is None:
        cache = load_cache()

    content_hash = _generate_content_hash(tweet)
    posts = cache.get("posts", [])

    # Check if hash exists in cache
    for post in posts:
        if post.get("hash") == content_hash:
            logger.warning(f"⚠️ Duplicate detected! Posted on {post.get('posted_at')}")
            return True

    return False


def add_to_cache(tweet: str, tweet_id: Optional[str] = None) -> Dict:
    """
    Add posted tweet to cache.

    Args:
        tweet: Tweet text
        tweet_id: Optional tweet ID

    Returns:
        Updated cache dict
    """
    cache = load_cache()

    content_hash = _generate_content_hash(tweet)

    # Add new post entry
    post_entry = {
        "hash": content_hash,
        "text_preview": tweet[:50] + "..." if len(tweet) > 50 else tweet,
        "posted_at": datetime.utcnow().isoformat() + "Z",
        "tweet_id": tweet_id,
    }

    cache.setdefault("posts", []).append(post_entry)

    # Save to disk
    save_cache(cache)

    logger.info(f"✅ Added to cache: {post_entry['text_preview']}")
    return cache


def get_recent_posts(limit: int = 10) -> list:
    """
    Get recent posts from cache for LLM context.

    Args:
        limit: Number of recent posts to retrieve

    Returns:
        List of recent post text previews
    """
    cache = load_cache()
    posts = cache.get("posts", [])

    # Get last N posts
    recent = posts[-limit:] if len(posts) > limit else posts

    # Return just the text previews
    return [post.get("text_preview", "") for post in reversed(recent)]


if __name__ == "__main__":
    # Test the cache manager
    logging.basicConfig(level=logging.INFO)

    # Test adding and checking duplicates
    test_tweet = "just saw devs arguing about tabs vs spaces again on HN... in 2026 lol 💀 #AI #Tech"

    print(f"\n🧪 Testing cache manager with: '{test_tweet}'\n")

    # Check if duplicate (should be False first time)
    is_dup = is_duplicate(test_tweet)
    print(f"Is duplicate? {is_dup}")

    # Add to cache
    add_to_cache(test_tweet, tweet_id="123456789")

    # Check again (should be True now)
    is_dup = is_duplicate(test_tweet)
    print(f"Is duplicate now? {is_dup}")

    # Check similar but different tweet
    different_tweet = "devs still arguing about tabs vs spaces lmao #Tech"
    is_dup = is_duplicate(different_tweet)
    print(f"Is different tweet duplicate? {is_dup}")
