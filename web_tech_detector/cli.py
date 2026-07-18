"""
Command-line interface for Web Technology Detector.
"""

import os
import sys
import io
import webbrowser
import argparse
from datetime import datetime

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from .scraper import WebScraper
from .detector import TechnologyDetector
from .report import ReportGenerator


def analyze_url(url: str, output_dir: str = None, auto_open: bool = True) -> str:
    """
    Analyze a URL and generate a technology report.

    Args:
        url: Target URL to analyze
        output_dir: Directory to save the report (default: current directory)
        auto_open: Whether to auto-open the report in browser

    Returns:
        Path to the generated report file
    """
    # Set output directory
    if output_dir is None:
        output_dir = os.getcwd()

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Initialize components
    scraper = WebScraper(url)
    detector = TechnologyDetector()

    # Fetch the website
    print(f"\n🔍 Fetching {scraper.url}...")
    if not scraper.fetch():
        print("❌ Failed to fetch the website. Please check the URL and try again.")
        sys.exit(1)
    print("✅ Page fetched successfully!")

    # Analyze technologies
    print("\n🔬 Analyzing technologies...")
    technologies = detector.detect_all(scraper.html, scraper.soup, scraper.http_headers)
    meta_info = detector.detect_meta_info(scraper.soup)
    json_ld = detector.detect_json_ld(scraper.soup)
    server_info = detector.extract_server_info(scraper.http_headers)

    # Compile results
    results = {
        "url": scraper.url,
        "domain": scraper.get_domain(),
        "title": scraper.soup.title.string if scraper.soup and scraper.soup.title else "",
        "status_code": scraper.status_code,
        "technologies": technologies,
        "meta_info": meta_info,
        "server_info": server_info,
        "json_ld": json_ld,
        "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Generate report
    print("📄 Generating HTML report...")
    generator = ReportGenerator(results)
    report_path = generator.save(output_dir)

    # Print summary
    _print_summary(results)

    # Auto-open in browser
    if auto_open:
        try:
            webbrowser.open(report_path)
            print(f"🌐 Opening report in your default browser...")
        except Exception as e:
            print(f"⚠️ Could not auto-open browser: {e}")

    print(f"\n✅ Report saved to:")
    print(f"   {report_path}")
    print(f"\n{'=' * 60}\n")

    return report_path


def _print_summary(results: dict):
    """Print a summary of detected technologies to the console."""
    print(f"\n{'=' * 60}")
    print("📊 Technology Summary")
    print(f"{'=' * 60}")

    technologies = results.get("technologies", {})
    for category, techs in technologies.items():
        if techs:
            print(f"\n{category}:")
            for tech in techs:
                print(f"  • {tech}")

    meta_info = results.get("meta_info", {})
    if meta_info:
        print("\nMeta Information:")
        for key, value in meta_info.items():
            print(f"  • {key}: {value}")

    server_info = results.get("server_info", {})
    if server_info:
        print("\nServer Info:")
        for key, value in server_info.items():
            print(f"  • {key}: {value}")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="🔍 Web Technology Detector - Detect technologies used by any website",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s github.com
  %(prog)s https://wordpress.com --output ./reports
  %(prog)s https://shopify.com --no-open
        """,
    )

    parser.add_argument(
        "url",
        nargs="?",
        help="URL of the website to analyze",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output directory for the report (default: current directory)",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Don't auto-open the report in browser",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    args = parser.parse_args()

    # Print banner
    print("\n" + "=" * 60)
    print("🔍 Web Technology Detector v1.0.0")
    print("=" * 60)

    # Get URL from argument or prompt
    url = args.url
    if not url:
        url = input("\nEnter website URL: ").strip()

    if not url:
        print("❌ No URL provided. Exiting.")
        sys.exit(1)

    # Run analysis
    analyze_url(
        url=url,
        output_dir=args.output,
        auto_open=not args.no_open,
    )


if __name__ == "__main__":
    main()
