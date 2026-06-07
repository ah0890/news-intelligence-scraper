"""
base_scraper.py - Abstract base class that every scraper must extend.

Provides shared HTTP session management, retry logic, and rate limiting
so individual scrapers can focus purely on parsing.
"""

import time
from abc import ABC, abstractmethod

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import REQUEST_TIMEOUT, REQUEST_DELAY, USER_AGENT
from utils.logger import get_logger
from utils.models import Article


class BaseScraper(ABC):
    """Abstract scraper.  Sub-classes implement `fetch(keyword)` only."""

    def __init__(self, source_name: str) -> None:
        self.source_name = source_name
        self.logger = get_logger(f"scraper.{source_name.lower().replace(' ', '_')}")
        self.session = self._build_session()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self, keyword: str) -> list[Article]:
        """
        Entry point called by the orchestrator.
        Wraps `fetch` with timing, logging and error handling.
        """
        self.logger.info("Scraping '%s' from %s ...", keyword, self.source_name)
        start = time.time()
        try:
            articles = self.fetch(keyword)
            elapsed = time.time() - start
            self.logger.info(
                "  [ok] %d articles found in %.1fs", len(articles), elapsed
            )
            time.sleep(REQUEST_DELAY)   # polite delay between calls
            return articles
        except Exception as exc:
            self.logger.error("  [fail] Error scraping %s: %s", self.source_name, exc)
            return []

    # ------------------------------------------------------------------
    # Sub-class contract
    # ------------------------------------------------------------------

    @abstractmethod
    def fetch(self, keyword: str) -> list[Article]:
        """Fetch articles for *keyword* and return a list of Article objects."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get(self, url: str, **kwargs) -> requests.Response:
        """Convenience wrapper around session.get with default timeout."""
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response

    @staticmethod
    def _build_session() -> requests.Session:
        """Build a requests Session with automatic retries."""
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT})

        retry_strategy = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
