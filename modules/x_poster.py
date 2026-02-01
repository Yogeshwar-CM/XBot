"""
X Poster Module
Posts tweets to X (Twitter) using API v2 via Tweepy
Includes duplicate detection using local cache
"""

import hashlib
import json
import logging
from pathlib import Path
import tweepy

from config.settings import (
    X_API_KEY,
    X_API_SECRET,
    X_ACCESS_TOKEN,
    X_ACCESS_TOKEN_SECRET,
    DRY_RUN,
)

logger = logging.getLogger(__name__)

# Cache file for storing recent tweet hashes (prevents duplicates)
CACHE_FILE = Path(__file__).parent.parent / "tweet_history.json"
MAX_HISTORY = 10


def _get_tweet_hash(text: str) -> str:
    """Generate a hash of tweet content for duplicate detection."""
    # Normalize: lowercase, remove extra spaces
    normalized = " ".join(text.lower().split())
    return hashlib.md5(normalized.encode()).hexdigest()[:16]


def _load_history() -> list:
    """Load tweet history from cache file."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_history(history: list):
    """Save tweet history to cache file."""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(history[-MAX_HISTORY:], f)
    except IOError as e:
        logger.warning(f"Could not save tweet history: {e}")


def is_duplicate(text: str) -> bool:
    """
    Check if a tweet is a duplicate of recent tweets.

    Args:
        text: Tweet content to check

    Returns:
        True if duplicate, False otherwise
    """
    tweet_hash = _get_tweet_hash(text)
    history = _load_history()
    return tweet_hash in history


def get_client() -> tweepy.Client:
    """
    Create and return an authenticated Tweepy Client for X API v2.

    Returns:
        Authenticated tweepy.Client instance
    """
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        raise ValueError("X API credentials are not fully configured")

    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
    )

    return client


def post_tweet(text: str, dry_run: bool = None) -> dict:
    """
    Post a tweet to X.

    Args:
        text: The tweet content (max 280 characters)
        dry_run: If True, log but don't actually post. Defaults to config setting.

    Returns:
        Response dict with tweet info or dry_run status
    """
    if dry_run is None:
        dry_run = DRY_RUN

    # Validate tweet length
    if len(text) > 280:
        raise ValueError(f"Tweet exceeds 280 characters: {len(text)}")

    # Check for duplicates
    if is_duplicate(text):
        logger.warning("⚠️ Duplicate tweet detected, skipping...")
        return {"duplicate": True, "text": text}

    if dry_run:
        logger.info(f"[DRY RUN] Would post tweet ({len(text)} chars):\n{text}")
        return {"dry_run": True, "text": text, "length": len(text)}

    try:
        client = get_client()

        response = client.create_tweet(text=text)

        tweet_id = response.data["id"]
        logger.info(f"✅ Tweet posted successfully! ID: {tweet_id}")
        logger.info(f"   View at: https://x.com/i/web/status/{tweet_id}")

        # Save to history after successful post
        history = _load_history()
        history.append(_get_tweet_hash(text))
        _save_history(history)

        return {
            "success": True,
            "tweet_id": tweet_id,
            "text": text,
            "url": f"https://x.com/i/web/status/{tweet_id}",
        }

    except tweepy.TweepyException as e:
        logger.error(f"❌ Error posting tweet: {e}")
        raise


def verify_credentials() -> dict:
    """
    Verify X API credentials by fetching authenticated user info.

    Returns:
        User info dict if successful
    """
    try:
        client = get_client()

        # Get authenticated user
        user = client.get_me()

        if user.data:
            logger.info(f"✅ Authenticated as: @{user.data.username}")
            return {"success": True, "username": user.data.username, "id": user.data.id}
        else:
            raise ValueError("Could not fetch user info")

    except Exception as e:
        logger.error(f"❌ Credential verification failed: {e}")
        raise


if __name__ == "__main__":
    # Test the X poster
    logging.basicConfig(level=logging.INFO)

    print("\n🔐 Verifying X API credentials...\n")
    try:
        user = verify_credentials()
        print(f"✅ Authenticated as @{user['username']}")

        # Test dry run
        print("\n📝 Testing dry run post...\n")
        result = post_tweet(
            "Test tweet from X Automation Bot! 🤖 #AI #Tech", dry_run=True
        )
        print(f"Dry run result: {result}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure your .env file has valid X API credentials!")
