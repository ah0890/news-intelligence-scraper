"""
models.py - Shared data models for the News Intelligence Scraper.
Using dataclasses keeps the code clean and IDE-friendly.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    """Represents a single scraped article or paper."""

    # Core identifiers
    title: str
    url: str
    source: str                         # e.g. "Hacker News", "The Guardian"

    # Content
    summary: str = ""
    author: str = ""
    published_at: Optional[datetime] = None

    # Metadata
    keyword: str = ""                   # which search keyword returned this
    relevance_score: float = 0.0        # 0–1 relevance estimate
    tags: list[str] = field(default_factory=list)
    scraped_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Serialise to a plain dict (for CSV / JSON export)."""
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "summary": self.summary[:400] if self.summary else "",
            "author": self.author,
            "published_at": (
                self.published_at.strftime("%Y-%m-%d %H:%M") if self.published_at else ""
            ),
            "keyword": self.keyword,
            "relevance_score": round(self.relevance_score, 3),
            "tags": ", ".join(self.tags),
            "scraped_at": self.scraped_at.strftime("%Y-%m-%d %H:%M"),
        }

    def __repr__(self) -> str:
        return f"<Article source={self.source!r} title={self.title[:60]!r}>"
