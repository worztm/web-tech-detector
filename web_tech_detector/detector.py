"""
Technology detection module - Analyzes HTML content to identify web technologies.
"""

import re
import json
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


# Technology detection patterns organized by category
TECHNOLOGY_PATTERNS: Dict[str, Dict[str, List[str]]] = {
    "JavaScript Frameworks": {
        "React": [r"react\.min\.js", r"react\.js", r"react-dom", r"__NEXT_DATA__", r"next/static"],
        "Vue.js": [r"vue\.min\.js", r"vue\.js", r"vue\.runtime", r"v-cloak", r"vue-router"],
        "Angular": [r"angular\.min\.js", r"angular\.js", r"ng-version", r"ng-app", r"ng-controller"],
        "Svelte": [r"svelte", r"__svelte"],
        "Solid.js": [r"solid\.js", r"solid-js"],
        "Preact": [r"preact\.min\.js", r"preact\.js"],
        "Alpine.js": [r"alpine\.min\.js", r"alpine\.js", r"x-data"],
        "Stimulus": [r"stimulus\.js", r"stimulus.min.js", r"data-controller"],
        "jQuery": [r"jquery\.min\.js", r"jquery-[0-9]", r"jquery\.js"],
        "Backbone.js": [r"backbone\.min\.js", r"backbone\.js"],
        "Ember.js": [r"ember\.min\.js", r"ember\.js"],
    },
    "CSS Frameworks": {
        "Bootstrap": [r"bootstrap\.min\.css", r"bootstrap\.css", r"bootstrap\.min\.js"],
        "Tailwind CSS": [r"tailwind\.css", r"tailwindcss"],
        "Bulma": [r"bulma\.min\.css", r"bulma\.css"],
        "Foundation": [r"foundation\.min\.css", r"foundation\.css"],
        "Material Design": [r"material\.min\.css", r"material-design", r"materialicons"],
        "Materialize CSS": [r"materialize\.min\.css", r"materialize\.css"],
        "Ant Design": [r"antd\.min\.css", r"antd\.css"],
        "Chakra UI": [r"chakra-ui"],
        "Radix UI": [r"radix-ui"],
        "shadcn/ui": [r"shadcn", r"shadcnui"],
    },
    "Static Site Generators": {
        "Next.js": [r"__NEXT_DATA__", r"next/static", r"next/head"],
        "Nuxt.js": [r"__NUXT__", r"nuxt\.js", r"nuxt\.config"],
        "Gatsby": [r"gatsby", r"___gatsby"],
        "Hugo": [r"hugo", r"themes/"],
        "Jekyll": [r"jekyll", r"jekyll-"],
        "Astro": [r"astro"],
        "Vite": [r"vite/client", r"@vite"],
        "Remix": [r"remix", r"__remix"],
    },
    "CMS": {
        "WordPress": [r"wp-content", r"wp-includes", r"wordpress"],
        "Drupal": [r"drupal", r"sites/default/files"],
        "Joomla": [r"joomla", r"com_content"],
        "Shopify": [r"shopify", r"cdn\.shopify\.com"],
        "Wix": [r"wix", r"wixstatic\.com"],
        "Squarespace": [r"squarespace", r"sqsp"],
        "Ghost": [r"ghost/", r"ghost-"],
        "Contentful": [r"contentful"],
        "Webflow": [r"webflow"],
        "TYPO3": [r"typo3"],
    },
    "E-commerce": {
        "Shopify": [r"shopify", r"cdn\.shopify\.com"],
        "WooCommerce": [r"woocommerce", r"wc-"],
        "BigCommerce": [r"bigcommerce"],
        "Magento": [r"magento"],
        "OpenCart": [r"opencart"],
        "PrestaShop": [r"prestashop"],
    },
    "Analytics": {
        "Google Analytics": [r"google-analytics\.com", r"gtag", r"ga\.js", r"analytics\.js", r"G-[A-Z0-9]+"],
        "Google Tag Manager": [r"googletagmanager\.com", r"gtm\.js", r"GTM-[A-Z0-9]+"],
        "Hotjar": [r"hotjar\.com", r"hj\("],
        "Mixpanel": [r"mixpanel\.com", r"mixpanel"],
        "Segment": [r"segment\.com/analytics", r"analytics\.js"],
        "Plausible": [r"plausible\.io"],
        "Matomo": [r"matomo", r"piwik"],
        "Amplitude": [r"amplitude"],
        "Heap": [r"heapanalytics\.com"],
        "FullStory": [r"fullstory\.com"],
        "Clarity": [r"clarity\.ms"],
        "Facebook Pixel": [r"fbevents\.js", r"facebook\.com/tr"],
        "Hotjar": [r"hotjar\.com", r"_hjSettings"],
    },
    "Web Servers": {
        "Nginx": [r"nginx"],
        "Apache": [r"apache"],
        "LiteSpeed": [r"litespeed"],
        "IIS": [r"Microsoft-IIS"],
        "Caddy": [r"caddy"],
    },
    "Programming Languages": {
        "PHP": [r"\.php", r"x-powered-by.*php"],
        "Python": [r"python", r"django", r"flask"],
        "Ruby": [r"ruby", r"rails", r"passenger"],
        "Java": [r"java", r"tomcat", r"jboss"],
        "Node.js": [r"node\.js", r"express"],
        ".NET": [r"asp\.net", r"dotnet", r"\.aspx"],
    },
    "Hosting & CDN": {
        "Cloudflare": [r"cloudflare", r"cf-ray"],
        "AWS": [r"amazonaws\.com", r"aws"],
        "Netlify": [r"netlify"],
        "Vercel": [r"vercel", r"now\.sh"],
        "Google Cloud": [r"googleapis\.com", r"gcp"],
        "Azure": [r"azure", r"azurewebsites"],
        "Heroku": [r"herokuapp\.com"],
        "GitHub Pages": [r"github\.io", r"github-pages"],
        "Fastly": [r"fastly"],
        "Akamai": [r"akamai"],
        "KeyCDN": [r"keycdn"],
    },
    "Libraries": {
        "Lodash": [r"lodash\.min\.js", r"lodash\.js"],
        "Moment.js": [r"moment\.min\.js", r"moment\.js"],
        "GSAP": [r"gsap\.min\.js", r"gsap\.js", r"greensock"],
        "Three.js": [r"three\.min\.js", r"three\.js"],
        "D3.js": [r"d3\.min\.js", r"d3\.js", r"d3\.v"],
        "Chart.js": [r"chart\.min\.js", r"chart\.js"],
        "Anime.js": [r"anime\.min\.js"],
        "AOS": [r"aos\.js", r"aos\.css"],
        "Swiper": [r"swiper\.min\.js", r"swiper\.js"],
        "Font Awesome": [r"fontawesome", r"font-awesome", r"fa-"],
        "Google Fonts": [r"fonts\.googleapis\.com"],
    },
    "Security": {
        "reCAPTCHA": [r"recaptcha", r"grecaptcha"],
        "hCaptcha": [r"hcaptcha"],
        "Cloudflare Turnstile": [r"turnstile"],
    },
    "Features": {
        "Schema.org": [r"schema\.org", r"application/ld\+json"],
        "Open Graph": [r"og:title", r"og:description", r"og:image"],
        "Twitter Cards": [r"twitter:card"],
        "PWA": [r"manifest\.json", r"service-worker"],
        "GraphQL": [r"graphql"],
        "REST API": [r"/api/", r"application/json"],
        "Lazy Loading": [r"loading=.lazy"],
        "Preload": [r"rel=.preload"],
    },
}


