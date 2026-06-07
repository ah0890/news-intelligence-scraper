"""
settings.py - Central configuration for the News Intelligence Scraper.
All tunable parameters live here so nothing is buried in source files.
"""

import os

# ---------------------------------------------------------------------------
# Search & Scraping
# ---------------------------------------------------------------------------
DEFAULT_KEYWORDS: list[str] = ["artificial intelligence", "machine learning", "python"]

# How many articles to retrieve per keyword from each source
MAX_ARTICLES_PER_SOURCE: int = 10

# Request timeout in seconds
REQUEST_TIMEOUT: int = 15

# Polite delay between requests (seconds) — respect the servers
REQUEST_DELAY: float = 1.2

# User-Agent string sent with every request
USER_AGENT: str = (
    "Mozilla/5.0 (compatible; NewsResearchBot/1.0; "
    "+https://github.com/yourusername/news-intelligence-scraper)"
)

# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------
SOURCES: dict[str, dict] = {
    "hackernews": {
        "name": "Hacker News",
        "base_url": "https://hn.algolia.com/api/v1/search",
        "type": "api",
        "enabled": True,
    },
    "guardian": {
        "name": "The Guardian",
        "base_url": "https://content.guardianapis.com/search",
        "type": "api",
        "api_key_env": "GUARDIAN_API_KEY",   # set to "test" for free tier
        "enabled": False,  # requires real API key — get one free at open-platform.theguardian.com
    },
    "arxiv": {
        "name": "arXiv",
        "base_url": "http://export.arxiv.org/api/query",
        "type": "api",
        "enabled": True,
    },
    "bbc": {
        "name": "BBC News",
        "base_url": "https://www.bbc.co.uk/search",
        "type": "html",
        "enabled": True,
    },
}

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
REPORTS_DIR: str = os.path.join(OUTPUT_DIR, "reports")
RAW_DIR: str = os.path.join(OUTPUT_DIR, "raw")

# Export formats to generate automatically
DEFAULT_EXPORTS: list[str] = ["csv", "json", "excel", "html"]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL: str = "INFO"
LOG_FILE: str = os.path.join(OUTPUT_DIR, "scraper.log")
