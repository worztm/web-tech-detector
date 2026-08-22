"""
Web Technology Detector — A powerful tool to detect technologies used by websites.

Detects 100+ technologies across 15+ categories including JavaScript frameworks,
CSS frameworks, CMS platforms, e-commerce, analytics, hosting, CDNs, databases,
security tools, and more. Generates beautiful shadcn/ui-inspired dark theme HTML reports
with interactive search, filtering, confidence scoring, and version extraction.

Features:
    - 250+ technology detection patterns with regex-based matching
    - Version extraction from scripts, headers, and metadata
    - Confidence scoring (high/medium/low) with evidence tracking
    - WordPress plugin/theme extraction
    - Cookie analysis for session technologies
    - Performance metrics (page size, load time, compression)
    - Social media meta detection (Open Graph, Twitter Cards)
    - Script analysis (inline vs external, ES modules, async/defer)
    - Link analysis (internal, external, API endpoints)
    - robots.txt and sitemap checking
    - Interactive shadcn/ui HTML reports with search/filter
    - JSON data export alongside HTML
    - Responsive dark theme with glassmorphism design
"""

__version__ = "1.2.0"
__author__ = "Waleed Masud"
__description__ = "Detect 100+ web technologies with beautiful dark theme reports"

# Export main classes for easy import
from .scraper import WebScraper
from .detector import TechnologyDetector
from .report import ReportGenerator
from .cli import analyze_url, main
