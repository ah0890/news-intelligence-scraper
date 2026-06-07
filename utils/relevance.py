"""
relevance.py - Lightweight keyword-relevance scorer.

Scores how relevant an article is to the original search keyword
without any external ML dependency — just TF-style counting + bonuses.
"""

import re
from utils.models import Article


def _tokenise(text: str) -> list[str]:
    """Lower-case and split text into word tokens."""
    return re.findall(r"[a-z0-9]+", text.lower())


def score_article(article: Article) -> float:
    """
    Return a relevance score in [0, 1] for an article against its keyword.

    Scoring rubric
    --------------
    - Keyword in title  → +0.40
    - Keyword in summary → +0.30 (scaled by density, max +0.30)
    - Summary length bonus → up to +0.20
    - Has author         → +0.05
    - Has publish date   → +0.05
    """
    if not article.keyword:
        return 0.5  # No keyword to compare against — neutral score

    keyword_tokens = _tokenise(article.keyword)
    title_tokens = _tokenise(article.title)
    summary_tokens = _tokenise(article.summary)

    score = 0.0

    # Title hit
    if all(kw in title_tokens for kw in keyword_tokens):
        score += 0.40
    elif any(kw in title_tokens for kw in keyword_tokens):
        score += 0.20

    # Summary density
    if summary_tokens:
        hits = sum(summary_tokens.count(kw) for kw in keyword_tokens)
        density = min(hits / len(summary_tokens), 0.05)   # cap at 5 % density
        score += density / 0.05 * 0.30

    # Summary length bonus (encourages more informative articles)
    summary_words = len(summary_tokens)
    if summary_words >= 100:
        score += 0.20
    elif summary_words >= 30:
        score += 0.10

    # Metadata completeness
    if article.author:
        score += 0.05
    if article.published_at:
        score += 0.05

    return round(min(score, 1.0), 3)


def enrich_articles(articles: list[Article]) -> list[Article]:
    """Score all articles in-place and sort by relevance descending."""
    for art in articles:
        art.relevance_score = score_article(art)
    return sorted(articles, key=lambda a: a.relevance_score, reverse=True)
