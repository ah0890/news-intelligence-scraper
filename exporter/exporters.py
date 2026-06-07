"""
exporters.py - Export scraped articles to CSV, JSON, Excel, and HTML.

Each function is self-contained so users can call only what they need.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from config.settings import REPORTS_DIR, RAW_DIR
from utils.logger import get_logger
from utils.models import Article

logger = get_logger("exporter")


def _ensure_dirs() -> None:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _to_dataframe(articles: list[Article]) -> pd.DataFrame:
    return pd.DataFrame([a.to_dict() for a in articles])


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def export_csv(articles: list[Article], filename: str | None = None) -> str:
    _ensure_dirs()
    filename = filename or f"articles_{_timestamp()}.csv"
    path = os.path.join(RAW_DIR, filename)
    df = _to_dataframe(articles)
    df.to_csv(path, index=False, encoding="utf-8-sig")   # utf-8-sig for Excel compat
    logger.info("CSV saved -> %s (%d rows)", path, len(df))
    return path


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------

def export_json(articles: list[Article], filename: str | None = None) -> str:
    _ensure_dirs()
    filename = filename or f"articles_{_timestamp()}.json"
    path = os.path.join(RAW_DIR, filename)
    data = [a.to_dict() for a in articles]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    logger.info("JSON saved -> %s (%d records)", path, len(data))
    return path


# ---------------------------------------------------------------------------
# Excel (multi-sheet workbook)
# ---------------------------------------------------------------------------

def export_excel(articles: list[Article], filename: str | None = None) -> str:
    _ensure_dirs()
    filename = filename or f"articles_{_timestamp()}.xlsx"
    path = os.path.join(RAW_DIR, filename)

    df = _to_dataframe(articles)

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        # Sheet 1 — all articles
        df.to_excel(writer, sheet_name="All Articles", index=False)

        # Sheet 2 — per-source summary
        summary = (
            df.groupby("source")
            .agg(count=("title", "count"), avg_relevance=("relevance_score", "mean"))
            .reset_index()
        )
        summary.to_excel(writer, sheet_name="Summary by Source", index=False)

        # Sheet 3 — top 20 by relevance
        top20 = df.nlargest(20, "relevance_score")
        top20.to_excel(writer, sheet_name="Top 20 Articles", index=False)

        # Auto-fit column widths (best-effort)
        for sheet in writer.sheets.values():
            for col in sheet.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                sheet.column_dimensions[col[0].column_letter].width = min(max_len + 2, 60)

    logger.info("Excel saved -> %s", path)
    return path


# ---------------------------------------------------------------------------
# HTML Report
# ---------------------------------------------------------------------------

def export_html(
    articles: list[Article],
    keywords: list[str],
    filename: str | None = None,
) -> str:
    _ensure_dirs()
    filename = filename or f"report_{_timestamp()}.html"
    path = os.path.join(REPORTS_DIR, filename)

    df = _to_dataframe(articles)
    source_counts = df["source"].value_counts().to_dict()
    kw_counts = df["keyword"].value_counts().to_dict()
    top_articles = articles[:10]

    # Build source badge HTML
    source_badges = "".join(
        f'<span class="badge">{src} <strong>{cnt}</strong></span>'
        for src, cnt in source_counts.items()
    )

    # Build keyword tag HTML
    kw_tags = "".join(
        f'<span class="kw-tag">{kw} ({cnt})</span>'
        for kw, cnt in kw_counts.items()
    )

    # Build article cards
    cards_html = ""
    for art in top_articles:
        score_pct = int(art.relevance_score * 100)
        score_color = "#22c55e" if score_pct >= 70 else "#f59e0b" if score_pct >= 40 else "#ef4444"
        pub = art.published_at.strftime("%d %b %Y") if art.published_at else "Unknown date"
        tags_html = "".join(f'<span class="tag">{t}</span>' for t in art.tags[:3])
        summary_short = (art.summary[:200] + "...") if len(art.summary) > 200 else art.summary

        cards_html += f"""
        <div class="card">
          <div class="card-header">
            <span class="source-label">{art.source}</span>
            <span class="score" style="color:{score_color}">{score_pct}% relevant</span>
          </div>
          <h3><a href="{art.url}" target="_blank" rel="noopener">{art.title}</a></h3>
          <p class="meta">
            {f'By {art.author} · ' if art.author else ''}{pub}
            {f' · keyword: <em>{art.keyword}</em>' if art.keyword else ''}
          </p>
          <p class="summary">{summary_short}</p>
          <div class="tags">{tags_html}</div>
          <div class="relevance-bar">
            <div class="relevance-fill" style="width:{score_pct}%; background:{score_color}"></div>
          </div>
        </div>
        """

    # Full table rows
    rows_html = ""
    for art in articles:
        pub = art.published_at.strftime("%d %b %Y") if art.published_at else ""
        rows_html += f"""
        <tr>
          <td><a href="{art.url}" target="_blank">{art.title[:80]}</a></td>
          <td>{art.source}</td>
          <td>{art.keyword}</td>
          <td>{pub}</td>
          <td>{art.author[:40]}</td>
          <td>{int(art.relevance_score * 100)}%</td>
        </tr>"""

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>News Intelligence Report</title>
  <style>
    :root {{
      --bg: #0f172a; --surface: #1e293b; --surface2: #334155;
      --accent: #38bdf8; --accent2: #818cf8; --text: #f1f5f9;
      --muted: #94a3b8; --border: #334155;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; padding: 2rem; }}
    header {{ border-bottom: 1px solid var(--border); padding-bottom: 1.5rem; margin-bottom: 2rem; }}
    header h1 {{ font-size: 2rem; background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    header p {{ color: var(--muted); margin-top: .4rem; }}
    .stats {{ display: flex; gap: 1.5rem; flex-wrap: wrap; margin: 1.5rem 0; }}
    .stat-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1rem 1.5rem; min-width: 140px; }}
    .stat-box .num {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
    .stat-box .label {{ color: var(--muted); font-size: .85rem; margin-top: .2rem; }}
    .badge {{ display: inline-block; background: var(--surface2); border-radius: 999px; padding: .25rem .75rem; font-size: .8rem; margin: .2rem; }}
    .kw-tag {{ display: inline-block; background: #1e3a5f; color: var(--accent); border-radius: 6px; padding: .2rem .6rem; font-size: .8rem; margin: .2rem; }}
    h2 {{ font-size: 1.3rem; margin: 2rem 0 1rem; color: var(--accent2); }}
    .cards-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1.2rem; }}
    .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.2rem; transition: border-color .2s; }}
    .card:hover {{ border-color: var(--accent); }}
    .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: .6rem; }}
    .source-label {{ font-size: .75rem; background: var(--surface2); padding: .15rem .5rem; border-radius: 4px; color: var(--muted); }}
    .score {{ font-size: .8rem; font-weight: 600; }}
    .card h3 {{ font-size: .95rem; margin-bottom: .4rem; line-height: 1.4; }}
    .card h3 a {{ color: var(--text); text-decoration: none; }}
    .card h3 a:hover {{ color: var(--accent); }}
    .meta {{ font-size: .78rem; color: var(--muted); margin-bottom: .5rem; }}
    .summary {{ font-size: .83rem; color: #cbd5e1; line-height: 1.5; margin-bottom: .6rem; }}
    .tags {{ display: flex; flex-wrap: wrap; gap: .3rem; margin-bottom: .7rem; }}
    .tag {{ font-size: .7rem; background: #1e3a5f; color: var(--accent); padding: .1rem .45rem; border-radius: 4px; }}
    .relevance-bar {{ height: 4px; background: var(--surface2); border-radius: 2px; overflow: hidden; }}
    .relevance-fill {{ height: 100%; border-radius: 2px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .83rem; margin-top: .5rem; }}
    th {{ background: var(--surface2); color: var(--muted); padding: .6rem .8rem; text-align: left; position: sticky; top: 0; }}
    td {{ padding: .55rem .8rem; border-bottom: 1px solid var(--border); }}
    td a {{ color: var(--accent); text-decoration: none; }}
    td a:hover {{ text-decoration: underline; }}
    .table-wrap {{ overflow-x: auto; background: var(--surface); border-radius: 12px; border: 1px solid var(--border); }}
    footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border); color: var(--muted); font-size: .8rem; text-align: center; }}
  </style>
</head>
<body>
  <header>
    <h1>📰 News Intelligence Report</h1>
    <p>Generated {generated_at} &nbsp;·&nbsp; Keywords: {', '.join(keywords)}</p>
  </header>

  <div class="stats">
    <div class="stat-box"><div class="num">{len(articles)}</div><div class="label">Total Articles</div></div>
    <div class="stat-box"><div class="num">{len(source_counts)}</div><div class="label">Sources</div></div>
    <div class="stat-box"><div class="num">{len(kw_counts)}</div><div class="label">Keywords</div></div>
    <div class="stat-box"><div class="num">{int(df['relevance_score'].mean()*100)}%</div><div class="label">Avg Relevance</div></div>
  </div>

  <div>{source_badges}</div>
  <div style="margin-top:.8rem">{kw_tags}</div>

  <h2>🏆 Top 10 Articles by Relevance</h2>
  <div class="cards-grid">{cards_html}</div>

  <h2>📋 Full Results Table</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr><th>Title</th><th>Source</th><th>Keyword</th><th>Published</th><th>Author</th><th>Relevance</th></tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>

  <footer>
    News Intelligence Scraper &nbsp;·&nbsp; Built with Python, requests &amp; BeautifulSoup
  </footer>
</body>
</html>"""

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    logger.info("HTML report saved -> %s", path)
    return path
