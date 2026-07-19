"""
Web scraper module - Fetches and parses website content.
Supports performance timing, cookie collection, robots.txt, and sitemap detection.
"""

import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import Optional, Dict, List, Tuple


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
                 follow_redirects: bool = True):
        """
        Initialize the scraper.

        Args:
            url: Target URL to scrape
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            follow_redirects: Whether to follow redirects
        """
        self.url = self._normalize_url(url)
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects
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
        """Ensure URL has a scheme (https://)."""
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            return f"https://{url}"
        return url

    def fetch(self) -> bool:
        """
        Fetch the webpage content.

        Returns:
            True if successful, False otherwise.
        """
        start_time = time.time()

        try:
            session = requests.Session()
            self.response = session.get(
                self.url,
                headers=self.DEFAULT_HEADERS,
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

        except requests.exceptions.SSLError:
            # Retry without SSL verification
            return self._retry_without_ssl(start_time)

        except requests.exceptions.TooManyRedirects:
            # Retry without following redirects
            return self._retry_no_redirects(start_time)

        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Error fetching URL: {e}")
            return False

    def _retry_without_ssl(self, start_time: float) -> bool:
        """Retry the request with SSL verification disabled."""
        try:
            self.response = requests.get(
                self.url,
                headers=self.DEFAULT_HEADERS,
                timeout=self.timeout,
                allow_redirects=self.follow_redirects,
                verify=False,
            )
            self.elapsed_time = time.time() - start_time
            self.response.raise_for_status()
            self._parse_response()
            return True
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Error fetching URL (SSL disabled): {e}")
            return False

    def _retry_no_redirects(self, start_time: float) -> bool:
        """Retry without following redirects."""
        try:
            self.response = requests.get(
                self.url,
                headers=self.DEFAULT_HEADERS,
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
        self.http_headers = dict(self.response.headers)
        self.cookies = dict(self.response.cookies)

    def check_robots_txt(self) -> Optional[str]:
        """Check if robots.txt exists and return content summary."""
        parsed = urlparse(self.url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        self.robots_url = robots_url

        try:
            resp = requests.get(robots_url, timeout=5, headers=self.DEFAULT_HEADERS)
            if resp.status_code == 200:
                return resp.text[:2000]  # Return first 2000 chars
        except requests.exceptions.RequestException:
            pass
        return None

    def check_sitemap(self) -> Optional[str]:
        """Check if sitemap.xml exists."""
        parsed = urlparse(self.url)
        sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        self.sitemap_url = sitemap_url

        try:
            resp = requests.get(sitemap_url, timeout=5, headers=self.DEFAULT_HEADERS)
            if resp.status_code == 200:
                return resp.text[:2000]
        except requests.exceptions.RequestException:
            pass
        return None

    def get_domain(self) -> str:
        """Extract the domain from the URL."""
        parsed = urlparse(self.url)
        return parsed.netloc

    def get_base_url(self) -> str:
        """Get the base URL of the page."""
        parsed = urlparse(self.url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def get_all_links(self) -> List[str]:
        """Extract all internal links from the page."""
        links = []
        base = self.get_base_url()
        domain = self.get_domain()

        for a in self.soup.find_all("a", href=True) if self.soup else []:
            href = a["href"]
            if href.startswith("/") or href.startswith(base) or domain in href:
                full_url = urljoin(base, href)
                if full_url.startswith(base):
                    links.append(full_url)

        return list(set(links))

    def get_resource_urls(self) -> Dict[str, List[str]]:
        """Extract URLs of external resources."""
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
            resources["scripts"].append(script["src"])

        for link in self.soup.find_all("link", rel="stylesheet", href=True):
            resources["stylesheets"].append(link["href"])

        for img in self.soup.find_all("img", src=True):
            resources["images"].append(img["src"])

        for iframe in self.soup.find_all("iframe", src=True):
            resources["iframes"].append(iframe["src"])

        return resources

    @property
    def is_success(self) -> bool:
        """Check if the last request was successful."""
        return self.response is not None and self.response.status_code == 200

    @property
    def status_code(self) -> Optional[int]:
        """Get the HTTP status code."""
        return self.response.status_code if self.response else None

    @property
    def final_url(self) -> str:
        """Get the final URL after redirects."""
        return self.response.url if self.response else self.url
