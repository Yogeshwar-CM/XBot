"""
X Poster Module
Posts tweets to X (Twitter) using API v2 via Tweepy
"""

import logging
import tweepy

from config.settings import (
    X_API_KEY,
    X_API_SECRET,
    X_ACCESS_TOKEN,
    X_ACCESS_TOKEN_SECRET,
    DRY_RUN,
)

logger = logging.getLogger(__name__)


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

    if dry_run:
        logger.info(f"[DRY RUN] Would post tweet ({len(text)} chars):\n{text}")
        return {"dry_run": True, "text": text, "length": len(text)}

    try:
        client = get_client()

        response = client.create_tweet(text=text)

        tweet_id = response.data["id"]
        logger.info(f"✅ Tweet posted successfully! ID: {tweet_id}")
        logger.info(f"   View at: https://x.com/i/web/status/{tweet_id}")

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
