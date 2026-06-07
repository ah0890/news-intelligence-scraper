"""
test_scraper.py - Unit tests for core modules.

Run with:  pytest tests/ -v
"""

import sys
from pathlib import Path
from datetime import datetime

# Make sure the project root is importable
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from utils.models import Article
from utils.relevance import score_article, enrich_articles


# ---------------------------------------------------------------------------
# Article model tests
# ---------------------------------------------------------------------------

class TestArticleModel:
    def _make(self, **kwargs) -> Article:
        defaults = dict(
            title="Test Title",
            url="https://example.com",
            source="TestSource",
            keyword="python",
        )
        defaults.update(kwargs)
        return Article(**defaults)

    def test_to_dict_keys(self):
        art = self._make()
        d = art.to_dict()
        for key in ("title", "url", "source", "summary", "author",
                    "published_at", "keyword", "relevance_score", "tags", "scraped_at"):
            assert key in d, f"Missing key: {key}"

    def test_summary_truncated_at_400(self):
        long_summary = "word " * 200     # 1000 chars
        art = self._make(summary=long_summary)
        assert len(art.to_dict()["summary"]) <= 400

    def test_tags_joined_as_string(self):
        art = self._make(tags=["ai", "ml", "python"])
        assert art.to_dict()["tags"] == "ai, ml, python"

    def test_published_at_formatted(self):
        art = self._make(published_at=datetime(2024, 6, 15, 12, 0))
        assert art.to_dict()["published_at"] == "2024-06-15 12:00"

    def test_repr(self):
        art = self._make(title="Hello World")
        assert "Hello World" in repr(art)


# ---------------------------------------------------------------------------
# Relevance scoring tests
# ---------------------------------------------------------------------------

class TestRelevanceScoring:
    def _art(self, title="", summary="", keyword="python", **kwargs) -> Article:
        return Article(
            title=title, url="https://x.com", source="Test",
            summary=summary, keyword=keyword, **kwargs
        )

    def test_score_in_range(self):
        art = self._art(title="Python programming tutorial", summary="Learn python today.")
        score = score_article(art)
        assert 0.0 <= score <= 1.0

    def test_title_hit_raises_score(self):
        art_hit = self._art(title="Python web scraping guide", keyword="python")
        art_miss = self._art(title="Java enterprise patterns",  keyword="python")
        assert score_article(art_hit) > score_article(art_miss)

    def test_longer_summary_bonus(self):
        art_short = self._art(title="Python news", summary="Python is great.", keyword="python")
        art_long  = self._art(
            title="Python news",
            summary=("Python is great. " * 30),   # long summary
            keyword="python",
        )
        assert score_article(art_long) >= score_article(art_short)

    def test_metadata_bonus(self):
        base = dict(title="Python tutorial", keyword="python")
        no_meta = self._art(**base)
        with_meta = self._art(**base, author="Alice", published_at=datetime.now())
        assert score_article(with_meta) > score_article(no_meta)

    def test_enrich_sorted_descending(self):
        arts = [
            self._art(title="Java tutorial", keyword="python"),
            self._art(title="Python data science", summary="Python is used widely.", keyword="python"),
            self._art(title="Rust systems programming", keyword="python"),
        ]
        enriched = enrich_articles(arts)
        scores = [a.relevance_score for a in enriched]
        assert scores == sorted(scores, reverse=True)

    def test_no_keyword_neutral(self):
        art = Article(title="Something", url="https://x.com", source="S", keyword="")
        score = score_article(art)
        assert score == 0.5


# ---------------------------------------------------------------------------
# Orchestrator import smoke test
# ---------------------------------------------------------------------------

class TestOrchestratorImport:
    def test_imports_without_error(self):
        from scraper.orchestrator import SCRAPER_REGISTRY
        assert len(SCRAPER_REGISTRY) >= 1

    def test_all_scrapers_instantiate(self):
        from scraper.orchestrator import _enabled_scrapers
        scrapers = _enabled_scrapers()
        assert len(scrapers) >= 1
        for s in scrapers:
            assert hasattr(s, "scrape")
