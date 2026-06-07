# 📰 News Intelligence Scraper

> A production-grade Python tool that aggregates articles from multiple news sources and research databases by keyword — then exports clean, structured reports in CSV, JSON, Excel, and HTML.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Tests](https://img.shields.io/badge/Tests-13%20passing-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square)

---

## 📌 Project Overview

News Intelligence Scraper is a **modular, multi-source news and research aggregator** built with clean Python architecture. Given a list of keywords, it simultaneously queries:

| Source | Type | API Key? |
|--------|------|----------|
| **Hacker News** (Algolia API) | REST API | ❌ Free |
| **The Guardian** | REST API | ✅ Free tier |
| **arXiv** | Atom/XML feed | ❌ Free |
| **BBC News** | HTML scraping | ❌ Free |

Results are de-duplicated, scored for relevance, and exported to **four formats** with a single command.

---

## ✨ Features

- 🔍 **Keyword-based search** — pass any number of terms from the CLI
- ⚡ **Concurrent scraping** — `ThreadPoolExecutor` runs all sources in parallel
- 🧠 **Relevance scoring** — custom algorithm ranks articles by keyword density, metadata completeness, and title matches
- 🗂️ **Four export formats** — CSV, JSON, multi-sheet Excel, and a polished dark-theme HTML report
- 🔄 **Automatic retries** — exponential back-off handles transient server errors
- 🪵 **Structured logging** — rotating log file + colour console output
- 🧩 **Plugin architecture** — add a new source by subclassing `BaseScraper` in one file
- ✅ **13 unit tests** — `pytest` coverage across models, scoring, and orchestration

---

## 📁 Project Structure

```
news_scraper/
├── main.py                     # CLI entry point
├── requirements.txt
├── .env.example                # copy to .env and add your API keys
├── .gitignore
│
├── config/
│   └── settings.py             # all tunable parameters in one place
│
├── scraper/
│   ├── base_scraper.py         # abstract base with HTTP session + retries
│   ├── hackernews_scraper.py   # Hacker News Algolia API
│   ├── guardian_scraper.py     # The Guardian Open API
│   ├── arxiv_scraper.py        # arXiv Atom feed
│   ├── bbc_scraper.py          # BBC News HTML (BeautifulSoup)
│   └── orchestrator.py         # parallel runner + de-duplication
│
├── exporter/
│   └── exporters.py            # CSV / JSON / Excel / HTML exporters
│
├── utils/
│   ├── models.py               # Article dataclass
│   ├── relevance.py            # keyword relevance scoring
│   └── logger.py               # rotating-file + console logger
│
├── tests/
│   └── test_scraper.py         # 13 pytest unit tests
│
└── output/
    ├── raw/                    # CSV, JSON, XLSX files
    └── reports/                # HTML report
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/news-intelligence-scraper.git
cd news-intelligence-scraper

# 2. Create and activate a virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys (optional)
cp .env.example .env
# Edit .env — only GUARDIAN_API_KEY is needed; leave as "test" for free tier
```

---

## 🎯 Usage

### Basic — use default keywords from `settings.py`
```bash
python main.py
```

### Custom keywords
```bash
python main.py --keywords "climate change" "renewable energy"
```

### Open the HTML report automatically in your browser
```bash
python main.py --keywords "machine learning" --open-report
```

### Skip specific export formats
```bash
python main.py --keywords "python" --no-excel --no-json
```

### Full option list
```
python main.py --help

options:
  --keywords KEYWORD [KEYWORD ...]   Search terms (use quotes for phrases)
  --no-csv      Skip CSV export
  --no-json     Skip JSON export
  --no-excel    Skip Excel export
  --no-html     Skip HTML report
  --open-report Open HTML report in browser on completion
  --quiet       Reduce console verbosity
```

### Run tests
```bash
pytest tests/ -v
```

---

## 📊 Sample Output

After running with `--keywords "artificial intelligence" "web scraping"`:

```
════════════════════════════════════════════════════════════
  📰  NEWS INTELLIGENCE SCRAPER
════════════════════════════════════════════════════════════
  Keywords : artificial intelligence, web scraping
════════════════════════════════════════════════════════════

[2025-06-01 14:22:10] INFO  orchestrator — Starting scrape — 2 keyword(s) × 4 source(s)
[2025-06-01 14:22:11] INFO  scraper.hacker_news — ✓ 10 articles found in 0.8s
[2025-06-01 14:22:11] INFO  scraper.the_guardian — ✓ 10 articles found in 1.1s
[2025-06-01 14:22:12] INFO  scraper.arxiv — ✓ 10 articles found in 1.4s
[2025-06-01 14:22:12] INFO  scraper.bbc_news — ✓ 8 articles found in 0.9s
[2025-06-01 14:22:12] INFO  orchestrator — De-duplicated: 38 → 35 articles
[2025-06-01 14:22:12] INFO  orchestrator — Total articles collected: 35

────────────────────────────────────────────────────────────
  ✅  Scraping complete — 35 articles collected
────────────────────────────────────────────────────────────
     Hacker News            12 articles
     The Guardian           10 articles
     arXiv                  8 articles
     BBC News               5 articles

  📁  Output files:
     [CSV  ] output/raw/articles_20250601_142212.csv
     [JSON ] output/raw/articles_20250601_142212.json
     [EXCEL] output/raw/articles_20250601_142212.xlsx
     [HTML ] output/reports/report_20250601_142212.html
────────────────────────────────────────────────────────────
```

The HTML report opens as a **dark-theme dashboard** with:
- Summary statistics (total articles, sources, avg relevance)
- Top-10 article cards with relevance bars
- Full scrollable table with all results

---

## 🖼️ Screenshots

> _Add screenshots of the HTML report here after running the project._
>
> Suggested files to capture:
> - `output/reports/report_*.html` opened in a browser
> - The terminal output after a successful run
> - The Excel workbook showing the three sheets

---

## 🔧 Configuration

All settings live in `config/settings.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `DEFAULT_KEYWORDS` | `["artificial intelligence", ...]` | Keywords used when none are passed via CLI |
| `MAX_ARTICLES_PER_SOURCE` | `10` | Articles fetched per keyword per source |
| `REQUEST_DELAY` | `1.2` | Polite delay between requests (seconds) |
| `REQUEST_TIMEOUT` | `15` | HTTP timeout per request |
| `DEFAULT_EXPORTS` | all four | Which formats to generate |

---

## 🛠️ Adding a New Source

1. Create `scraper/mysource_scraper.py` subclassing `BaseScraper`
2. Implement the single `fetch(keyword: str) -> list[Article]` method
3. Register it in `scraper/orchestrator.py`:
   ```python
   from scraper.mysource_scraper import MySourceScraper
   SCRAPER_REGISTRY["mysource"] = MySourceScraper
   ```
4. Add its config block to `config/settings.py`

That's it — the orchestrator picks it up automatically.

---

## 🔮 Future Improvements

- [ ] **Playwright integration** for JavaScript-heavy sites (e.g. Reuters, Bloomberg)
- [ ] **SQLite persistence** — store results in a local DB, avoid re-scraping known URLs
- [ ] **Scheduled runs** via APScheduler or cron with email/Slack digest
- [ ] **PDF ingestion** — extract and index text from uploaded PDFs alongside web articles
- [ ] **Sentiment analysis** — annotate articles with positive/negative/neutral sentiment
- [ ] **Streamlit dashboard** — interactive web UI for keyword entry and live result browsing
- [ ] **RSS feed support** — generic parser for any site exposing an RSS/Atom feed
- [ ] **Docker container** — one-command deployment anywhere

---

## 📄 License

MIT — see `LICENSE` for details.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change. Ensure tests pass (`pytest tests/ -v`) before submitting.
