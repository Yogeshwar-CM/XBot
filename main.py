#!/usr/bin/env python3
"""
X Automation Bot - Main Entry Point
Generates and posts AI/Development content to X daily at 7PM IST
"""

import argparse
import logging
import signal
import sys
from datetime import datetime

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import TIMEZONE, POST_HOUR, POST_MINUTE, DRY_RUN, validate_config
from modules.news_fetcher import fetch_all_trending
from modules.content_generator import generate_with_retry
from modules.x_poster import post_tweet, verify_credentials
from modules.cache_manager import is_duplicate, add_to_cache, get_recent_posts

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


def run_bot():
    """
    Main bot execution: Fetch trending → Generate tweet → Post to X
    """
    logger.info("=" * 50)
    logger.info("🤖 X Automation Bot - Starting run")
    logger.info("=" * 50)

    try:
        # Step 1: Fetch trending discussions
        logger.info("🔥 Step 1: Fetching trending dev discussions...")
        trending = fetch_all_trending()

        hn_count = len(trending.get("hn_discussions", []))
        gh_count = len(trending.get("github_repos", []))
        news_count = len(trending.get("news", []))

        logger.info(
            f"   Found: {hn_count} HN discussions, {gh_count} GitHub repos, {news_count} news"
        )

        # Log top discussions
        for d in trending.get("hn_discussions", [])[:3]:
            logger.info(f"   📢 HN: {d['title'][:50]}... ({d['points']} pts)")
        for r in trending.get("github_repos", [])[:2]:
            logger.info(f"   ⭐ GH: {r['title'][:50]}... ({r['stars']} stars)")

        # Step 2: Generate authentic tweet (with retry if duplicate)
        logger.info("\n🤖 Step 2: Generating tweet with AI...")

        # Get recent posts for context
        recent_posts = get_recent_posts(limit=10)
        logger.info(
            f"   Context: Using last {len(recent_posts)} posts to avoid repetition"
        )

        max_attempts = 5
        tweet = None

        for attempt in range(max_attempts):
            tweet = generate_with_retry(trending, recent_posts=recent_posts)
            logger.info(f"   Generated ({len(tweet)} chars): {tweet}")

            # Check if duplicate
            if is_duplicate(tweet):
                logger.warning(
                    f"   ⚠️ Duplicate detected (attempt {attempt + 1}/{max_attempts}), regenerating..."
                )
                continue
            else:
                logger.info("   ✅ Unique content, proceeding to post")
                break

        if tweet is None or is_duplicate(tweet):
            raise RuntimeError("Failed to generate unique content after all attempts")

        # Step 3: Post to X
        logger.info("\n📤 Step 3: Posting to X...")
        result = post_tweet(tweet)

        # Step 4: Save to cache if successful
        if not result.get("dry_run"):
            tweet_id = result.get("tweet_id")
            add_to_cache(tweet, tweet_id)
            logger.info("   💾 Saved to cache")

        if result.get("dry_run"):
            logger.info("   [DRY RUN] Tweet was not actually posted")
        else:
            logger.info(f"   ✅ Posted! View at: {result.get('url')}")

        logger.info("\n" + "=" * 50)
        logger.info("✅ Bot run completed successfully!")
        logger.info("=" * 50)

        return result

    except Exception as e:
        logger.error(f"❌ Bot run failed: {e}")
        raise


def start_scheduler():
    """
    Start the APScheduler to run the bot daily at configured time.
    """
    # Validate configuration
    errors = validate_config()
    if errors:
        logger.error("Configuration errors:")
        for error in errors:
            logger.error(f"  • {error}")
        sys.exit(1)

    # Verify X credentials
    logger.info("🔐 Verifying X API credentials...")
    try:
        user = verify_credentials()
        logger.info(f"   Authenticated as @{user['username']}")
    except Exception as e:
        logger.error(f"Failed to verify credentials: {e}")
        sys.exit(1)

    # Setup scheduler
    tz = pytz.timezone(TIMEZONE)
    scheduler = BlockingScheduler(timezone=tz)

    # Add jobs for 9:00 AM and 7:34 PM
    trigger_morning = CronTrigger(hour=9, minute=0, timezone=tz)
    trigger_evening = CronTrigger(hour=19, minute=34, timezone=tz)

    scheduler.add_job(run_bot, trigger_morning, id="daily_post_morning")
    scheduler.add_job(run_bot, trigger_evening, id="daily_post_evening")

    # Log configuration
    now = datetime.now(tz)
    logger.info("\n📅 Scheduler configured:")
    logger.info(f"   Timezone: {TIMEZONE}")
    logger.info(f"   Post times: 09:00, 19:34")
    logger.info(f"   Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    # Print next runs
    for job in scheduler.get_jobs():
        logger.info(
            f"   Next run ({job.id}): {job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )

    logger.info(f"   Dry run mode: {DRY_RUN}")

    # Graceful shutdown
    def shutdown(signum, frame):
        logger.info("\n👋 Shutting down scheduler...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    logger.info("\n🚀 Scheduler started! Press Ctrl+C to stop.\n")
    scheduler.start()


def main():
    """
    Main entry point with argument parsing.
    """
    parser = argparse.ArgumentParser(
        description="X Automation Bot - AI/Dev content poster",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py          # Start scheduler (runs at 7PM daily)
  python main.py --now    # Run once immediately
  python main.py --verify # Verify credentials only
        """,
    )
    parser.add_argument(
        "--now",
        action="store_true",
        help="Run the bot once immediately instead of scheduling",
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verify credentials and exit"
    )

    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════╗
║           🤖 X Automation Bot                         ║
║           AI/Development Content Poster               ║
╚═══════════════════════════════════════════════════════╝
    """)

    if args.verify:
        # Just verify credentials
        errors = validate_config()
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"   • {error}")
            sys.exit(1)

        try:
            user = verify_credentials()
            print(f"✅ Authenticated as @{user['username']}")
        except Exception as e:
            print(f"❌ Credential verification failed: {e}")
            sys.exit(1)

    elif args.now:
        # Run once immediately
        errors = validate_config()
        if errors:
            logger.error("Configuration errors:")
            for error in errors:
                logger.error(f"  • {error}")
            sys.exit(1)

        run_bot()
    else:
        # Start scheduler
        start_scheduler()


if __name__ == "__main__":
    main()
