"""
Example usage of the Web Technology Detector library.
Demonstrates the full API with all available features.
"""

import os
import sys

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_tech_detector import WebScraper, TechnologyDetector, ReportGenerator, analyze_url
from datetime import datetime


def basic_usage():
    """Simplest usage — just analyze a URL."""
    print("\n" + "=" * 60)
    print("📌 Basic Usage")
    print("=" * 60)

    report_path = analyze_url(
        url="https://example.com",
        output_dir="./examples/output",
        auto_open=False,
    )
    print(f"Report: {report_path}")


def advanced_usage():
    """Advanced usage with all features manually."""
    print("\n" + "=" * 60)
    print("📌 Advanced Usage (Manual API)")
    print("=" * 60)

    url = "https://github.com"
    output_dir = "./examples/output"
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Fetch with custom settings
    print(f"\n  🔍 Fetching {url}...")
    scraper = WebScraper(
        url,
        timeout=15,
        verify_ssl=True,
        follow_redirects=True,
    )

    if not scraper.fetch():
        print("  ❌ Failed to fetch")
        return

    print(f"  ✅ Status: {scraper.status_code}")
    print(f"  ✅ Time: {scraper.elapsed_time:.2f}s")
    print(f"  ✅ Domain: {scraper.get_domain()}")
    print(f"  ✅ Final URL: {scraper.final_url}")

    # Step 2: Detect everything
    print(f"\n  🔬 Running detection...")
    detector = TechnologyDetector()

    technologies = detector.detect_all(
        html=scraper.html,
        soup=scraper.soup,
        http_headers=scraper.http_headers,
    )
    print(f"  ✅ Found {sum(len(v) for v in technologies.values())} technologies")

    # Additional analyses
    meta_info = detector.detect_meta_info(scraper.soup)
    json_ld = detector.detect_json_ld(scraper.soup)
    server_info = detector.extract_server_info(scraper.http_headers)
    performance = detector.extract_performance_metrics(
        scraper.html, scraper.http_headers, scraper.elapsed_time
    )
    social_meta = detector.detect_social_meta(scraper.soup)
    script_analysis = detector.detect_script_analysis(scraper.soup)
    link_analysis = detector.detect_links_analysis(scraper.soup)
    cookie_findings = detector.analyze_cookies(scraper.cookies)

    print(f"  ✅ Meta fields: {len(meta_info)}")
    print(f"  ✅ JSON-LD items: {len(json_ld)}")
    print(f"  ✅ Performance: {performance.get('response_time_ms', '?')}ms, {performance.get('page_size_formatted', '?')}")
    print(f"  ✅ Social tags: {len(social_meta)} platforms")

    # Optional checks
    print(f"\n  🤖 Checking robots.txt...")
    robots = scraper.check_robots_txt()
    print(f"  {'✅ Found' if robots else '❌ Not found'}")

    print(f"  🗺️  Checking sitemap.xml...")
    sitemap = scraper.check_sitemap()
    print(f"  {'✅ Found' if sitemap else '❌ Not found'}")

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
        "performance": performance,
        "social_meta": social_meta,
        "script_analysis": script_analysis,
        "link_analysis": link_analysis,
        "cookie_findings": cookie_findings,
        "robots": robots,
        "sitemap": sitemap,
        "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Step 4: Generate report
    print(f"\n  📄 Generating HTML report...")
    generator = ReportGenerator(results)
    report_path = generator.save(output_dir)
    print(f"  ✅ Report: {report_path}")

    # Also save JSON
    json_path = report_path.replace(".html", ".json")
    print(f"  ✅ JSON: {json_path}")

    # Print summary
    print(f"\n{'─' * 50}")
    print("📊 Technology Summary")
    print(f"{'─' * 50}")

    for category, techs in technologies.items():
        if techs:
            print(f"\n  {category}:")
            for tech in techs:
                if isinstance(tech, dict):
                    name = tech.get("name", "?")
                    version = tech.get("version")
                    confidence = tech.get("confidence", "low")
                    extra = f" v{version}" if version else ""
                    conf_icon = "🟢" if confidence == "high" else "🟡" if confidence == "medium" else "🟠"
                    print(f"    {conf_icon} {name}{extra}")
                else:
                    print(f"    • {tech}")

    return report_path


def batch_analysis():
    """Analyze multiple URLs in batch."""
    print("\n" + "=" * 60)
    print("📌 Batch Analysis")
    print("=" * 60)

    urls = [
        "https://example.com",
        "https://httpbin.org",
    ]

    for url in urls:
        print(f"\n  Analyzing: {url}")
        try:
            analyze_url(
                url=url,
                output_dir="./examples/output",
                auto_open=False,
                verbose=False,
            )
        except Exception as e:
            print(f"  ❌ Error: {e}")


def main():
    """Run all examples."""
    os.makedirs("./examples/output", exist_ok=True)

    print("\n")
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║   Web Technology Detector — Examples         ║")
    print("  ║   Detects 100+ technologies                  ║")
    print("  ║   Beautiful shadcn/ui dark theme reports     ║")
    print("  ╚══════════════════════════════════════════════╝")

    basic_usage()
    advanced_usage()
    # batch_analysis()

    print("\n  ✅ All examples completed!")


if __name__ == "__main__":
    main()
