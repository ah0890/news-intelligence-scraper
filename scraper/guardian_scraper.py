"""
guardian_scraper.py - Fetches articles from The Guardian's open API.

Free tier key: set GUARDIAN_API_KEY=test in your .env file or shell.
Register for a free key at https://open-platform.theguardian.com/
"""

import os
from datetime import datetime

from config.settings import MAX_ARTICLES_PER_SOURCE
from scraper.base_scraper import BaseScraper
from utils.models import Article


class GuardianScraper(BaseScraper):
    """Search The Guardian via https://open-platform.theguardian.com/"""

    BASE_URL = "https://content.guardianapis.com/search"

    def __init__(self) -> None:
        super().__init__("The Guardian")
        # Falls back to the public "test" key (lower rate limits)
        self.api_key = os.getenv("GUARDIAN_API_KEY", "test")

    def fetch(self, keyword: str) -> list[Article]:
        params = {
            "q": keyword,
            "api-key": self.api_key,
            "show-fields": "trailText,byline,wordcount",
            "page-size": MAX_ARTICLES_PER_SOURCE,
            "order-by": "relevance",
        }
        resp = self.get(self.BASE_URL, params=params)
        results = resp.json().get("response", {}).get("results", [])

        articles: list[Article] = []
        for item in results:
            fields = item.get("fields", {})

            pub = item.get("webPublicationDate")
            published_at = None
            if pub:
                try:
                    published_at = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                except ValueError:
                    pass

            section = item.get("sectionName", "")
            articles.append(
                Article(
                    title=item.get("webTitle", "").strip(),
                    url=item.get("webUrl", ""),
                    source=self.source_name,
                    summary=fields.get("trailText", ""),
                    author=fields.get("byline", ""),
                    published_at=published_at,
                    keyword=keyword,
                    tags=[section.lower()] if section else [],
                )
            )

        return articles
