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
TWEET_PROMPT = """You are a developer who's active on X (Twitter) and loves sharing interesting tech finds.

You just saw these trending discussions in the dev community:

{context}

Write ONE tweet that:
1. Sounds like a REAL person sharing something cool they found
2. References the actual discussion/topic (be specific, not vague)
3. Adds your own genuine take or question
4. Feels conversational, like texting a friend
5. Uses casual language (contractions, lowercase ok, emoji sparingly)
6. MUST be under 240 characters (leave room for hashtags)
7. Ends with 2-3 relevant hashtags like #AI #Tech #Coding #OpenSource #DevLife

STYLE EXAMPLES (mimic this vibe):
- "just saw devs arguing about tabs vs spaces again on HN... in 2026 lol 💀"
- "this new AI coding tool has 2k stars in a week?? ok I need to try it"
- "hot take: the best code is the code you don't write. fight me"
- "why are we still debating monorepos. just pick one and ship 😭"

DO NOT:
- Sound like a marketing bot
- Use formal language
- Start with "Exciting news!" or "Breaking:"
- Use more than 1-2 emojis
- Be generic
- Include ANY URLs or links (I'll add those myself)

Output ONLY the tweet text, nothing else:"""


COMMENT_TWEET_PROMPT = """You're a dev sharing a hot take about this trending discussion:

TOPIC: {topic}
FROM: {source}
CONTEXT: {context}

Write a SHORT, punchy tweet (under 250 chars) with your genuine reaction.
Sound like a real dev - casual, opinionated, maybe a bit sarcastic.
Include the topic reference so followers know what you're talking about.

Just the tweet text, no quotes:"""


def generate_tweet(trending_data: Dict) -> str:
    """
    Generate an authentic tweet based on trending dev discussions.

    Args:
        trending_data: Dict with hn_discussions, github_repos, news from fetch_all_trending()

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
    prompt = TWEET_PROMPT.format(context=context)

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


def generate_with_retry(trending_data: Dict, max_retries: int = 3) -> str:
    """
    Generate tweet with retry logic.

    Args:
        trending_data: Trending content dict
        max_retries: Maximum retry attempts

    Returns:
        Generated tweet text
    """
    for attempt in range(max_retries):
        try:
            tweet = generate_tweet(trending_data)
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
