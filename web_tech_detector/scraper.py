"""
Web scraper module - Fetches and parses website content.
Supports performance timing, cookie collection, robots.txt, and sitemap detection.
"""

import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import Optional, Dict, List, Tuple, Mapping


class WebScraper:
    """Fetches webpage content and extracts raw data for analysis."""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self, url: str, timeout: int = 30, verify_ssl: bool = True,
                 follow_redirects: bool = True,
                 headers: Optional[Mapping[str, str]] = None):
        """
        Initialize the scraper.

        Args:
            url: Target URL to scrape
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            follow_redirects: Whether to follow redirects
            headers: Additional request headers. These override defaults by name.
        """
        self.url = self._normalize_url(url)
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects
        self.headers = dict(self.DEFAULT_HEADERS)
        if headers:
            self.headers.update({str(key): str(value) for key, value in headers.items()})
        self.session = requests.Session()
        self.response: Optional[requests.Response] = None
        self.soup: Optional[BeautifulSoup] = None
        self.html: str = ""
        self.http_headers: Dict[str, str] = {}
        self.cookies: Dict[str, str] = {}
        self.elapsed_time: float = 0.0
        self.redirect_chain: List[str] = []
        self.robots_url: Optional[str] = None
        self.sitemap_url: Optional[str] = None

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize and validate an HTTP(S) URL."""
        if not isinstance(url, str) or not url.strip():
            raise ValueError("url must be a non-empty string")

        value = url.strip()
        if not re.match(r"^https?://", value, re.IGNORECASE):
            value = f"https://{value}"

        parsed = urlparse(value)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
            raise ValueError("url must contain a valid http:// or https:// host")
        if parsed.username or parsed.password:
            raise ValueError("URLs with embedded credentials are not supported")
        try:
            parsed.port
        except ValueError as exc:
            raise ValueError("url contains an invalid port") from exc
        return parsed._replace(scheme=parsed.scheme.lower()).geturl()

    def fetch(self) -> bool:
        """
        Fetch the webpage content.

        Returns:
            True if successful, False otherwise.
        """
        start_time = time.time()
        self.response = None
        self.soup = None
        self.html = ""
        self.http_headers = {}
        self.cookies = {}
        self.elapsed_time = 0.0
        self.redirect_chain = []

        try:
            self.response = self.session.get(
                self.url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=self.follow_redirects,
                verify=self.verify_ssl,
            )
            self.elapsed_time = time.time() - start_time
            self.response.raise_for_status()
            self._parse_response()

            # Track redirects
            if self.follow_redirects and self.response.history:
                for resp in self.response.history:
                    self.redirect_chain.append(resp.url)

            return True

        except requests.exceptions.TooManyRedirects:
            # Retry without following redirects
            return self._retry_no_redirects(start_time)

        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Error fetching URL: {e}")
            return False

    def _retry_no_redirects(self, start_time: float) -> bool:
        """Retry without following redirects."""
        try:
            self.response = self.session.get(
                self.url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=False,
                verify=self.verify_ssl,
            )
            self.elapsed_time = time.time() - start_time
            self._parse_response()
            return True
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Error fetching URL (no redirects): {e}")
            return False

    def _parse_response(self):
        """Parse the response content."""
        if self.response is None:
            return
        self.html = self.response.text
        self.soup = BeautifulSoup(self.html, "html.parser")
        # Normalize header keys to lowercase so lookups are case-insensitive
        self.http_headers = {k.lower(): v for k, v in self.response.headers.items()}
        self.cookies = dict(self.response.cookies)

    def check_robots_txt(self) -> Optional[str]:
        """Check if robots.txt exists and return content summary."""
        parsed = urlparse(self.final_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        self.robots_url = robots_url

        try:
            resp = self.session.get(robots_url, timeout=5, headers=self.headers, verify=self.verify_ssl)
            if resp.status_code == 200:
                return resp.text[:2000]  # Return first 2000 chars
        except requests.exceptions.RequestException:
            pass
        return None

    def check_sitemap(self) -> Optional[str]:
        """Check if sitemap.xml exists."""
        parsed = urlparse(self.final_url)
        sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        self.sitemap_url = sitemap_url

        try:
            resp = self.session.get(sitemap_url, timeout=5, headers=self.headers, verify=self.verify_ssl)
            if resp.status_code == 200:
                return resp.text[:2000]
        except requests.exceptions.RequestException:
            pass
        return None

    def get_domain(self) -> str:
        """Extract the domain from the URL."""
        parsed = urlparse(self.final_url)
        return parsed.netloc

    def get_base_url(self) -> str:
        """Get the base URL of the page."""
        parsed = urlparse(self.final_url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def get_all_links(self) -> List[str]:
        """Extract all internal links from the page."""
        links = []
        base = self.final_url
        page_host = (urlparse(base).hostname or "").lower()

        for a in self.soup.find_all("a", href=True) if self.soup else []:
            href = str(a["href"]).strip()
            full_url = urljoin(base, href)
            # Only keep links that live on the same host. Ignore non-HTTP links
            # such as mailto:, tel:, and javascript:.
            parsed_url = urlparse(full_url)
            if parsed_url.scheme in {"http", "https"} and (parsed_url.hostname or "").lower() == page_host:
                links.append(full_url)

        return list(dict.fromkeys(links))

    def get_resource_urls(self) -> Dict[str, List[str]]:
        """Extract normalized URLs of resources referenced by the page."""
        resources = {
            "scripts": [],
            "stylesheets": [],
            "images": [],
            "fonts": [],
            "iframes": [],
        }

        if not self.soup:
            return resources

        for script in self.soup.find_all("script", src=True):
            resources["scripts"].append(urljoin(self.final_url, script["src"]))

        for link in self.soup.find_all("link", rel="stylesheet", href=True):
            resources["stylesheets"].append(urljoin(self.final_url, link["href"]))

        for img in self.soup.find_all("img", src=True):
            resources["images"].append(urljoin(self.final_url, img["src"]))

        for iframe in self.soup.find_all("iframe", src=True):
            resources["iframes"].append(urljoin(self.final_url, iframe["src"]))

        for link in self.soup.find_all("link", href=True):
            rel = {str(value).lower() for value in (link.get("rel") or [])}
            if "preload" in rel and str(link.get("as", "")).lower() == "font":
                resources["fonts"].append(urljoin(self.final_url, link["href"]))

        for resource_type, urls in resources.items():
            resources[resource_type] = list(dict.fromkeys(urls))

        return resources

    @property
    def is_success(self) -> bool:
        """Check if the last request was successful."""
        return self.response is not None and 200 <= self.response.status_code < 300

    @property
    def status_code(self) -> Optional[int]:
        """Get the HTTP status code."""
        return self.response.status_code if self.response else None

    @property
    def final_url(self) -> str:
        """Get the final URL after redirects."""
        return self.response.url if self.response else self.url
