"""
main.py - CLI entry point for the News Intelligence Scraper.

Usage examples
--------------
# Use default keywords from settings.py
python main.py

# Custom keywords
python main.py --keywords "climate change" "renewable energy" "solar power"

# Skip certain export formats
python main.py --keywords "AI" --no-excel

# Quiet mode (less console output)
python main.py --keywords "blockchain" --quiet
"""

import argparse
import os
import sys
import time
import webbrowser

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so sub-packages resolve correctly
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import DEFAULT_KEYWORDS, DEFAULT_EXPORTS
from scraper.orchestrator import run as scrape
from exporter.exporters import export_csv, export_json, export_excel, export_html
from utils.logger import get_logger

logger = get_logger("main")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="News Intelligence Scraper — keyword-based article aggregator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--keywords", "-k",
        nargs="+",
        default=DEFAULT_KEYWORDS,
        metavar="KEYWORD",
        help="One or more search keywords (use quotes for phrases)",
    )
    parser.add_argument(
        "--no-csv",   action="store_true", help="Skip CSV export"
    )
    parser.add_argument(
        "--no-json",  action="store_true", help="Skip JSON export"
    )
    parser.add_argument(
        "--no-excel", action="store_true", help="Skip Excel export"
    )
    parser.add_argument(
        "--no-html",  action="store_true", help="Skip HTML report"
    )
    parser.add_argument(
        "--open-report", action="store_true",
        help="Automatically open the HTML report in your browser when done",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Reduce console verbosity"
    )
    return parser.parse_args()


def print_banner(keywords: list[str]) -> None:
    width = 60
    print("\n" + "═" * width)
    print("  📰  NEWS INTELLIGENCE SCRAPER")
    print("═" * width)
    print(f"  Keywords : {', '.join(keywords)}")
    print("═" * width + "\n")


def print_summary(articles, paths: dict) -> None:
    from collections import Counter
    sources = Counter(a.source for a in articles)
    print("\n" + "─" * 60)
    print(f"  ✅  Scraping complete — {len(articles)} articles collected")
    print("─" * 60)
    for src, cnt in sources.most_common():
        print(f"     {src:25s} {cnt:>3} articles")
    print("\n  📁  Output files:")
    for fmt, path in paths.items():
        print(f"     [{fmt.upper():5s}] {path}")
    print("─" * 60 + "\n")


def main() -> None:
    args = parse_args()

    if args.quiet:
        import logging
        logging.getLogger().setLevel(logging.WARNING)

    print_banner(args.keywords)
    t0 = time.time()

    # --- Scrape ---
    articles = scrape(keywords=args.keywords)

    if not articles:
        logger.error("No articles found. Check your internet connection or keywords.")
        sys.exit(1)

    # --- Export ---
    ts = time.strftime("%Y%m%d_%H%M%S")
    output_paths: dict[str, str] = {}

    if not args.no_csv:
        output_paths["csv"] = export_csv(articles, f"articles_{ts}.csv")

    if not args.no_json:
        output_paths["json"] = export_json(articles, f"articles_{ts}.json")

    if not args.no_excel:
        output_paths["excel"] = export_excel(articles, f"articles_{ts}.xlsx")

    if not args.no_html:
        html_path = export_html(articles, args.keywords, f"report_{ts}.html")
        output_paths["html"] = html_path
        if args.open_report:
            webbrowser.open(f"file://{os.path.abspath(html_path)}")

    elapsed = time.time() - t0
    logger.info("Total time: %.1fs", elapsed)
    print_summary(articles, output_paths)


if __name__ == "__main__":
    main()
