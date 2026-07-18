"""
Example usage of the Web Technology Detector library.
"""

import os
import sys

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_tech_detector.scraper import WebScraper
from web_tech_detector.detector import TechnologyDetector
from web_tech_detector.report import ReportGenerator
from datetime import datetime


def analyze_website(url: str, output_dir: str = "./output"):
    """
    Analyze a website and generate a report.

    Args:
        url: Target URL to analyze
        output_dir: Directory to save the report
    """
    print(f"\n🔍 Analyzing: {url}\n")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Fetch the website
    scraper = WebScraper(url, timeout=30)
    if not scraper.fetch():
        print("❌ Failed to fetch website")
        return

    print(f"✅ Fetched: {scraper.final_url}")
    print(f"   Status: {scraper.status_code}")

    # Step 2: Detect technologies
    detector = TechnologyDetector()

    technologies = detector.detect_all(
        html=scraper.html,
        soup=scraper.soup,
        http_headers=scraper.http_headers
    )

    meta_info = detector.detect_meta_info(scraper.soup)
    json_ld = detector.detect_json_ld(scraper.soup)
    server_info = detector.extract_server_info(scraper.http_headers)

    # Step 3: Compile results
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

    # Step 4: Generate report
    generator = ReportGenerator(results)
    report_path = generator.save(output_dir)

    print(f"\n📄 Report saved to: {report_path}")

    # Print summary
    print("\n" + "=" * 50)
    print("📊 Detected Technologies:")
    print("=" * 50)

    for category, techs in technologies.items():
        if techs:
            print(f"\n{category}:")
            for tech in techs:
                print(f"  • {tech}")

    return report_path


def main():
    """Run example analysis."""
    # Example URLs to analyze
    urls = [
        "https://example.com",
        # Add more URLs here
    ]

    for url in urls:
        analyze_website(url, output_dir="./examples/output")


if __name__ == "__main__":
    main()
