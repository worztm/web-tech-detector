"""
Web scraper module - Fetches and parses website content.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Optional, Dict


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
    }

    def __init__(self, url: str, timeout: int = 30, verify_ssl: bool = True):
        """
        Initialize the scraper.

        Args:
            url: Target URL to scrape
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.url = self._normalize_url(url)
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.response: Optional[requests.Response] = None
        self.soup: Optional[BeautifulSoup] = None
        self.html: str = ""
        self.http_headers: Dict[str, str] = {}

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Ensure URL has a scheme (https://)."""
        if not url.startswith(("http://", "https://")):
            return f"https://{url}"
        return url

    def fetch(self) -> bool:
        """
        Fetch the webpage content.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self.response = requests.get(
                self.url,
                headers=self.DEFAULT_HEADERS,
                timeout=self.timeout,
                allow_redirects=True,
                verify=self.verify_ssl,
            )
            self.response.raise_for_status()
            self._parse_response()
            return True

        except requests.exceptions.SSLError:
            # Retry without SSL verification
            return self._retry_without_ssl()

        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {e}")
            return False

    def _retry_without_ssl(self) -> bool:
        """Retry the request with SSL verification disabled."""
        try:
            self.response = requests.get(
                self.url,
                headers=self.DEFAULT_HEADERS,
                timeout=self.timeout,
                allow_redirects=True,
                verify=False,
            )
            self.response.raise_for_status()
            self._parse_response()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL (SSL disabled): {e}")
            return False

    def _parse_response(self):
        """Parse the response content."""
        if self.response is None:
            return
        self.html = self.response.text
        self.soup = BeautifulSoup(self.html, "html.parser")
        self.http_headers = dict(self.response.headers)

    def get_domain(self) -> str:
        """Extract the domain from the URL."""
        parsed = urlparse(self.url)
        return parsed.netloc

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
