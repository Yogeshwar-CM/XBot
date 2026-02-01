"""
News Fetcher Module
Fetches trending AI/Development discussions from Hacker News, GitHub, and RSS feeds
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import re

from config.settings import RSS_FEEDS

logger = logging.getLogger(__name__)

# Hacker News Algolia API for trending discussions
HN_ALGOLIA_URL = "https://hn.algolia.com/api/v1/search"

# GitHub trending (via search API - no auth needed for basic search)
GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"


def fetch_hn_trending(min_points: int = 50, max_items: int = 5) -> List[Dict]:
    """
    Fetch trending AI/Dev discussions from Hacker News using Algolia API.
    These are REAL discussions devs are having right now.

    Args:
        min_points: Minimum upvotes to consider "trending"
        max_items: Max items to return

    Returns:
        List of trending HN discussions
    """
    discussions = []

    # Search for AI/ML/Dev related posts with good engagement
    queries = ["AI", "LLM", "programming", "developer", "coding"]

    for query in queries:
        try:
            params = {
                "query": query,
                "tags": "story",
                "numericFilters": f"points>{min_points}",
                "hitsPerPage": 5,
            }

            response = requests.get(HN_ALGOLIA_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for hit in data.get("hits", []):
                # Skip if already added
                if any(d["id"] == hit["objectID"] for d in discussions):
                    continue

                discussions.append(
                    {
                        "id": hit["objectID"],
                        "title": hit.get("title", ""),
                        "url": hit.get(
                            "url",
                            f"https://news.ycombinator.com/item?id={hit['objectID']}",
                        ),
                        "points": hit.get("points", 0),
                        "comments": hit.get("num_comments", 0),
                        "author": hit.get("author", ""),
                        "source": "Hacker News",
                        "category": "Dev Discussion",
                        "hn_link": f"https://news.ycombinator.com/item?id={hit['objectID']}",
                    }
                )

        except Exception as e:
            logger.warning(f"Error fetching HN for query '{query}': {e}")
            continue

    # Sort by points (most upvoted = most discussed)
    discussions.sort(key=lambda x: x["points"], reverse=True)
    logger.info(f"Found {len(discussions)} trending HN discussions")

    return discussions[:max_items]


def fetch_github_trending(max_items: int = 3) -> List[Dict]:
    """
    Fetch trending AI/Dev repositories from GitHub.

    Args:
        max_items: Max items to return

    Returns:
        List of trending repos
    """
    repos = []

    # Search for repos created in last 7 days with good stars
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    try:
        params = {
            "q": f"AI OR machine-learning OR LLM created:>{week_ago}",
            "sort": "stars",
            "order": "desc",
            "per_page": max_items,
        }

        response = requests.get(GITHUB_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        for repo in data.get("items", []):
            repos.append(
                {
                    "title": f"{repo['name']} - {repo.get('description', 'No description')[:100]}",
                    "url": repo["html_url"],
                    "stars": repo["stargazers_count"],
                    "language": repo.get("language", "Unknown"),
                    "source": "GitHub Trending",
                    "category": "Open Source",
                    "author": repo["owner"]["login"],
                }
            )

        logger.info(f"Found {len(repos)} trending GitHub repos")

    except Exception as e:
        logger.warning(f"Error fetching GitHub trending: {e}")

    return repos


def fetch_rss_news(max_age_hours: int = 24, max_items: int = 5) -> List[Dict]:
    """
    Fetch recent news from configured RSS feeds.

    Args:
        max_age_hours: Only include articles from the last N hours
        max_items: Maximum number of articles to return

    Returns:
        List of news items
    """
    all_news = []
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

    for feed_config in RSS_FEEDS:
        try:
            logger.info(f"Fetching from {feed_config['name']}...")
            feed = feedparser.parse(feed_config["url"])

            for entry in feed.entries[:5]:  # Limit per feed
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])

                if published and published < cutoff_time:
                    continue

                summary = ""
                if hasattr(entry, "summary"):
                    summary = entry.summary[:200]
                elif hasattr(entry, "description"):
                    summary = entry.description[:200]

                summary = re.sub(r"<[^>]+>", "", summary).strip()

                news_item = {
                    "title": entry.title,
                    "summary": summary,
                    "link": entry.link,
                    "source": feed_config["name"],
                    "category": feed_config["category"],
                    "published": published.isoformat() if published else None,
                }
                all_news.append(news_item)

        except Exception as e:
            logger.error(f"Error fetching from {feed_config['name']}: {e}")
            continue

    all_news.sort(key=lambda x: x["published"] or "", reverse=True)
    return all_news[:max_items]


def fetch_all_trending(max_items: int = 10) -> Dict:
    """
    Fetch ALL trending content: HN discussions, GitHub repos, and RSS news.
    Returns structured data for better tweet generation.

    Returns:
        Dict with categorized trending content
    """
    logger.info("🔥 Fetching trending dev discussions...")

    hn_discussions = fetch_hn_trending(min_points=30, max_items=5)
    github_repos = fetch_github_trending(max_items=3)
    rss_news = fetch_rss_news(max_items=5)

    return {
        "hn_discussions": hn_discussions,
        "github_repos": github_repos,
        "news": rss_news,
        "top_discussion": hn_discussions[0] if hn_discussions else None,
        "top_repo": github_repos[0] if github_repos else None,
    }


def get_headlines(news_items: List[Dict]) -> List[str]:
    """Extract just the headlines from news items."""
    return [item["title"] for item in news_items]


if __name__ == "__main__":
    # Test the news fetcher
    logging.basicConfig(level=logging.INFO)

    print("\n🔥 TRENDING DEV DISCUSSIONS\n")

    trending = fetch_all_trending()

    print("📢 Hacker News Hot Topics:")
    for d in trending["hn_discussions"]:
        print(f"  • {d['title'][:60]}... ({d['points']} pts, {d['comments']} comments)")

    print("\n⭐ GitHub Trending Repos:")
    for r in trending["github_repos"]:
        print(f"  • {r['title'][:60]}... ({r['stars']} stars)")

    print("\n📰 Latest News:")
    for n in trending["news"][:3]:
        print(f"  • {n['title'][:60]}...")