class TechnologyDetector:
    """Detects web technologies from HTML content and HTTP headers."""

    def __init__(self):
        self.patterns = TECHNOLOGY_PATTERNS

    def detect_all(self, html: str, soup: BeautifulSoup, http_headers: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Run all detection methods and return combined results.

        Args:
            html: Raw HTML content
            soup: Parsed BeautifulSoup object
            http_headers: HTTP response headers

        Returns:
            Dictionary of category -> list of detected technologies
        """
        results: Dict[str, List[str]] = {}

        # Detect from HTML content
        html_detections = self._detect_from_html(html)
        results.update(html_detections)

        # Detect from HTTP headers
        header_detections = self._detect_from_headers(http_headers)
        if header_detections:
            results["Server Headers"] = header_detections

        return results

    def _detect_from_html(self, html: str) -> Dict[str, List[str]]:
        """Detect technologies by pattern matching against HTML source."""
        detected: Dict[str, List[str]] = {}

        for category, techs in self.patterns.items():
            category_matches = []

            for tech_name, patterns in techs.items():
                for pattern in patterns:
                    if re.search(pattern, html, re.IGNORECASE):
                        if tech_name not in category_matches:
                            category_matches.append(tech_name)
                        break

            if category_matches:
                detected[category] = category_matches

        return detected

    def _detect_from_headers(self, headers: Dict[str, str]) -> List[str]:
        """Detect technologies from HTTP response headers."""
        techs = []

        header_checks = {
            "php": "PHP",
            "asp.net": "ASP.NET",
            "express": "Node.js/Express",
            "django": "Django",
            "rails": "Ruby on Rails",
        }

        for header, value in headers.items():
            if isinstance(value, str):
                value_lower = value.lower()
                for pattern, tech_name in header_checks.items():
                    if pattern in value_lower and tech_name not in techs:
                        techs.append(tech_name)

        return techs

    def detect_meta_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract technology hints from meta tags."""
        meta_info = {}

        # Generator meta tag
        generator = soup.find("meta", attrs={"name": "generator"})
        if generator and generator.get("content"):
            meta_info["Generator"] = generator["content"]

        # Theme/CMS hints
        for meta in soup.find_all("meta"):
            name = meta.get("name", "").lower()
            content = meta.get("content", "")

            if "theme" in name:
                meta_info["Theme"] = content
            elif "cms" in name or "platform" in name:
                meta_info["Platform"] = content

        return meta_info

    def detect_json_ld(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract JSON-LD structured data."""
        json_ld_data = []

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                json_ld_data.append(data)
            except (json.JSONDecodeError, TypeError):
                pass

        return json_ld_data

    def extract_server_info(self, http_headers: Dict[str, str]) -> Dict[str, str]:
        """Extract server information from HTTP headers."""
        server_info = {}

        header_mapping = {
            "Server": "Server",
            "X-Powered-By": "Powered By",
            "X-AspNet-Version": "ASP.NET Version",
        }

        for header, label in header_mapping.items():
            if header in http_headers:
                server_info[label] = http_headers[header]

        # Detect CDN
        if "CF-RAY" in http_headers or "cf-ray" in http_headers:
            server_info["CDN"] = "Cloudflare"

        return server_info
