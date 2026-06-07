"""
bbc_scraper.py - Scrapes BBC News search results using BeautifulSoup.

Demonstrates HTML parsing — a complementary skill to API-based scrapers.
Respects BBC's robots.txt; only public search pages are accessed.
"""

from urllib.parse import urlencode, quote_plus

from bs4 import BeautifulSoup

from config.settings import MAX_ARTICLES_PER_SOURCE
from scraper.base_scraper import BaseScraper
from utils.models import Article


class BBCScraper(BaseScraper):
    """Scrape BBC News search results for a keyword."""

    BASE_URL = "https://www.bbc.co.uk/search"

    def __init__(self) -> None:
        super().__init__("BBC News")

    def fetch(self, keyword: str) -> list[Article]:
        params = {"q": keyword, "filter": "news"}
        resp = self.get(self.BASE_URL, params=params)

        soup = BeautifulSoup(resp.text, "html.parser")
        articles: list[Article] = []

        # BBC's search results live in <div data-testid="default-promo"> cards
        cards = soup.select("[data-testid='default-promo']")

        # Fallback selector for older BBC markup
        if not cards:
            cards = soup.select("li.ssrcss-1f3bvyz-StyledListItem, article")

        for card in cards[:MAX_ARTICLES_PER_SOURCE]:
            # Title
            title_el = card.select_one("h3, h2, [data-testid='card-headline']")
            title = title_el.get_text(strip=True) if title_el else ""

            # URL
            link_el = card.select_one("a[href]")
            href = link_el["href"] if link_el else ""
            if href and not href.startswith("http"):
                href = "https://www.bbc.co.uk" + href

            # Summary / description
            desc_el = card.select_one(
                "p, [data-testid='card-description'], .ssrcss-1q0x1qg-Paragraph"
            )
            summary = desc_el.get_text(strip=True) if desc_el else ""

            if not title or not href:
                continue   # skip incomplete cards

            articles.append(
                Article(
                    title=title,
                    url=href,
                    source=self.source_name,
                    summary=summary,
                    keyword=keyword,
                    tags=["news", "bbc"],
                )
            )

        if not articles:
            self.logger.warning(
                "BBC: No articles parsed — site structure may have changed."
            )

        return articles
