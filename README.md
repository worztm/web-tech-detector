Web Technology Detector
======================

A Python tool to detect technologies used by any website and generate beautiful HTML reports with a modern shadcn/ui-inspired design.


Overview
--------

Web Technology Detector analyzes websites to identify the frameworks, libraries, CMS, analytics tools, hosting providers, and other technologies they use. It then generates a clean, dark-mode HTML report that you can open in any browser.


Features
--------

- Detects 50+ technologies across multiple categories
- Generates beautiful shadcn/ui-inspired dark mode reports
- Fast analysis with pattern matching
- Analyzes HTML, meta tags, and HTTP headers
- Responsive design that works on all devices
- Works as both a CLI tool and importable library


Technologies Detected
---------------------

JavaScript Frameworks
  - React, Vue.js, Angular, Svelte, Solid.js, Preact
  - Alpine.js, Stimulus, jQuery, Backbone.js, Ember.js

CSS Frameworks
  - Tailwind CSS, Bootstrap, Bulma, Foundation
  - Material Design, Materialize CSS, Ant Design, shadcn/ui

Static Site Generators
  - Next.js, Nuxt.js, Gatsby, Hugo, Jekyll, Astro, Vite, Remix

CMS Platforms
  - WordPress, Drupal, Joomla, Shopify, Wix, Squarespace
  - Ghost, Contentful, Webflow, TYPO3

E-commerce
  - Shopify, WooCommerce, BigCommerce, Magento, OpenCart

Analytics
  - Google Analytics, Google Tag Manager, Hotjar, Mixpanel
  - Segment, Plausible, Matomo, Amplitude, Heap, FullStory
  - Facebook Pixel, Microsoft Clarity

Web Servers
  - Nginx, Apache, LiteSpeed, IIS, Caddy

Programming Languages
  - PHP, Python, Ruby, Node.js, Java, .NET

Hosting and CDN
  - Cloudflare, AWS, Vercel, Netlify, Google Cloud
  - Azure, Heroku, GitHub Pages, Fastly, Akamai

Libraries
  - Lodash, Moment.js, GSAP, Three.js, D3.js, Chart.js
  - Anime.js, Swiper, Font Awesome, Google Fonts

Security
  - reCAPTCHA, hCaptcha, Cloudflare Turnstile


Installation
------------

Clone the repository:

    git clone https://github.com/yourusername/web-tech-detector.git
    cd web-tech-detector

Install dependencies:

    pip install -r requirements.txt

Or install as a package:

    pip install -e .


Usage
-----

Command Line
^^^^^^^^^^^^

Basic usage:

    python -m web_tech_detector https://example.com

After installing the package:

    tech-detector https://github.com

With options:

    tech-detector https://wordpress.com --output ./reports
    tech-detector https://shopify.com --no-open

Interactive Mode
^^^^^^^^^^^^^^^^

    python -m web_tech_detector

Then enter the URL when prompted.

As a Library
^^^^^^^^^^^^

    from web_tech_detector.scraper import WebScraper
    from web_tech_detector.detector import TechnologyDetector
    from web_tech_detector.report import ReportGenerator

    # Fetch the website
    scraper = WebScraper("https://example.com")
    scraper.fetch()

    # Detect technologies
    detector = TechnologyDetector()
    technologies = detector.detect_all(
        html=scraper.html,
        soup=scraper.soup,
        http_headers=scraper.http_headers
    )

    # Generate report
    results = {
        "url": scraper.url,
        "technologies": technologies,
    }
    generator = ReportGenerator(results)
    generator.save("./output")


CLI Options
-----------

    usage: tech-detector [-h] [-o OUTPUT] [--no-open] [-v] [url]

    positional arguments:
      url                   URL of the website to analyze

    optional arguments:
      -h, --help            show this help message and exit
      -o, --output OUTPUT   Output directory for the report
      --no-open             Don't auto-open the report in browser
      -v, --version         show program's version number and exit


Project Structure
-----------------

    web-tech-detector/
    |-- README.md
    |-- LICENSE
    |-- requirements.txt
    |-- setup.py
    |-- .gitignore
    |
    |-- web_tech_detector/
    |   |-- __init__.py
    |   |-- __main__.py
    |   |-- cli.py
    |   |-- detector.py
    |   |-- report.py
    |   |-- scraper.py
    |
    |-- examples/
        |-- sample_usage.py

File Descriptions
^^^^^^^^^^^^^^^^^

    __init__.py     Package initialization and version info
    __main__.py     Entry point for python -m command
    cli.py          Command-line interface with argument parsing
    detector.py     Technology detection logic and patterns
    report.py       HTML report generator with shadcn/ui design
    scraper.py      Web scraping and HTTP request handling


Report Features
---------------

The generated HTML reports include:

- Dark mode design by default
- Statistics dashboard with key metrics
- Meta information extracted from the page
- Server details from HTTP headers
- Technology badges color-coded by category
- JSON-LD structured data when available
- Fully responsive layout for mobile and desktop
- Clean typography using Inter and JetBrains Mono fonts


Contributing
------------

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m "Add amazing feature")
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request


Ideas for Contributions
^^^^^^^^^^^^^^^^^^^^^^^

- Add more technology detection patterns
- Create alternative report themes
- Add unit tests
- Add API endpoint support
- Improve detection accuracy


License
-------

This project is licensed under the MIT License. See the LICENSE file for details.


Acknowledgments
---------------

- BeautifulSoup - HTML parsing library
- Requests - HTTP library for Python
- shadcn/ui - Design inspiration for the reports