"""
orchestrator.py - Coordinates all scrapers and returns a unified article list.

Uses ThreadPoolExecutor so multiple sources run concurrently — much faster
than sequential scraping.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from config.settings import SOURCES
from scraper.hackernews_scraper import HackerNewsScraper
from scraper.guardian_scraper import GuardianScraper
from scraper.arxiv_scraper import ArxivScraper
from scraper.bbc_scraper import BBCScraper
from utils.logger import get_logger
from utils.models import Article
from utils.relevance import enrich_articles

logger = get_logger("orchestrator")

# Registry — add new scrapers here without touching anything else
SCRAPER_REGISTRY: dict[str, Callable] = {
    "hackernews": HackerNewsScraper,
    "guardian": GuardianScraper,
    "arxiv": ArxivScraper,
    "bbc": BBCScraper,
}


def _enabled_scrapers() -> list:
    """Instantiate only the scrapers whose source is marked enabled."""
    scrapers = []
    for key, cls in SCRAPER_REGISTRY.items():
        if SOURCES.get(key, {}).get("enabled", True):
            try:
                scrapers.append(cls())
            except Exception as exc:
                logger.warning("Could not initialise scraper '%s': %s", key, exc)
    return scrapers


def run(
    keywords: list[str],
    max_workers: int = 4,
    deduplicate: bool = True,
) -> list[Article]:
    """
    Run all enabled scrapers for every keyword concurrently.

    Parameters
    ----------
    keywords    : list of search terms
    max_workers : thread-pool size (default 4)
    deduplicate : remove articles with identical URLs

    Returns
    -------
    Sorted list of Article objects, most relevant first.
    """
    scrapers = _enabled_scrapers()
    logger.info(
        "Starting scrape — %d keyword(s) × %d source(s)", len(keywords), len(scrapers)
    )

    all_articles: list[Article] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(scraper.scrape, kw): (scraper.source_name, kw)
            for scraper in scrapers
            for kw in keywords
        }
        for future in as_completed(futures):
            source, kw = futures[future]
            try:
                results = future.result()
                all_articles.extend(results)
                logger.debug("  %s / '%s' -> %d articles", source, kw, len(results))
            except Exception as exc:
                logger.error("Future failed (%s / '%s'): %s", source, kw, exc)

    if deduplicate:
        seen: set[str] = set()
        unique: list[Article] = []
        for art in all_articles:
            if art.url not in seen:
                seen.add(art.url)
                unique.append(art)
        logger.info("De-duplicated: %d -> %d articles", len(all_articles), len(unique))
        all_articles = unique

    all_articles = enrich_articles(all_articles)
    logger.info("Total articles collected: %d", len(all_articles))
    return all_articles
