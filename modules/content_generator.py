"""
Content Generator Module
Uses Groq AI to generate authentic, conversational tweets based on trending dev discussions
"""

import logging
from typing import Dict
from groq import Groq

from config.settings import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)

# Authentic tweet generation - sounds like a real dev, not a bot

TWEET_PROMPT = """You are a senior developer who has seen it all. You are tired of the hype cycle.
You are posting on X (Twitter).

CONTEXT (What's trending):
{context}

YOUR RECENT POSTS (Don't repeat these):
{recent_posts_context}

TASK:
Write ONE tweet about something from the context.

PERSONA RULES:
1. Speak in lowercase. It's more authentic.
2. Be skeptical but open-minded. Prefer "huh, interesting" over "wow amazing".
3. NO corporate buzzwords (unleash, revolutionize, game-changer).
4. NO "Exciting news!" start.
5. Max 1 emoji (or 0). 💀 and 😭 are okay. 🚀 is BANNED.
6. Don't frame it as a news update. Frame it as "i just saw this and..."
7. Allow fragments. Imperfect grammar is real.

BAD EXAMPLES (Bot behavior):
- "Check out this amazing new AI tool! #AI #Tech" (Too eager)
- "The future of coding is here with GPT-5." (Too formal)
- "Exciting development in the world of Python!" (Marketing bot)

GOOD EXAMPLES (Human behavior):
- "wait, did openai just actually fix the reasoning bug? big if true"
- "everyone arguing about monorepos again. nature is healing."
- "tried the new cursor update. honestly? not bad."
- "i give this new framework 6 months before google kills it"

Output ONLY the tweet text. No quotes."""


COMMENT_TWEET_PROMPT = """You're a dev reading this trending news:

TOPIC: {topic}
FROM: {source}
CONTEXT: {context}

Write a quick, opinionated reaction tweet.
1. Be cynical, funny, or impressed. Just pick ONE vibe.
2. 280 chars max (but shorter is better, like < 140).
3. No boomer energy. No corporate speak.
4. lowercase looks more real.
5. If it's about AI, be skeptical or mind-blown.
6. If it's about a JS framework, be exhausted.

Examples:
- "obsidian really is just markdown files and good vibes huh"
- "copilot just wrote my entire unit test suite. i might actually cry."
- "another js framework? daring today aren't we"

Output JUST the tweet text:"""


def generate_tweet(trending_data: Dict, recent_posts: list = None) -> str:
    """
    Generate an authentic tweet based on trending dev discussions.

    Args:
        trending_data: Dict with hn_discussions, github_repos, news from fetch_all_trending()
        recent_posts: Optional list of recently posted tweets for context

    Returns:
        Generated tweet text (under 280 characters)
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured")

    # Build context from trending data
    context_parts = []

    # Add HN discussions (most important - real dev conversations)
    hn = trending_data.get("hn_discussions", [])
    if hn:
        context_parts.append("🔥 HOT ON HACKER NEWS:")
        for d in hn[:3]:
            context_parts.append(
                f'  • "{d["title"]}" ({d["points"]} upvotes, {d["comments"]} comments)'
            )

    # Add GitHub trending
    gh = trending_data.get("github_repos", [])
    if gh:
        context_parts.append("\n⭐ TRENDING ON GITHUB:")
        for r in gh[:2]:
            context_parts.append(f"  • {r['title']} ({r['stars']} stars)")

    # Add news
    news = trending_data.get("news", [])
    if news:
        context_parts.append("\n📰 LATEST NEWS:")
        for n in news[:2]:
            context_parts.append(f"  • {n['title']}")

    if not context_parts:
        context_parts = ["AI and coding tools continue to evolve rapidly"]

    context = "\n".join(context_parts)

    # Build recent posts context
    recent_posts_context = ""
    if recent_posts:
        recent_posts_context = (
            "YOUR RECENT POSTS (avoid repeating these topics/angles):\n"
        )
        for i, post in enumerate(recent_posts[:10], 1):
            recent_posts_context += f"  {i}. {post}\n"

    prompt = TWEET_PROMPT.format(
        context=context, recent_posts_context=recent_posts_context
    )

    try:
        client = Groq(api_key=GROQ_API_KEY)

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a tech-savvy developer who shares interesting finds on X. You sound authentic, not corporate. Short, punchy tweets.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,
            temperature=0.9,  # More creative/varied
        )

        tweet = response.choices[0].message.content.strip()
        tweet = tweet.strip('"').strip("'")

        # Ensure under 280 chars
        if len(tweet) > 280:
            tweet = tweet[:277].rsplit(" ", 1)[0] + "..."

        logger.info(f"Generated tweet ({len(tweet)} chars): {tweet}")
        return tweet

    except Exception as e:
        logger.error(f"Error generating tweet: {e}")
        raise


def generate_discussion_tweet(discussion: Dict) -> str:
    """
    Generate a tweet commenting on a specific trending discussion.
    More focused than general tweet.

    Args:
        discussion: Single HN discussion or GitHub repo dict

    Returns:
        Generated tweet
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured")

    topic = discussion.get("title", "")
    source = discussion.get("source", "dev community")

    # Build context
    context_parts = []
    if "points" in discussion:
        context_parts.append(
            f"{discussion['points']} upvotes, {discussion.get('comments', 0)} comments"
        )
    if "stars" in discussion:
        context_parts.append(f"{discussion['stars']} GitHub stars")

    context = ", ".join(context_parts) if context_parts else "trending now"

    prompt = COMMENT_TWEET_PROMPT.format(topic=topic, source=source, context=context)

    try:
        client = Groq(api_key=GROQ_API_KEY)

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You're a developer commenting on tech trends. Be authentic and opinionated.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=80,
            temperature=0.9,
        )

        tweet = response.choices[0].message.content.strip()
        tweet = tweet.strip('"').strip("'")

        if len(tweet) > 280:
            tweet = tweet[:277].rsplit(" ", 1)[0] + "..."

        return tweet

    except Exception as e:
        logger.error(f"Error generating discussion tweet: {e}")
        raise


def generate_with_retry(
    trending_data: Dict, recent_posts: list = None, max_retries: int = 3
) -> str:
    """
    Generate tweet with retry logic.

    Args:
        trending_data: Trending content dict
        recent_posts: Optional list of recent posts for context
        max_retries: Maximum retry attempts

    Returns:
        Generated tweet text
    """
    for attempt in range(max_retries):
        try:
            tweet = generate_tweet(trending_data, recent_posts)
            if tweet and len(tweet) <= 280:
                return tweet
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise

    raise RuntimeError("Failed to generate valid tweet after retries")


if __name__ == "__main__":
    # Test the content generator
    logging.basicConfig(level=logging.INFO)

    # Mock trending data for testing
    test_data = {
        "hn_discussions": [
            {
                "title": "Show HN: I built an AI that writes code better than me",
                "points": 342,
                "comments": 156,
                "source": "Hacker News",
            },
            {
                "title": "Why I'm mass quitting AI tools after a year",
                "points": 234,
                "comments": 89,
                "source": "Hacker News",
            },
        ],
        "github_repos": [
            {
                "title": "cursor-ai-clone - Open source AI coding assistant",
                "stars": 1200,
                "source": "GitHub Trending",
            }
        ],
        "news": [
            {"title": "OpenAI releases GPT-5 with revolutionary reasoning capabilities"}
        ],
    }

    print("\n🤖 Generating authentic tweet...\n")
    tweet = generate_tweet(test_data)
    print(f"📝 Tweet ({len(tweet)} chars):\n{tweet}")
