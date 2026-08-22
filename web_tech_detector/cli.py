"""
Command-line interface for Web Technology Detector.
Features: URL analysis, JSON export, verbose mode, multi-page crawling, custom headers.
"""

import os
import sys
import io
import json
import webbrowser
import argparse
import time
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, Iterable, Optional

# Fix encoding for Windows console (guard for environments without a buffer)
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from .scraper import WebScraper
from .detector import TechnologyDetector
from .report import ReportGenerator
from . import __version__


def _parse_headers(values: Optional[Iterable[str]]) -> Dict[str, str]:
    """Parse repeatable ``--header Name: value`` arguments."""
    headers: Dict[str, str] = {}
    for value in values or []:
        name, separator, header_value = value.partition(":")
        if not separator or not name.strip() or not header_value.strip():
            raise ValueError(f"Invalid header {value!r}; use --header 'Name: value'")
        headers[name.strip()] = header_value.strip()
    return headers


def analyze_url(
    url: str,
    output_dir: str = None,
    auto_open: bool = True,
    json_output: bool = False,
    verbose: bool = False,
    timeout: int = 30,
    follow_redirects: bool = True,
    check_robots: bool = False,
    check_sitemap: bool = False,
    detect_social: bool = True,
    headers: Optional[Dict[str, str]] = None,
) -> str:
    """
    Analyze a URL and generate a comprehensive technology report.

    Args:
        url: Target URL to analyze
        output_dir: Directory to save the report (default: current directory)
        auto_open: Whether to auto-open the report in browser
        json_output: Also save raw JSON data
        verbose: Enable verbose output
        timeout: Request timeout in seconds
        follow_redirects: Whether to follow redirects
        check_robots: Check robots.txt
        check_sitemap: Check sitemap.xml
        detect_social: Extract social media meta tags
        headers: Additional HTTP request headers

    Returns:
        Path to the generated report file
    """
    # Set output directory
    if not output_dir:
        output_dir = os.getcwd()

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Initialize components
    scraper = WebScraper(
        url,
        timeout=timeout,
        verify_ssl=True,
        follow_redirects=follow_redirects,
        headers=headers,
    )
    detector = TechnologyDetector()

    # Print header
    if verbose:
        print(f"\n{'='*60}")
        print(f"  🔍 Web Technology Detector v{__version__}")
        print(f"  Analyzing: {scraper.url}")
        print(f"{'='*60}")
    else:
        print(f"\n  🔍 Analyzing {scraper.url}...")

    # Start timing
    start_time = time.time()

    # Fetch the website
    if not scraper.fetch():
        print(f"  ❌ Failed to fetch the website. Please check the URL and try again.")
        raise RuntimeError("Failed to fetch the website. Please check the URL and try again.")

    fetch_time = time.time() - start_time

    if verbose:
        print(f"  ✅ Page fetched in {fetch_time:.2f}s")
        print(f"     Status: {scraper.status_code}")
        print(f"     Final URL: {scraper.final_url}")
        print(f"     Page size: {len(scraper.html)} bytes")
        if scraper.redirect_chain:
            print(f"     Redirects: {' → '.join(scraper.redirect_chain)} → {scraper.final_url}")
    else:
        print(f"  ✅ Page fetched (status: {scraper.status_code})")

    # Analyze technologies
    print(f"  🔬 Analyzing technologies...")

    technologies = detector.detect_all(scraper.html, scraper.soup, scraper.http_headers)
    meta_info = detector.detect_meta_info(scraper.soup)
    json_ld = detector.detect_json_ld(scraper.soup)
    server_info = detector.extract_server_info(scraper.http_headers)
    performance = detector.extract_performance_metrics(scraper.html, scraper.http_headers, fetch_time)

    # Social meta
    social_meta = {}
    if detect_social:
        social_meta = detector.detect_social_meta(scraper.soup)

    # Script & Link analysis
    script_analysis = detector.detect_script_analysis(scraper.soup)
    link_analysis = detector.detect_links_analysis(scraper.soup, domain=scraper.get_domain())

    # Cookie analysis
    cookie_findings = detector.analyze_cookies(scraper.cookies)

    # Robots & Sitemap
    robots_content = None
    sitemap_content = None
    if check_robots:
        if verbose:
            print(f"  🤖 Checking robots.txt...")
        robots_content = scraper.check_robots_txt()
    if check_sitemap:
        if verbose:
            print(f"  🗺️  Checking sitemap.xml...")
        sitemap_content = scraper.check_sitemap()

    # Compile results
    results = {
        "url": scraper.url,
        "domain": scraper.get_domain(),
        "title": scraper.soup.title.string if scraper.soup and scraper.soup.title else scraper.get_domain(),
        "status_code": scraper.status_code,
        "technologies": technologies,
        "meta_info": meta_info,
        "server_info": server_info,
        "json_ld": json_ld,
        "performance": performance,
        "social_meta": social_meta,
        "script_analysis": script_analysis,
        "link_analysis": link_analysis,
        "cookie_findings": cookie_findings,
        "robots": robots_content,
        "sitemap": sitemap_content,
        "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Generate report
    print(f"  📄 Generating HTML report...")
    generator = ReportGenerator(results)
    # Export JSON only when requested. ReportGenerator keeps JSON enabled by
    # default for direct library users, while the CLI flag remains opt-in.
    report_path = generator.save(output_dir, save_json=json_output)
    if json_output:
        json_path = os.path.splitext(report_path)[0] + ".json"
        print(f"  📋 JSON data exported to: {json_path}")

    # Print summary
    _print_summary(results, verbose)

    # Auto-open in browser
    if auto_open:
        try:
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
            print(f"  🌐 Opening report in your default browser...")
        except Exception as e:
            print(f"  ⚠️  Could not auto-open browser: {e}")

    print(f"\n  ✅ Report saved to:")
    print(f"     {report_path}")
    print()

    return report_path


def _print_summary(results: dict, verbose: bool = False):
    """Print a summary of detected technologies to the console."""
    technologies = results.get("technologies", {})

    # Count how many high-confidence techs
    high_count = 0
    for category, techs in technologies.items():
        for tech in techs:
            if isinstance(tech, dict) and tech.get("confidence") == "high":
                high_count += 1
            elif isinstance(tech, str):
                high_count += 1

    print(f"  {'─' * 56}")
    print(f"  📊 Summary: {high_count} technologies detected across {len([c for c, t in technologies.items() if t])} categories")
    print(f"  {'─' * 56}")

    if verbose:
        for category, techs in technologies.items():
            if techs:
                print(f"\n  ├─ {category}")
                for tech in techs:
                    if isinstance(tech, dict):
                        name = tech.get("name", "?")
                        version = tech.get("version")
                        confidence = tech.get("confidence", "low")
                        version_str = f" v{version}" if version else ""
                        conf_icon = "🟢" if confidence == "high" else "🟡" if confidence == "medium" else "🟠"
                        print(f"  │  {conf_icon} {name}{version_str}")
                    else:
                        print(f"  │  • {tech}")


def main():
    """Main entry point for CLI."""
    version_str = f"v{__version__}"
    parser = argparse.ArgumentParser(
        description="🔍 Web Technology Detector — detect technologies used by any website",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com                     # Basic scan
  %(prog)s github.com                              # Auto-adds https://
  %(prog)s https://wordpress.com --output ./reports # Custom output dir
  %(prog)s https://shopify.com --no-open            # Don't open browser
  %(prog)s https://example.com --json               # Also export JSON
  %(prog)s https://example.com --verbose            # Detailed output
  %(prog)s https://example.com --check-robots       # Check robots.txt
  %(prog)s https://example.com --timeout 60         # Extended timeout
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
        "--json",
        action="store_true",
        dest="json_output",
        help="Also export raw data as JSON",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output with detailed information",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--no-redirect",
        action="store_true",
        dest="no_redirect",
        help="Don't follow HTTP redirects",
    )
    parser.add_argument(
        "--check-robots",
        action="store_true",
        help="Check robots.txt for the domain",
    )
    parser.add_argument(
        "--check-sitemap",
        action="store_true",
        help="Check sitemap.xml for the domain",
    )
    parser.add_argument(
        "--no-social",
        action="store_true",
        dest="no_social",
        help="Skip social media meta tag detection",
    )
    parser.add_argument(
        "--header",
        action="append",
        dest="headers",
        metavar="NAME: VALUE",
        help="Add or override an HTTP request header (repeatable)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + version_str,
        help="Show program version",
    )

    args = parser.parse_args()

    # Print banner
    print(f"\n  {'═' * 56}")
    print(f"  🔍  Web Technology Detector  {version_str}")
    print(f"  {'═' * 56}")
    if args.verbose:
        print(f"  Detects 250+ technologies with confidence scoring and version extraction")
        print(f"  {'─' * 56}")

    # Get URL from argument or prompt
    url = args.url
    if not url:
        url = input("\n  Enter website URL: ").strip()

    if not url:
        print("  ❌ No URL provided. Exiting.")
        sys.exit(1)

    # Run analysis
    try:
        request_headers = _parse_headers(args.headers)
        analyze_url(
            url=url,
            output_dir=args.output,
            auto_open=not args.no_open,
            json_output=args.json_output,
            verbose=args.verbose,
            timeout=args.timeout,
            follow_redirects=not args.no_redirect,
            check_robots=args.check_robots,
            check_sitemap=args.check_sitemap,
            detect_social=not args.no_social,
            headers=request_headers,
        )
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
