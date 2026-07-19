<div align="center">

Web Technology Detector

Detect 100+ web technologies with beautiful shadcn/ui-inspired dark theme reports.

[Installation](#installation)  [Usage](#usage)  [Features](#features)  [Contributing](#contributing)

</div>

A Python tool that looks at any website and tells you what it's built with. Frameworks, CMS platforms, analytics tools, hosting providers, databases, CDNs. It generates stunning interactive HTML reports with search, filtering, confidence scoring, and version extraction. Everything you need to understand a site's tech stack in seconds.

<br>

Why this exists

When you land on a website and wonder what powers it, you usually have to dig through the source code, check HTTP headers, inspect scripts. This tool does all of that for you. Point it at a URL, and it returns a complete breakdown of every technology it can identify, along with a beautiful report you can open in your browser, share with your team, or save for later.

<br>

Installation

Clone the repo and install the dependencies.

<pre>
git clone https://github.com/waleedmasud/web-tech-detector.git
cd web-tech-detector
pip install -r requirements.txt
</pre>

Or install it as a package.

<pre>
pip install -e .
</pre>

<br>

Quick start

Point the tool at any website and it will generate a report.

<pre>
python -m web_tech_detector https://example.com
</pre>

If you installed the package, you can use the shorter command.

<pre>
tech-detector https://github.com
</pre>

The tool will open the report in your default browser automatically. If you prefer to keep the browser closed, pass the no-open flag.

<pre>
tech-detector https://shopify.com --no-open
</pre>

<br>

All command line options

The tool accepts a range of flags to customize what it does.

<pre>
tech-detector [url] [options]

Options:

  -o, --output DIRECTORY    Where to save the report. Defaults to your
                            current directory.

  --no-open                 Don't open the report in your browser after
                            generation.

  --json                    Export the raw detection data as a JSON file
                            alongside the HTML report.

  -v, --verbose             Show detailed output while the tool is running,
                            including redirect chains and timing information.

  --timeout SECONDS         How long to wait for the page to load.
                            Default is 30 seconds.

  --no-redirect             Don't follow HTTP redirects. Useful if you want
                            to inspect the first response only.

  --check-robots            Fetch and include the site's robots.txt in the
                            report.

  --check-sitemap           Look for a sitemap.xml and include it in the
                            report.

  --no-social               Skip social media meta tag detection.
</pre>

<br>

Using it as a Python library

You can import the tool into your own Python projects and use it programmatically.

The simplest way.

<pre>
from web_tech_detector import analyze_url

report_path = analyze_url("https://example.com")
</pre>

If you want more control over each step, you can use the individual components.

<pre>
from web_tech_detector import WebScraper, TechnologyDetector, ReportGenerator
from datetime import datetime

scraper = WebScraper("https://example.com")
scraper.fetch()

detector = TechnologyDetector()
technologies = detector.detect_all(scraper.html, scraper.soup, scraper.http_headers)
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

results = {
    "url": scraper.url,
    "technologies": technologies,
    "meta_info": meta_info,
    "json_ld": json_ld,
    "server_info": server_info,
    "performance": performance,
    "social_meta": social_meta,
    "script_analysis": script_analysis,
    "link_analysis": link_analysis,
    "cookie_findings": cookie_findings,
    "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}

generator = ReportGenerator(results)
report_path = generator.save("./output")
</pre>

<br>

What it detects

The tool recognizes over 100 technologies grouped into the following categories.

JavaScript Frameworks

React, Vue.js, Angular, Svelte, Solid, Preact, Alpine.js, HTMX, Lit, jQuery, Backbone.js, Ember.js, MooTools, Dojo, Stimulus, Petite Vue.

CSS Frameworks and Libraries

Tailwind CSS, Bootstrap, Bulma, Foundation, Materialize CSS, Ant Design, Chakra UI, Radix UI, shadcn/ui, UnoCSS, Open Props, Pico CSS, Windi CSS, Emotion, Styled Components.

Static Site Generators and Bundlers

Next.js, Nuxt.js, Gatsby, Hugo, Jekyll, Astro, Vite, Remix, Webpack, Parcel, Rollup, ESBuild, SvelteKit.

CMS Platforms

WordPress, Drupal, Joomla, Wix, Squarespace, Ghost, Contentful, Webflow, TYPO3, Strapi, Sanity, Umbraco, Craft CMS.

E-commerce

Shopify, WooCommerce, BigCommerce, Magento, OpenCart, PrestaShop, Squarespace Commerce, Ecwid, Stripe, Snipcart, Gumroad, Lemon Squeezy.

Analytics and Marketing

Google Analytics, GA4, Google Tag Manager, Facebook Pixel, Hotjar, Mixpanel, Segment, Plausible, Matomo, Amplitude, Heap, FullStory, Microsoft Clarity, LinkedIn Insight Tag, Twitter Pixel, Reddit Pixel, HubSpot, Intercom, Crisp Chat, Tidio, Drift, Mouseflow, Crazy Egg, VWO, Optimizely, Google Ads.

Web Servers

Nginx, Apache, LiteSpeed, IIS, Caddy, Cloudflare Server, OpenResty, Tomcat.

Programming Languages and Runtimes

PHP, Python, Ruby, Node.js, .NET, Java, Go, Rust, Django, Flask, Ruby on Rails, Express, FastAPI, Deno, Bun.

Hosting and CDN

Cloudflare, AWS, Vercel, Netlify, Google Cloud, Azure, Heroku, GitHub Pages, GitLab Pages, Cloudflare Pages, Railway, Render, Fastly, Akamai, KeyCDN, CloudFront, bunny.net, jsDelivr, unpkg, cdnjs.

UI Libraries and Components

Material UI, Radix UI, Headless UI, Framer Motion, GSAP, Three.js, D3.js, Chart.js, ECharts, Anime.js, Swiper, React Router, React Query, Redux, Zustand, Pinia, Vuex, Prism.js, Highlight.js, AOS, Lodash, Moment.js, Day.js, date-fns, Axios, Socket.io, Font Awesome, Google Fonts, Adobe Fonts, Lucide Icons, Heroicons.

Security

reCAPTCHA, hCaptcha, Cloudflare Turnstile, CSP, HSTS, CORS, Sucuri, Wordfence, ModSecurity.

Databases

MySQL, PostgreSQL, MongoDB, Redis, Elasticsearch, Firebase, Supabase, SQLite, Prisma.

DevOps and CI/CD

Docker, Kubernetes, GitHub Actions, CircleCI, Travis CI, Jenkins, Sentry, Datadog, New Relic.

Features and Standards

Schema.org, Open Graph, Twitter Cards, PWA, GraphQL, REST API, Lazy Loading, Preload, Microdata, RSS Feed, Sitemap, Robots.txt, Meta Viewport, CSS Custom Properties, HTTP/2, HTTP/3.

<br>

Smart detection features

The tool doesn't just match technology names. It does a lot more under the hood.

Version extraction. When it detects a library or framework, it tries to figure out which version is running. It extracts version numbers from script filenames, URL patterns, meta tags, and HTTP headers.

Confidence scoring. Every detection gets a confidence rating: high, medium, or low. High confidence means the tool found multiple strong signals. Low confidence means only a weak pattern matched. The report shows this visually so you know which results are reliable.

WordPress plugin and theme extraction. For WordPress sites, the tool scans the HTML for references to active plugins and themes, listing them all out in the report with expandable details.

Cookie analysis. The tool examines cookies set by the site and uses them to identify backend technologies. A PHPSESSID cookie suggests PHP. A csrftoken cookie suggests Django. An ASP.NET SessionId cookie suggests .NET. And so on.

Performance metrics. The report includes page size, response time, compression method, and counts of scripts, stylesheets, and images.

Social media meta detection. It extracts Open Graph tags and Twitter Card metadata so you can see how the site appears when shared on social platforms.

Script analysis. The tool counts inline versus external scripts, identifies ES modules, and notes which scripts are loaded with async or defer.

Link analysis. It categorizes links as internal or external and discovers any API endpoints referenced in anchor tags.

<br>

What the report looks like

The generated HTML report is designed to feel like a modern dashboard, not a boring document. It uses a dark theme inspired by shadcn/ui with glassmorphism cards, gradient accents, and subtle animated background orbs that add depth without being distracting.

Every page includes a sticky header with the tool name and version badge. Below that, a hero card shows the website name, URL, and HTTP status code with a green dot if everything is healthy.

A stats dashboard at the top shows four key numbers: how many technologies were detected, how many categories they span, the HTTP status code, and how many data sources contributed to the analysis.

There is an interactive search bar that filters technologies in real time as you type. It comes with suggestion chips for common technologies like React, WordPress, Cloudflare, and Shopify.

All detected technologies appear as color-coded pills in a badge grid at the top of the report, then get detailed sections below organized by category. Each technology row shows its name, detected version if available, confidence indicator with three visual bars, and a confidence label with a colored dot.

For WordPress sites, each detected plugin or theme shows a toggle button that expands to reveal the full list of items found.

JSON-LD structured data appears in an accordion. You can click each item to expand and view the full JSON payload.

The report is fully responsive and works on phones, tablets, and desktops.

<br>

Project structure

<pre>
web-tech-detector/
  README.md
  LICENSE
  requirements.txt
  setup.py
  web_tech_detector/
    __init__.py       Package exports and version info
    __main__.py       Entry point for python -m
    cli.py            Command line interface
    detector.py       Detection patterns and logic
    report.py         HTML report generator
    scraper.py        Web scraping and HTTP
  examples/
    sample_usage.py   Library usage examples
    output/           Generated reports land here
</pre>

<br>

Contributing

This project is open source and contributions are welcome. If you want to add detection patterns for a technology that is missing, improve version extraction accuracy, add alternative report themes, write unit tests, or set up an API endpoint for web service deployment, go ahead and open a pull request.

The codebase is small and easy to navigate. The detection patterns live in a single dictionary in detector.py. Adding a new technology means adding a few regex patterns to the right category. The report template is in report.py with inline CSS and JavaScript, so changes to the design are self-contained.

If you find a bug or have an idea for a new feature, open an issue first so we can discuss it before you write code.

<br>

License

This project is licensed under the MIT License. You can use it, modify it, and distribute it freely. See the LICENSE file for the full text.

<br>

Built with

BeautifulSoup for HTML parsing. Requests for HTTP. shadcn/ui for design inspiration. Inter and JetBrains Mono for typography.
