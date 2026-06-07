"""
hackernews_scraper.py - Fetches stories from the free Hacker News Algolia API.
No API key required.
"""

from datetime import datetime, timezone

from config.settings import MAX_ARTICLES_PER_SOURCE
from scraper.base_scraper import BaseScraper
from utils.models import Article


class HackerNewsScraper(BaseScraper):
    """Search HN stories via https://hn.algolia.com/api/v1/search"""

    BASE_URL = "https://hn.algolia.com/api/v1/search"

    def __init__(self) -> None:
        super().__init__("Hacker News")

    def fetch(self, keyword: str) -> list[Article]:
        params = {
            "query": keyword,
            "tags": "story",
            "hitsPerPage": MAX_ARTICLES_PER_SOURCE,
        }
        resp = self.get(self.BASE_URL, params=params)
        hits = resp.json().get("hits", [])

        articles: list[Article] = []
        for hit in hits:
            # Skip items without a proper URL (Ask HN, etc.)
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"

            pub = hit.get("created_at")
            published_at = None
            if pub:
                try:
                    published_at = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                except ValueError:
                    pass

            articles.append(
                Article(
                    title=hit.get("title", "").strip(),
                    url=url,
                    source=self.source_name,
                    summary=hit.get("story_text") or "",
                    author=hit.get("author", ""),
                    published_at=published_at,
                    keyword=keyword,
                    tags=["tech", "hacker-news"],
                )
            )

        return articles
