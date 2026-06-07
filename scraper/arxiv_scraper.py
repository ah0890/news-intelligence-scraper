"""
arxiv_scraper.py - Fetches research papers from arXiv's free Atom API.
No API key needed.  Docs: https://arxiv.org/help/api/
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote_plus

from config.settings import MAX_ARTICLES_PER_SOURCE
from scraper.base_scraper import BaseScraper
from utils.models import Article

_NS = "http://www.w3.org/2005/Atom"   # Atom namespace


def _text(element, tag: str) -> str:
    """Safely pull inner text from an XML element."""
    child = element.find(f"{{{_NS}}}{tag}")
    return child.text.strip() if child is not None and child.text else ""


class ArxivScraper(BaseScraper):
    """Search academic papers on arXiv via their public Atom feed."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self) -> None:
        super().__init__("arXiv")

    def fetch(self, keyword: str) -> list[Article]:
        params = {
            "search_query": f"all:{quote_plus(keyword)}",
            "start": 0,
            "max_results": MAX_ARTICLES_PER_SOURCE,
            "sortBy": "relevance",
        }
        resp = self.get(self.BASE_URL, params=params)
        root = ET.fromstring(resp.content)

        articles: list[Article] = []
        for entry in root.findall(f"{{{_NS}}}entry"):
            title = _text(entry, "title").replace("\n", " ")
            summary = _text(entry, "summary").replace("\n", " ")
            url = _text(entry, "id")

            # Authors
            authors = [
                a.find(f"{{{_NS}}}name").text.strip()   # type: ignore[union-attr]
                for a in entry.findall(f"{{{_NS}}}author")
                if a.find(f"{{{_NS}}}name") is not None
            ]

            # Published date
            pub_raw = _text(entry, "published")
            published_at = None
            if pub_raw:
                try:
                    published_at = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
                except ValueError:
                    pass

            # Categories → tags
            categories = [
                c.attrib.get("term", "")
                for c in entry.findall(
                    f"{{{_NS}}}category"
                    if False else
                    ".//{http://arxiv.org/schemas/atom}primary_category"
                )
            ]
            # Simpler fallback
            cats_plain = [
                c.attrib.get("term", "")
                for c in entry.findall("{http://www.w3.org/2005/Atom}category")
            ]

            articles.append(
                Article(
                    title=title,
                    url=url,
                    source=self.source_name,
                    summary=summary,
                    author=", ".join(authors[:3]),   # first three authors
                    published_at=published_at,
                    keyword=keyword,
                    tags=cats_plain[:3],
                )
            )

        return articles
