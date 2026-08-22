"""
HTML report generator module - Creates beautiful shadcn/ui-inspired dark theme reports.
Features glassmorphism cards, gradient accents, tech badges with versions,
search/filter, accordion for JSON-LD, performance metrics, and responsive design.
"""

import os
import json
import html as html_module
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from string import Template


# Category icons (emoji + SVG)
CATEGORY_ICONS: Dict[str, str] = {
    "JavaScript Frameworks": "⚡",
    "CSS Frameworks & Libraries": "🎨",
    "Static Site Generators & Bundlers": "🚀",
    "CMS": "📝",
    "E-commerce": "🛒",
    "Analytics & Marketing": "📊",
    "Web Servers": "🖥️",
    "Programming Languages & Runtimes": "💻",
    "Hosting & CDN": "☁️",
    "UI Libraries & Components": "📚",
    "Security": "🔒",
    "Features & Standards": "✨",
    "Databases": "🗄️",
    "DevOps & CI/CD": "🔄",
    "Server Headers": "📡",
}

# Category accent colors (HSL for CSS)
CATEGORY_HSL: Dict[str, str] = {
    "JavaScript Frameworks": "217, 91%, 60%",       # blue
    "CSS Frameworks & Libraries": "271, 81%, 56%",   # purple
    "Static Site Generators & Bundlers": "330, 81%, 60%",  # pink
    "CMS": "24, 95%, 53%",                            # orange
    "E-commerce": "142, 71%, 45%",                    # green
    "Analytics & Marketing": "48, 96%, 53%",          # amber
    "Web Servers": "0, 84%, 60%",                     # red
    "Programming Languages & Runtimes": "187, 85%, 53%",  # cyan
    "Hosting & CDN": "226, 70%, 55%",                 # indigo
    "UI Libraries & Components": "160, 84%, 39%",     # emerald
    "Security": "38, 92%, 50%",                       # amber/yellow
    "Features & Standards": "262, 83%, 58%",          # violet
    "Databases": "199, 89%, 48%",                     # sky
    "DevOps & CI/CD": "334, 77%, 55%",                # rose
    "Server Headers": "215, 16%, 47%",                # slate
}


class ReportGenerator:
    """Generates HTML reports with shadcn/ui-inspired dark theme design."""

    def __init__(self, results: Dict):
        """
        Initialize the report generator.

        Args:
            results: Detection results dictionary
        """
        self.results = results
        self.url = results.get("url", "")
        self.title = results.get("title", "Unknown Website")
        self.domain = results.get("domain", "")

    def generate(self) -> str:
        """Generate the complete HTML report."""
        html_techs = self.results.get("technologies", {})
        meta_techs = self.results.get("meta_info", {})
        server_info = self.results.get("server_info", {})
        json_ld = self.results.get("json_ld", [])
        performance = self.results.get("performance", {})
        social_meta = self.results.get("social_meta", {})
        script_analysis = self.results.get("script_analysis", {})
        link_analysis = self.results.get("link_analysis", {})

        # Count totals
        total_count = sum(len(techs) for techs in html_techs.values())
        total_count += len(meta_techs) + len(server_info)
        total_categories = len([c for c, t in html_techs.items() if t])

        return self._build_html(
            total_count=total_count,
            total_categories=total_categories,
            status_code=self.results.get("status_code", "N/A"),
            json_ld_count=len(json_ld),
            meta_techs=meta_techs,
            server_info=server_info,
            html_techs=html_techs,
            json_ld=json_ld,
            performance=performance,
            social_meta=social_meta,
            script_analysis=script_analysis,
            link_analysis=link_analysis,
            robots=self.results.get("robots"),
            sitemap=self.results.get("sitemap"),
        )

    def save(self, output_path: str, save_json: bool = True) -> str:
        """
        Generate and save the HTML report.

        Args:
            output_path: Directory to save the report
            save_json: Also save a sanitized JSON copy alongside the report.

        Returns:
            Full path to the saved file
        """
        html_content = self.generate()

        output_path = output_path or os.curdir
        os.makedirs(output_path, exist_ok=True)

        # Generate a filesystem-safe filename. Include microseconds to avoid
        # overwriting reports created by rapid successive scans.
        safe_domain = re.sub(r"[^A-Za-z0-9_-]+", "_", self.domain).strip("_") or "unknown"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"tech_report_{safe_domain}_{timestamp}.html"

        full_path = os.path.join(output_path, filename)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        if save_json:
            json_path = os.path.splitext(full_path)[0] + ".json"
            # Clean results for JSON export (remove non-serializable)
            json_results = self._sanitize_for_json(self.results)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_results, f, indent=2, ensure_ascii=False, default=str)

        return full_path

    def _sanitize_for_json(self, obj: Any) -> Any:
        """Recursively sanitize objects for JSON serialization."""
        if isinstance(obj, dict):
            return {k: self._sanitize_for_json(v) for k, v in obj.items() if not k.startswith("_")}
        elif isinstance(obj, list):
            return [self._sanitize_for_json(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        else:
            return str(obj)

    def _escape(self, text) -> str:
        """Escape HTML special characters."""
        if text is None:
            return ""
        text = str(text)
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def _build_html(
        self,
        total_count: int,
        total_categories: int,
        status_code: int,
        json_ld_count: int,
        meta_techs: Dict,
        server_info: Dict,
        html_techs: Dict[str, list],
        json_ld: List[Dict],
        performance: Dict,
        social_meta: Dict,
        script_analysis: Dict,
        link_analysis: Dict,
        robots: Optional[str] = None,
        sitemap: Optional[str] = None,
    ) -> str:
        """Build the complete HTML document."""

        # Build sections
        stats_section = self._build_stats_section(total_count, total_categories, status_code, json_ld_count)
        distribution_section = self._build_distribution_section(html_techs)
        search_section = self._build_search_section(html_techs)
        meta_section = self._build_meta_section(meta_techs)
        server_section = self._build_server_section(server_info)
        performance_section = self._build_performance_section(performance)
        tech_grid = self._build_tech_grid(html_techs)
        tech_sections = self._build_tech_sections(html_techs)
        json_ld_section = self._build_json_ld_section(json_ld)
        social_section = self._build_social_section(social_meta)
        script_section = self._build_script_analysis_section(script_analysis)
        link_section = self._build_link_analysis_section(link_analysis)
        cookie_section = self._build_cookie_section(self.results.get("cookie_findings", []))
        robots_section = self._build_robots_section(robots)

        return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tech Report — {self._escape(self.title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        {self._get_styles()}
    </style>
</head>
<body>
    <div class="scroll-progress" id="scrollProgress"></div>
    <div class="app">
        <!-- Animated background orbs -->
        <div class="orbs">
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="orb orb-3"></div>
        </div>

        <!-- Header -->
        <header class="header">
            <div class="container">
                <div class="header-inner">
                    <div class="header-left">
                        <div class="logo">
                            <svg class="logo-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="11" cy="11" r="8"></circle>
                                <path d="m21 21-4.3-4.3"></path>
                            </svg>
                            <div class="logo-text">
                                <h1>Tech Detector</h1>
                                <span>Web Technology Analyzer</span>
                            </div>
                        </div>
                    </div>
                    <div class="header-right">
                        <span class="badge badge-primary pulse">LIVE</span>
                        <span class="badge badge-ghost v">{self.results.get('detected_at', '').split(' ')[0] if self.results.get('detected_at') else ''}</span>
                    </div>
                </div>
            </div>
        </header>

        <main class="main container">
            <!-- Hero / URL Card -->
            <section class="hero-card glass">
                <div class="hero-bg"></div>
                <div class="hero-content">
                    <div class="hero-icon-wrap">
                        <img class="hero-favicon" src="https://www.google.com/s2/favicons?domain={self._escape(self.domain)}&sz=128" alt="" loading="lazy"
                             onerror="this.classList.add('is-hidden'); this.nextElementSibling.classList.remove('is-hidden');">
                        <span class="hero-icon is-hidden">🌐</span>
                    </div>
                    <div class="hero-text">
                        <h2 class="hero-title">{self._escape(self.title)}</h2>
                        <div class="hero-url">
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                            </svg>
                            <span>{self._escape(self.url)}</span>
                        </div>
                    </div>
                    <div class="hero-status">
                        <div class="status-dot {'status-success' if (self.results.get('status_code') or 0) < 300 else 'status-warning' if (self.results.get('status_code') or 0) < 400 else 'status-error'}"></div>
                        <span>{self.results.get('status_code', 'N/A')}</span>
                    </div>
                </div>
            </section>

            <!-- Stats Grid -->
            {stats_section}

            <!-- Category Distribution -->
            {distribution_section}

            <!-- Search / Filter -->
            {search_section}

            <!-- Technology Badge Grid (visual overview) -->
            {tech_grid}

            <!-- Meta Information -->
            {meta_section}

            <!-- Server Information -->
            {server_section}

            <!-- Performance Metrics -->
            {performance_section}

            <!-- Social Meta -->
            {social_section}

            <!-- Script Analysis -->
            {script_section}

            <!-- Link Analysis -->
            {link_section}

            <!-- Cookie Findings -->
            {cookie_section}

            <!-- robots.txt -->
            {robots_section}

            <!-- Detailed Technology Sections -->
            {tech_sections}

            <!-- JSON-LD -->
            {json_ld_section}
        </main>

        <!-- Back to top -->
        <button class="back-to-top" id="backToTop" aria-label="Back to top">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg>
        </button>

        <!-- Footer -->
        <footer class="footer">
            <div class="container">
                <div class="footer-inner">
                    <p>Generated on {self.results.get('detected_at', 'N/A')}</p>
                    <div class="footer-dot"></div>
                    <p>Web Technology Detector v1.0</p>
                </div>
            </div>
        </footer>
    </div>

    <div class="toast" id="toast"></div>

    <script id="report-data" type="application/json">{self._safe_json_export()}</script>

    <script>
        {self._get_scripts()}
    </script>
</body>
</html>"""

    def _build_stats_section(self, total_count: int, total_categories: int, status_code: int, json_ld_count: int) -> str:
        """Build the statistics cards section with glassmorphism."""
        stats = [
            {"label": "Technologies", "value": str(total_count), "icon": "🔬", "gradient": "#3b82f6, #8b5cf6"},
            {"label": "Categories", "value": str(total_categories), "icon": "📂", "gradient": "#10b981, #06b6d4"},
            {"label": "Status Code", "value": str(status_code), "icon": "📡", "gradient": "#f59e0b, #ef4444"},
            {"label": "Data Sources", "value": str(json_ld_count + 1), "icon": "📋", "gradient": "#ec4899, #8b5cf6"},
        ]

        cards = ""
        for stat in stats:
            cards += f"""
            <div class="stat-card glass card-hover" data-stat="{stat['label'].lower().replace(' ', '-')}">
                <div class="stat-icon-wrap" style="background: linear-gradient(135deg, {stat['gradient']});">
                    <span>{stat['icon']}</span>
                </div>
                <div class="stat-info">
                    <span class="stat-value count-up" data-target="{stat['value']}">{stat['value']}</span>
                    <span class="stat-label">{stat['label']}</span>
                </div>
            </div>"""

        return f"""
        <section class="stats-grid">
            {cards}
        </section>"""

    def _build_search_section(self, html_techs: Dict[str, list]) -> str:
        """Build the search/filter section for technologies."""
        chips = ""
        for category, techs in sorted(html_techs.items()):
            if not techs:
                continue
            icon = CATEGORY_ICONS.get(category, "📦")
            chips += f"""
                <button class="cat-chip" data-cat="{self._escape(category.lower())}">
                    <span>{icon}</span>
                    {self._escape(category)}
                    <span class="cat-chip-count">{len(techs)}</span>
                </button>"""
        chips_block = f"""
            <div class="cat-chips" id="catChips">{chips}
            </div>""" if chips else ""
        return f"""
        <section class="search-section glass">
            <div class="search-inner">
                <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.3-4.3"></path>
                </svg>
                <input type="text" class="search-input" id="techSearch" placeholder="Search technologies, frameworks, tools..." autocomplete="off">
                <button class="search-clear" id="clearSearch" title="Clear filter">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            {chips_block}
            <div class="search-hints">
                <span class="legend"><span class="tech-pill-indicator confidence-high"></span> High</span>
                <span class="legend"><span class="tech-pill-indicator confidence-medium"></span> Medium</span>
                <span class="legend"><span class="tech-pill-indicator confidence-low"></span> Low</span>
                <span class="legend-divider"></span>
                <span>Try: <button class="hint-chip" data-hint="react">React</button></span>
                <span><button class="hint-chip" data-hint="wordpress">WordPress</button></span>
                <span><button class="hint-chip" data-hint="cloudflare">Cloudflare</button></span>
                <span><button class="hint-chip" data-hint="shopify">Shopify</button></span>
            </div>
        </section>"""

    def _safe_json_export(self) -> str:
        """Serialize results for embedding in a JSON script tag."""
        payload = json.dumps(self._sanitize_for_json(self.results), indent=2, ensure_ascii=False, default=str)
        # Prevent </script> breakouts inside the embedded JSON block
        return payload.replace("</", "<" + chr(92) + "/")

    def _build_distribution_section(self, html_techs: Dict[str, list]) -> str:
        """Build a horizontal bar chart showing technologies per category."""
        if not html_techs:
            return ""
        total = sum(len(t) for t in html_techs.values())
        max_count = max(len(t) for t in html_techs.values()) or 1
        bars = ""
        for category, techs in sorted(html_techs.items(), key=lambda kv: -len(kv[1])):
            if not techs:
                continue
            icon = CATEGORY_ICONS.get(category, "📦")
            hsl = CATEGORY_HSL.get(category, "215, 16%, 47%")
            pct_width = round(len(techs) / max_count * 100, 1)
            bars += f"""
                <div class="dist-row">
                    <div class="dist-label">{icon} {self._escape(category)}</div>
                    <div class="dist-track">
                        <div class="dist-fill" style="width: {pct_width}%; background: linear-gradient(90deg, hsl({hsl} / 0.55), hsl({hsl}));"></div>
                    </div>
                    <div class="dist-count">{len(techs)}</div>
                </div>"""
        return f"""
        <section class="card glass">
            <div class="section-header">
                <h3 class="section-title">
                    <span class="section-icon">📊</span>
                    Category Distribution
                </h3>
                <span class="badge badge-ghost">{total} total</span>
            </div>
            <div class="dist-chart">
                {bars}
            </div>
        </section>"""

    def _build_tech_grid(self, html_techs: Dict[str, list]) -> str:
        """Build a visual badge grid of all detected technologies."""
        if not html_techs:
            return ""

        all_techs = []
        for category, techs in html_techs.items():
            for tech in techs:
                all_techs.append({
                    "name": tech.get("name", tech) if isinstance(tech, dict) else tech,
                    "version": tech.get("version") if isinstance(tech, dict) else None,
                    "confidence": tech.get("confidence", "low") if isinstance(tech, dict) else "low",
                    "category": category,
                })

        if not all_techs:
            return ""

        badges = ""
        for tech in sorted(all_techs, key=lambda x: (0 if x["confidence"] == "high" else 1 if x["confidence"] == "medium" else 2, x["name"])):
            version_str = f" <span class='tech-version'>{tech['version']}</span>" if tech.get("version") else ""
            badges += f"""
                <span class="tech-pill" data-tech="{self._escape(tech['name'].lower())}" data-category="{self._escape(tech['category'].lower())}" data-confidence="{tech['confidence']}" onclick="filterByTech(this.dataset.tech)">
                    <span class="tech-pill-indicator confidence-{tech['confidence']}"></span>
                    <span class="tech-pill-name">{self._escape(tech['name'])}{version_str}</span>
                    <span class="tech-pill-confidence">{tech['confidence']}</span>
                </span>"""

        return f"""
        <section class="tech-grid-section glass" id="techGrid">
            <div class="section-header">
                <h3 class="section-title">
                    <span class="section-icon">🎯</span>
                    Detected Technologies
                    <span class="section-count">{len(all_techs)}</span>
                </h3>
                <div class="section-actions">
                    <button class="btn btn-ghost btn-sm" id="downloadJson">⬇ JSON</button>
                    <button class="btn btn-ghost btn-sm" id="copyAll">Copy List</button>
                    <button class="btn btn-ghost btn-sm" id="expandAll">Show Details</button>
                </div>
            </div>
            <div class="tech-pills" id="techPills">
                {badges}
            </div>
            <div class="tech-grid-empty" id="techGridEmpty" style="display:none">
                <span class="empty-icon">🔍</span>
                <p>No technologies match your search</p>
                <button class="btn btn-outline btn-sm" id="resetSearch">Reset Filter</button>
            </div>
        </section>"""

    def _build_meta_section(self, meta_techs: Dict) -> str:
        """Build the meta information section."""
        if not meta_techs:
            return ""

        items = ""
        for key, value in meta_techs.items():
            items += f"""
            <div class="info-row">
                <span class="info-key">{self._escape(key)}</span>
                <span class="info-value">{self._escape(value)}</span>
            </div>"""

        return f"""
        <section class="card glass">
            <div class="section-header">
                <h3 class="section-title">
                    <span class="section-icon">🏷️</span>
                    Meta Information
                </h3>
            </div>
            <div class="info-grid">
                {items}
            </div>
        </section>"""

    def _build_server_section(self, server_info: Dict) -> str:
        """Build the server information section."""
        if not server_info:
            return ""

        items = ""
        for key, value in server_info.items():
            items += f"""
            <div class="info-row">
                <span class="info-key">{self._escape(key)}</span>
                <span class="info-value code">{self._escape(value)}</span>
            </div>"""

        return f"""
        <section class="card glass">
            <div class="section-header">
                <h3 class="section-title">
                    <span class="section-icon">🖥️</span>
                    Server Information
                </h3>
            </div>
            <div class="info-grid">
                {items}
            </div>
        </section>"""

    def _build_performance_section(self, performance: Dict) -> str:
        """Build the performance metrics section."""
        if not performance:
            return ""

        metrics = []
        if performance.get("response_time_ms"):
            time_val = performance["response_time_ms"]
            color = "text-emerald-400" if time_val < 500 else "text-amber-400" if time_val < 1500 else "text-red-400"
            metrics.append(("Response Time", f"{time_val}ms", color))

        if performance.get("page_size_formatted"):
            metrics.append(("Page Size", performance["page_size_formatted"], "text-blue-400"))

        if performance.get("compression") and performance["compression"] != "None":
            metrics.append(("Compression", performance["compression"].upper(), "text-purple-400"))

        if performance.get("script_count"):
            metrics.append(("Scripts", str(performance["script_count"]), "text-amber-400"))

        if performance.get("stylesheet_count"):
            metrics.append(("Stylesheets", str(performance["stylesheet_count"]), "text-pink-400"))

        if performance.get("image_count"):
            metrics.append(("Images", str(performance["image_count"]), "text-green-400"))

        if not metrics:
            return ""

        items = ""
        for label, value, color in metrics:
            items += f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value {color}">{value}</div>
            </div>"""

        return f"""
        <section class="card glass">
            <div class="section-header">
                <h3 class="section-title">
                    <span class="section-icon">📈</span>
                    Performance & Metrics
                </h3>
            </div>
            <div class="metrics-grid">
                {items}
            </div>
        </section>"""

    def _build_social_section(self, social_meta: Dict) -> str:
        """Build social media meta section."""
        if not social_meta:
            return ""

        sections_html = ""
        for platform, tags in social_meta.items():
            if not tags:
                continue
            platform_label = platform.replace("_", " ").title()
            items = ""
            for key, value in list(tags.items())[:8]:
                items += f"""
                <div class="info-row">
                    <span class="info-key">{self._escape(key)}</span>
                    <span class="info-value">{self._escape(value)}</span>
                </div>"""
            if items:
                sections_html += f"""
                <div class="social-platform">
                    <h4 class="social-title">{platform_label}</h4>
                    <div class="info-grid">{items}</div>
                </div>"""

        if not sections_html:
            return ""

        return f"""
        <section class="card glass">
            <div class="section-header">
                <h3 class="section-title">
                    <span class="section-icon">📱</span>
                    Social Media & Sharing
                </h3>
            </div>
            {sections_html}
        </section>"""

    def _build_script_analysis_section(self, script_analysis: Dict) -> str:
        """Build script analysis section."""
        if not script_analysis:
            return ""

        items = ""
        labels_map = {
            "total_scripts": ("Total Scripts", "text-blue-400"),
            "inline_scripts": ("Inline Scripts", "text-purple-400"),
            "external_scripts": ("External Scripts", "text-amber-400"),
            "module_scripts": ("ES Modules", "text-emerald-400"),
            "deferred_scripts": ("Deferred", "text-sky-400"),
            "async_scripts": ("Async", "text-pink-400"),
        }

        for key, (label, color) in labels_map.items():
            val = script_analysis.get(key, 0)
            if val is not None:
                items += f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value {color}">{val}</div>
                </div>"""

        return f"""
        <section class="card glass">
            <div class="section-header">
                <h3 class="section-title">
                    <span class="section-icon">📜</span>
                    Script Analysis
                </h3>
            </div>
            <div class="metrics-grid">
                {items}
            </div>
        </section>"""

    def _build_link_analysis_section(self, link_analysis: Dict) -> str:
        """Build link analysis section."""
        if not link_analysis:
            return ""

        items = ""

        if link_analysis.get("internal_links") is not None:
            items += f"""
            <div class="metric-card">
                <div class="metric-label">Internal Links</div>
                <div class="metric-value text-emerald-400">{link_analysis['internal_links']}</div>
            </div>"""

        if link_analysis.get("external_links") is not None:
            items += f"""
            <div class="metric-card">
                <div class="metric-label">External Links</div>
                <div class="metric-value text-blue-400">{link_analysis['external_links']}</div>
            </div>"""

        if link_analysis.get("has_mailto"):
            items += f"""
            <div class="metric-card">
                <div class="metric-label">Email Links</div>
                <div class="metric-value text-purple-400">✓</div>
            </div>"""

        if link_analysis.get("api_endpoints"):
            api_list = "".join(f'<div class="api-item">{self._escape(e)}</div>' for e in link_analysis["api_endpoints"])
            items += f"""
            <div class="metric-card metric-card-wide">
                <div class="metric-label">API Endpoints</div>
                <div class="api-list">{api_list}</div>
            </div>"""

        if not items:
            return ""

        return f"""
        <section class="card glass">
            <div class="section-header">
                <h3 class="section-title">
                    <span class="section-icon">🔗</span>
                    Link Analysis
                </h3>
            </div>
            <div class="metrics-grid">
                {items}
            </div>
        </section>"""

    def _build_cookie_section(self, cookie_findings: List[Dict]) -> str:
        """Build the cookie technology findings section."""
        if not cookie_findings:
            return ""

        rows = ""
        for finding in cookie_findings:
            rows += f"""
            <div class="tech-row">
                <div class="tech-row-info">
                    <span class="tech-row-badge" style="background: hsl(142 71% 45% / 0.15); color: hsl(142 71% 45%); border: 1px solid hsl(142 71% 45% / 0.3);">
                        {self._escape(finding.get('tech', 'Unknown'))}
                    </span>
                    <span class="cookie-name">{self._escape(finding.get('cookie', ''))}</span>
                </div>
                <div class="tech-row-meta">
                    <span class="tech-row-confidence confidence-high">🟢 high</span>
                </div>
            </div>"""

        return f"""
        <section class="card glass">
            <div class="section-header">
                <h3 class="section-title">
                    <span class="section-icon">🍪</span>
                    Cookie Technology Findings
                    <span class="section-count">{len(cookie_findings)}</span>
                </h3>
            </div>
            <div class="tech-list">
                {rows}
            </div>
        </section>"""

    def _build_robots_section(self, robots: Optional[str]) -> str:
        """Build robots.txt section."""
        if not robots:
            return ""

        preview = robots[:500]
        if len(robots) > 500:
            preview += "..."

        return f"""
        <section class="card glass">
            <div class="section-header">
                <h3 class="section-title">
                    <span class="section-icon">🤖</span>
                    robots.txt
                </h3>
            </div>
            <div class="code-block">
                <pre>{self._escape(preview)}</pre>
            </div>
        </section>"""

    def _build_tech_sections(self, html_techs: Dict[str, list]) -> str:
        """Build detailed technology detection sections."""
        sections = ""

        for category, techs in html_techs.items():
            if not techs:
                continue

            icon = CATEGORY_ICONS.get(category, "📦")
            hsl = CATEGORY_HSL.get(category, "215, 16%, 47%")

            rows = ""
            # Determine if any tech has extracted items (plugins/themes)
            has_items = any(isinstance(t, dict) and t.get("items") for t in techs)

            for tech in techs:
                if isinstance(tech, str):
                    # Backward compatibility
                    rows += f"""
                    <div class="tech-row" data-tech-name="{self._escape(tech.lower())}">
                        <div class="tech-row-info">
                            <span class="tech-row-badge" style="background: hsl({hsl})">{self._escape(tech)}</span>
                        </div>
                        <div class="tech-row-meta">
                            <span class="tech-row-version">—</span>
                            <span class="tech-row-confidence confidence-low">low</span>
                        </div>
                    </div>"""
                    continue

                name = tech.get("name", "Unknown")
                version = tech.get("version")
                confidence = tech.get("confidence", "low")
                evidence_count = tech.get("evidence_count", 0)
                items_list = tech.get("items", [])

                version_html = f"<span class='tech-row-version'>v{self._escape(version)}</span>" if version else "<span class='tech-row-version'>—</span>"
                confidence_icon = "🟢" if confidence == "high" else "🟡" if confidence == "medium" else "🟠"

                # Build items expandable if there are extracted items
                items_html = ""
                if items_list:
                    items_html = f"""
                    <div class="tech-items">
                        <button class="tech-items-toggle" onclick="toggleTechItems(this)">
                            <span>{len(items_list)} items</span>
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="6 9 12 15 18 9"></polyline>
                            </svg>
                        </button>
                        <div class="tech-items-list">
                            {''.join(f'<span class="tech-item-chip">{self._escape(item)}</span>' for item in items_list[:20])}
                            {f'<span class="tech-item-chip">... and {len(items_list) - 20} more</span>' if len(items_list) > 20 else ''}
                        </div>
                    </div>"""

                bars = ""
                if confidence == "high":
                    bars = """<div class="confidence-bars"><span class="bar active"></span><span class="bar active"></span><span class="bar active"></span></div>"""
                elif confidence == "medium":
                    bars = """<div class="confidence-bars"><span class="bar active"></span><span class="bar active"></span><span class="bar"></span></div>"""
                else:
                    bars = """<div class="confidence-bars"><span class="bar active"></span><span class="bar"></span><span class="bar"></span></div>"""

                rows += f"""
                <div class="tech-row" data-tech-name="{self._escape(name.lower())}">
                    <div class="tech-row-info">
                        <span class="tech-row-badge" style="background: hsl({hsl} / 0.15); color: hsl({hsl}); border: 1px solid hsl({hsl} / 0.3);">
                            {self._escape(name)}
                        </span>
                        {items_html}
                    </div>
                    <div class="tech-row-meta">
                        {bars}
                        {version_html}
                        <span class="tech-row-confidence confidence-{confidence}">{confidence_icon} {confidence}</span>
                    </div>
                </div>"""

            sections += f"""
            <section class="card glass tech-category" data-category="{self._escape(category.lower())}">
                <div class="section-header">
                    <h3 class="section-title">
                        <span class="section-icon">{icon}</span>
                        {self._escape(category)}
                        <span class="section-count">{len(techs)}</span>
                    </h3>
                </div>
                <div class="tech-list" data-category="{self._escape(category)}">
                    {rows}
                </div>
            </section>"""

        if not sections:
            return """
            <section class="card glass">
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <h3>No Technologies Detected</h3>
                    <p>We couldn't identify any technologies from the HTML source.</p>
                </div>
            </section>"""

        return sections

    def _build_json_ld_section(self, json_ld: List[Dict]) -> str:
        """Build the JSON-LD structured data section with accordion."""
        if not json_ld:
            return ""

        items = ""
        for i, item in enumerate(json_ld):
            formatted = json.dumps(item, indent=2)
            item_id = f"jsonld-{i}"
            # Extract @type if available
            item_type = item.get("@type", f"Item {i + 1}")
            items += f"""
            <div class="accordion-item">
                <button class="accordion-trigger" onclick="toggleAccordion('{item_id}')">
                    <span class="accordion-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="9 18 15 12 9 6"></polyline>
                        </svg>
                    </span>
                    <span class="accordion-label">{self._escape(str(item_type))}</span>
                </button>
                <div class="accordion-content" id="{item_id}">
                    <pre class="code-block">{self._escape(formatted)}</pre>
                </div>
            </div>"""

        return f"""
        <section class="card glass">
            <div class="section-header">
                <h3 class="section-title">
                    <span class="section-icon">📋</span>
                    JSON-LD Structured Data
                    <span class="section-count">{len(json_ld)}</span>
                </h3>
            </div>
            <div class="accordion">
                {items}
            </div>
        </section>"""

    def _get_styles(self) -> str:
        """Return the CSS styles for the report with complete shadcn/ui dark theme."""
        return """
        /* ============================================================
           CSS Variables - shadcn/ui inspired dark theme with glass
           ============================================================ */
        :root {
            --background: 224 71% 4%;
            --foreground: 210 40% 98%;
            --card: 224 71% 4%;
            --card-foreground: 210 40% 98%;
            --primary: 217 91% 60%;
            --primary-foreground: 224 71% 4%;
            --secondary: 215 28% 17%;
            --secondary-foreground: 210 40% 98%;
            --muted: 215 28% 17%;
            --muted-foreground: 218 11% 65%;
            --accent: 215 28% 17%;
            --accent-foreground: 210 40% 98%;
            --destructive: 0 63% 31%;
            --border: 215 28% 17%;
            --ring: 217 91% 60%;
            --radius: 0.75rem;
            --radius-sm: 0.5rem;
            --radius-lg: 1rem;
            --shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
            --glass-bg: hsl(var(--card) / 0.6);
            --glass-border: hsl(var(--border) / 0.4);
            --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* ============================================================
           Base / Reset
           ============================================================ */
        *, *::before, *::after {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: hsl(var(--background));
            color: hsl(var(--foreground));
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            overflow-x: hidden;
        }

        ::selection {
            background: hsl(var(--primary) / 0.3);
            color: hsl(var(--foreground));
        }

        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: hsl(var(--background));
        }
        ::-webkit-scrollbar-thumb {
            background: hsl(var(--muted));
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: hsl(var(--muted-foreground));
        }

        /* ============================================================
           Layout
           ============================================================ */
        .app {
            position: relative;
            min-height: 100vh;
            overflow: hidden;
        }

        /* ============================================================
           Scroll Progress Bar
           ============================================================ */
        .scroll-progress {
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            width: 0%;
            z-index: 200;
            background: linear-gradient(90deg, hsl(217 91% 60%), hsl(271 81% 56%), hsl(330 81% 60%));
            box-shadow: 0 0 12px hsl(217 91% 60% / 0.6);
            border-radius: 0 2px 2px 0;
            transition: width 0.08s linear;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1.5rem;
            position: relative;
            z-index: 1;
        }

        /* ============================================================
           Animated Background Orbs
           ============================================================ */
        .orbs {
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }
        .orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(80px);
            opacity: 0.15;
            animation: orbFloat 20s ease-in-out infinite;
        }
        .orb-1 {
            width: 600px; height: 600px;
            background: hsl(217 91% 60%);
            top: -200px; right: -200px;
            animation-delay: 0s;
        }
        .orb-2 {
            width: 500px; height: 500px;
            background: hsl(271 81% 56%);
            bottom: -150px; left: -150px;
            animation-delay: -7s;
        }
        .orb-3 {
            width: 400px; height: 400px;
            background: hsl(142 71% 45%);
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            animation-delay: -14s;
        }

        @keyframes orbFloat {
            0%, 100% { transform: translate(0, 0) scale(1); }
            25% { transform: translate(50px, -50px) scale(1.1); }
            50% { transform: translate(-30px, 30px) scale(0.9); }
            75% { transform: translate(40px, 20px) scale(1.05); }
        }

        /* ============================================================
           Header
           ============================================================ */
        .header {
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid hsl(var(--border) / 0.4);
            background: hsl(var(--background) / 0.8);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
        }
        .header-inner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.875rem 0;
        }
        .header-left, .header-right {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .logo-icon {
            width: 2rem;
            height: 2rem;
            padding: 0.4rem;
            border-radius: 0.5rem;
            background: hsl(var(--primary));
            color: hsl(var(--primary-foreground));
        }
        .logo-text h1 {
            font-size: 1.125rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            line-height: 1.3;
        }
        .logo-text span {
            font-size: 0.75rem;
            color: hsl(var(--muted-foreground));
            display: block;
        }

        /* ============================================================
           Badges
           ============================================================ */
        .badge {
            display: inline-flex;
            align-items: center;
            border-radius: 9999px;
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 600;
            transition: all 0.2s;
        }
        .badge-primary {
            background: hsl(var(--primary));
            color: hsl(var(--primary-foreground));
        }
        .badge-ghost {
            background: hsl(var(--muted));
            color: hsl(var(--muted-foreground));
        }
        .badge-outline {
            border: 1px solid hsl(var(--border));
            color: hsl(var(--muted-foreground));
        }

        .pulse {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        /* ============================================================
           Glass Card
           ============================================================ */
        .glass {
            background: hsl(var(--card) / 0.5);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid hsl(var(--border) / 0.3);
            border-radius: var(--radius-lg);
            box-shadow: var(--glass-shadow);
        }

        .card {
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .card-hover {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .card-hover:hover {
            transform: translateY(-2px);
            border-color: hsl(var(--primary) / 0.2);
            box-shadow: 0 8px 32px 0 rgba(59, 130, 246, 0.08);
        }

        /* ============================================================
           Hero
           ============================================================ */
        .hero-card {
            position: relative;
            overflow: hidden;
            padding: 2rem;
            margin-bottom: 1.5rem;
            margin-top: 1.5rem;
        }
        .hero-bg {
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, hsl(217 91% 60% / 0.05), hsl(271 81% 56% / 0.05));
            pointer-events: none;
        }
        .hero-content {
            position: relative;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        }
        .hero-icon-wrap {
            flex-shrink: 0;
            width: 4rem;
            height: 4rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: var(--radius);
            background: linear-gradient(135deg, hsl(217 91% 60% / 0.15), hsl(271 81% 56% / 0.15));
            font-size: 2rem;
        }
        .hero-favicon {
            width: 2.5rem;
            height: 2.5rem;
            border-radius: 0.5rem;
        }
        .is-hidden { display: none; }
        .hero-text { flex: 1; min-width: 0; }
        .hero-title {
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            line-height: 1.3;
            margin-bottom: 0.25rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .hero-url {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: hsl(var(--muted-foreground));
            font-size: 0.875rem;
            font-family: 'JetBrains Mono', monospace;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .hero-url svg { flex-shrink: 0; opacity: 0.5; }
        .hero-status {
            flex-shrink: 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.125rem;
            font-weight: 600;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }
        .status-success { background: #22c55e; box-shadow: 0 0 12px #22c55e40; }
        .status-warning { background: #f59e0b; box-shadow: 0 0 12px #f59e0b40; }
        .status-error { background: #ef4444; box-shadow: 0 0 12px #ef444440; }

        /* ============================================================
           Stats Grid
           ============================================================ */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .stat-card {
            padding: 1.25rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .stat-icon-wrap {
            width: 3rem;
            height: 3rem;
            border-radius: var(--radius);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            flex-shrink: 0;
        }
        .stat-info {
            display: flex;
            flex-direction: column;
        }
        .stat-value {
            font-size: 1.75rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.2;
        }
        .stat-label {
            font-size: 0.8rem;
            color: hsl(var(--muted-foreground));
            font-weight: 500;
        }

        /* ============================================================
           Section Headers
           ============================================================ */
        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid hsl(var(--border) / 0.3);
        }
        .section-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .section-icon { font-size: 1.2rem; }
        .section-count {
            margin-left: 0.5rem;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.125rem 0.5rem;
            border-radius: 9999px;
            background: hsl(var(--muted));
            color: hsl(var(--muted-foreground));
        }
        .section-actions {
            display: flex;
            gap: 0.5rem;
        }

        /* ============================================================
           Search
           ============================================================ */
        .search-section {
            padding: 1.25rem;
            margin-bottom: 1.5rem;
        }
        .search-inner {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.5rem 1rem;
            border-radius: var(--radius);
            background: hsl(var(--background));
            border: 1px solid hsl(var(--border));
            transition: border-color 0.2s;
        }
        .search-inner:focus-within {
            border-color: hsl(var(--primary) / 0.5);
            box-shadow: 0 0 0 3px hsl(var(--primary) / 0.1);
        }
        .search-icon { flex-shrink: 0; opacity: 0.4; }
        .search-input {
            flex: 1;
            border: none;
            background: transparent;
            color: hsl(var(--foreground));
            font-family: 'Inter', sans-serif;
            font-size: 0.9375rem;
            outline: none;
            padding: 0.25rem 0;
        }
        .search-input::placeholder {
            color: hsl(var(--muted-foreground) / 0.6);
        }
        .search-clear {
            display: none;
            background: none;
            border: none;
            color: hsl(var(--muted-foreground));
            cursor: pointer;
            padding: 0.25rem;
            border-radius: 4px;
            opacity: 0.6;
            transition: opacity 0.2s;
        }
        .search-clear:hover { opacity: 1; }
        .search-clear.visible { display: block; }
        .search-hints {
            display: flex;
            gap: 0.75rem;
            margin-top: 0.75rem;
            flex-wrap: wrap;
            align-items: center;
            font-size: 0.8rem;
            color: hsl(var(--muted-foreground));
        }
        .hint-chip {
            background: none;
            border: 1px solid hsl(var(--border));
            color: hsl(var(--muted-foreground));
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.15s;
            font-family: inherit;
        }
        .hint-chip:hover {
            border-color: hsl(var(--primary) / 0.5);
            color: hsl(var(--primary));
        }

        /* ============================================================
           Category Chips & Legend
           ============================================================ */
        .cat-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.375rem;
            margin-top: 0.875rem;
        }
        .cat-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.375rem;
            padding: 0.3rem 0.7rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            font-family: inherit;
            background: hsl(var(--muted) / 0.4);
            border: 1px solid hsl(var(--border) / 0.5);
            color: hsl(var(--muted-foreground));
            cursor: pointer;
            transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
            user-select: none;
        }
        .cat-chip:hover {
            border-color: hsl(var(--primary) / 0.45);
            color: hsl(var(--primary));
            transform: translateY(-1px);
        }
        .cat-chip.is-active {
            background: hsl(var(--primary));
            border-color: hsl(var(--primary));
            color: hsl(var(--primary-foreground));
            box-shadow: 0 4px 14px hsl(217 91% 60% / 0.35);
        }
        .cat-chip-count {
            font-size: 0.65rem;
            font-weight: 700;
            padding: 0.05rem 0.4rem;
            border-radius: 9999px;
            background: hsl(var(--background) / 0.6);
        }
        .legend {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }
        .legend-divider {
            width: 1px;
            height: 0.9rem;
            background: hsl(var(--border));
            margin: 0 0.25rem;
        }
        .cookie-name {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            opacity: 0.6;
        }

        /* ============================================================
           Category Distribution Chart
           ============================================================ */
        .dist-chart {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        .dist-row {
            display: grid;
            grid-template-columns: 220px 1fr 2.5rem;
            align-items: center;
            gap: 0.75rem;
        }
        .dist-label {
            font-size: 0.8125rem;
            color: hsl(var(--muted-foreground));
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .dist-track {
            height: 8px;
            border-radius: 9999px;
            background: hsl(var(--muted) / 0.4);
            overflow: hidden;
        }
        .dist-fill {
            height: 100%;
            border-radius: 9999px;
            transform-origin: left;
            animation: distGrow 0.9s cubic-bezier(0.22, 1, 0.36, 1) backwards;
            box-shadow: 0 0 10px rgb(255 255 255 / 0.06);
        }
        @keyframes distGrow {
            from { transform: scaleX(0); }
            to { transform: scaleX(1); }
        }
        .dist-count {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 600;
            text-align: right;
            color: hsl(var(--foreground));
        }
        @media (max-width: 768px) {
            .dist-row {
                grid-template-columns: 130px 1fr 2rem;
                gap: 0.5rem;
            }
        }

        /* ============================================================
           Tech Pills / Grid
           ============================================================ */
        .tech-grid-section {
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .tech-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .tech-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.375rem;
            padding: 0.375rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.8125rem;
            font-weight: 500;
            background: hsl(var(--muted) / 0.5);
            border: 1px solid hsl(var(--border) / 0.4);
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            user-select: none;
        }
        .tech-pill:hover {
            border-color: hsl(var(--primary) / 0.4);
            background: hsl(var(--primary) / 0.08);
            transform: translateY(-1px);
        }
        .tech-pill.is-hidden {
            display: none;
        }
        .tech-pill.is-highlighted {
            border-color: hsl(var(--primary));
            box-shadow: 0 0 0 2px hsl(var(--primary) / 0.15);
        }
        .tech-pill-indicator {
            width: 0.5rem;
            height: 0.5rem;
            border-radius: 50%;
        }
        .confidence-high { background: #22c55e; }
        .confidence-medium { background: #f59e0b; }
        .confidence-low { background: #ef4444; }
        .tech-pill-name { }
        .tech-version {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.6875rem;
            opacity: 0.7;
        }
        .tech-pill-confidence {
            font-size: 0.625rem;
            opacity: 0.5;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .tech-grid-empty {
            text-align: center;
            padding: 2rem;
        }
        .tech-grid-empty .empty-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            display: block;
        }
        .tech-grid-empty p {
            color: hsl(var(--muted-foreground));
            margin-bottom: 0.75rem;
        }

        /* ============================================================
           Info Grid / Rows
           ============================================================ */
        .info-grid {
            display: flex;
            flex-direction: column;
            gap: 0.375rem;
        }
        .info-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.625rem 0.75rem;
            border-radius: var(--radius-sm);
            background: hsl(var(--background) / 0.4);
            gap: 1rem;
        }
        .info-key {
            font-size: 0.8125rem;
            color: hsl(var(--muted-foreground));
            font-weight: 500;
            flex-shrink: 0;
        }
        .info-value {
            font-size: 0.875rem;
            font-weight: 500;
            text-align: right;
            word-break: break-word;
        }
        .info-value.code {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8125rem;
            color: hsl(var(--primary));
        }

        /* ============================================================
           Metrics Grid
           ============================================================ */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 0.75rem;
        }
        .metric-card {
            padding: 1rem;
            border-radius: var(--radius-sm);
            background: hsl(var(--background) / 0.4);
            text-align: center;
        }
        .metric-card-wide {
            grid-column: 1 / -1;
        }
        .metric-label {
            font-size: 0.75rem;
            color: hsl(var(--muted-foreground));
            font-weight: 500;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        .metric-value {
            font-size: 1.5rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: -0.02em;
        }

        .text-emerald-400 { color: #34d399; }
        .text-amber-400 { color: #fbbf24; }
        .text-red-400 { color: #f87171; }
        .text-blue-400 { color: #60a5fa; }
        .text-purple-400 { color: #c084fc; }
        .text-pink-400 { color: #f472b6; }
        .text-green-400 { color: #4ade80; }
        .text-sky-400 { color: #38bdf8; }
        .text-slate-400 { color: #94a3b8; }

        /* ============================================================
           Social Section
           ============================================================ */
        .social-platform {
            margin-bottom: 1rem;
        }
        .social-platform:last-child { margin-bottom: 0; }
        .social-title {
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            padding: 0.25rem 0.75rem;
            border-radius: var(--radius-sm);
            background: hsl(var(--muted) / 0.3);
            display: inline-block;
        }

        /* ============================================================
           API List
           ============================================================ */
        .api-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.375rem;
            margin-top: 0.5rem;
            justify-content: center;
        }
        .api-item {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            background: hsl(var(--primary) / 0.08);
            color: hsl(var(--primary));
            border: 1px solid hsl(var(--primary) / 0.15);
        }

        /* ============================================================
           Code Block
           ============================================================ */
        .code-block {
            border-radius: var(--radius-sm);
            background: hsl(var(--background));
            padding: 1rem;
            overflow-x: auto;
        }
        .code-block pre {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8125rem;
            line-height: 1.6;
            color: #34d399;
            white-space: pre-wrap;
            word-break: break-all;
        }

        /* ============================================================
           Tech List (Detailed)
           ============================================================ */
        .tech-list {
            display: flex;
            flex-direction: column;
            gap: 0.375rem;
        }
        .tech-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.625rem 0.75rem;
            border-radius: var(--radius-sm);
            background: hsl(var(--background) / 0.4);
            gap: 0.75rem;
            transition: all 0.2s;
        }
        .tech-row:hover {
            background: hsl(var(--muted) / 0.4);
        }
        .tech-row.is-hidden {
            display: none;
        }
        .tech-row-info {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex: 1;
            min-width: 0;
            flex-wrap: wrap;
        }
        .tech-row-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.8125rem;
            font-weight: 600;
            white-space: nowrap;
        }
        .tech-row-meta {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-shrink: 0;
        }
        .tech-row-version {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: hsl(var(--muted-foreground));
            background: hsl(var(--background) / 0.5);
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
        }
        .tech-row-confidence {
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        .confidence-low { color: #ef4444; }
        .confidence-medium { color: #f59e0b; }
        .confidence-high { color: #22c55e; }

        /* Confidence bars */
        .confidence-bars {
            display: flex;
            gap: 3px;
            align-items: center;
        }
        .confidence-bars .bar {
            width: 6px;
            height: 12px;
            border-radius: 2px;
            background: hsl(var(--muted));
            transition: background 0.3s;
        }
        .confidence-bars .bar.active:nth-child(1) { background: #ef4444; }
        .confidence-bars .bar.active:nth-child(2) { background: #f59e0b; }
        .confidence-bars .bar.active:nth-child(3) { background: #22c55e; }

        /* ============================================================
           Tech Items (Plugins/Themes sublist)
           ============================================================ */
        .tech-items { }
        .tech-items-toggle {
            display: flex;
            align-items: center;
            gap: 0.375rem;
            background: hsl(var(--muted) / 0.3);
            border: 1px solid hsl(var(--border) / 0.3);
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            color: hsl(var(--muted-foreground));
            cursor: pointer;
            font-family: inherit;
            transition: all 0.15s;
        }
        .tech-items-toggle:hover {
            border-color: hsl(var(--primary) / 0.3);
            color: hsl(var(--primary));
        }
        .tech-items-toggle svg {
            transition: transform 0.2s;
        }
        .tech-items-toggle.is-open svg {
            transform: rotate(180deg);
        }
        .tech-items-list {
            display: none;
            flex-wrap: wrap;
            gap: 0.25rem;
            margin-top: 0.5rem;
            padding-top: 0.5rem;
            border-top: 1px solid hsl(var(--border) / 0.2);
        }
        .tech-items-list.is-visible {
            display: flex;
        }
        .tech-item-chip {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.6875rem;
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            background: hsl(var(--muted) / 0.3);
            border: 1px solid hsl(var(--border) / 0.2);
        }

        /* ============================================================
           Accordion
           ============================================================ */
        .accordion { }
        .accordion-item {
            border-bottom: 1px solid hsl(var(--border) / 0.2);
        }
        .accordion-item:last-child { border-bottom: none; }
        .accordion-trigger {
            width: 100%;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem;
            background: none;
            border: none;
            color: hsl(var(--foreground));
            font-family: inherit;
            font-size: 0.8125rem;
            font-weight: 500;
            cursor: pointer;
            border-radius: var(--radius-sm);
            transition: background 0.15s;
        }
        .accordion-trigger:hover {
            background: hsl(var(--muted) / 0.3);
        }
        .accordion-icon svg {
            transition: transform 0.2s;
        }
        .accordion-trigger.is-open .accordion-icon svg {
            transform: rotate(90deg);
        }
        .accordion-label { }
        .accordion-content {
            display: none;
            padding: 0 0.75rem 0.75rem;
        }
        .accordion-content.is-visible {
            display: block;
        }

        /* ============================================================
           Empty State
           ============================================================ */
        .empty-state {
            text-align: center;
            padding: 3rem 1rem;
        }
        .empty-state .empty-icon {
            font-size: 3rem;
            margin-bottom: 0.75rem;
            display: block;
            opacity: 0.5;
        }
        .empty-state h3 {
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .empty-state p {
            color: hsl(var(--muted-foreground));
            max-width: 400px;
            margin: 0 auto;
        }

        /* ============================================================
           Buttons
           ============================================================ */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            border-radius: var(--radius-sm);
            font-weight: 600;
            font-family: inherit;
            font-size: 0.8125rem;
            padding: 0.5rem 1rem;
            border: none;
            cursor: pointer;
            transition: all 0.15s;
            white-space: nowrap;
        }
        .btn-ghost {
            background: transparent;
            color: hsl(var(--muted-foreground));
        }
        .btn-ghost:hover {
            background: hsl(var(--muted));
            color: hsl(var(--foreground));
        }
        .btn-outline {
            background: transparent;
            border: 1px solid hsl(var(--border));
            color: hsl(var(--muted-foreground));
        }
        .btn-outline:hover {
            border-color: hsl(var(--primary) / 0.4);
            color: hsl(var(--primary));
        }
        .btn-sm {
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
        }
        .btn-primary {
            background: hsl(var(--primary));
            color: hsl(var(--primary-foreground));
        }
        .btn-primary:hover {
            background: hsl(var(--primary) / 0.9);
        }

        /* ============================================================
           Toast
           ============================================================ */
        .toast {
            position: fixed;
            bottom: 1.5rem;
            left: 50%;
            transform: translate(-50%, 16px);
            z-index: 300;
            padding: 0.6rem 1.25rem;
            border-radius: 9999px;
            background: hsl(var(--foreground));
            color: hsl(var(--background));
            font-size: 0.8125rem;
            font-weight: 600;
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
            box-shadow: var(--shadow-lg);
        }
        .toast.is-visible {
            opacity: 1;
            transform: translate(-50%, 0);
        }

        /* ============================================================
           Footer
           ============================================================ */
        /* ============================================================
           Back To Top
           ============================================================ */
        .back-to-top {
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            z-index: 150;
            width: 2.75rem;
            height: 2.75rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 9999px;
            background: hsl(var(--primary));
            color: hsl(var(--primary-foreground));
            border: none;
            cursor: pointer;
            opacity: 0;
            transform: translateY(12px);
            pointer-events: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 8px 24px hsl(217 91% 60% / 0.35);
        }
        .back-to-top.is-visible {
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }
        .back-to-top:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 32px hsl(217 91% 60% / 0.45);
        }

        .footer {
            border-top: 1px solid hsl(var(--border) / 0.3);
            margin-top: 2rem;
        }
        .footer-inner {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.75rem;
            padding: 1.5rem 0;
            color: hsl(var(--muted-foreground));
            font-size: 0.8125rem;
        }
        .footer-dot {
            width: 3px;
            height: 3px;
            border-radius: 50%;
            background: hsl(var(--muted-foreground) / 0.4);
        }

        /* ============================================================
           Responsive
           ============================================================ */
        @media (max-width: 1024px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 768px) {
            .hero-content {
                flex-wrap: wrap;
            }
            .hero-title {
                font-size: 1.25rem;
                white-space: normal;
            }
            .hero-url {
                white-space: normal;
                word-break: break-all;
            }
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 0.75rem;
            }
            .stat-card {
                padding: 1rem;
            }
            .stat-value {
                font-size: 1.375rem;
            }
            .stat-icon-wrap {
                width: 2.5rem;
                height: 2.5rem;
                font-size: 1.25rem;
            }
            .card {
                padding: 1rem;
            }
            .tech-row {
                flex-wrap: wrap;
            }
            .tech-row-meta {
                width: 100%;
                justify-content: flex-start;
                padding-top: 0.375rem;
                border-top: 1px solid hsl(var(--border) / 0.15);
            }
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .container {
                padding: 0 1rem;
            }
        }

        @media (max-width: 480px) {
            .stats-grid {
                grid-template-columns: 1fr 1fr;
                gap: 0.5rem;
            }
            .hero-card {
                padding: 1.25rem;
            }
            .hero-icon-wrap {
                width: 3rem;
                height: 3rem;
                font-size: 1.5rem;
            }
        }

        /* ============================================================
           Print
           ============================================================ */
        @media print {
            .orbs, .header { display: none; }
            .glass { background: #fff; color: #000; border: 1px solid #ddd; backdrop-filter: none; }
            body { background: #fff; color: #000; }
            .tech-row { break-inside: avoid; }
        }
        """

    def _get_scripts(self) -> str:
        """Return the JavaScript for interactive features."""
        return """
        document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.getElementById('techSearch');
            const clearBtn = document.getElementById('clearSearch');
            const techPills = document.querySelectorAll('.tech-pill');
            const techRows = document.querySelectorAll('.tech-row');
            const techCategories = document.querySelectorAll('.tech-category');
            const techGridEmpty = document.getElementById('techGridEmpty');
            const resetBtn = document.getElementById('resetSearch');
            const hintChips = document.querySelectorAll('.hint-chip');

            // Scroll progress bar
            const progressBar = document.getElementById('scrollProgress');
            function updateScrollProgress() {
                const docHeight = document.documentElement.scrollHeight - window.innerHeight;
                const pct = docHeight > 0 ? (window.scrollY / docHeight) * 100 : 0;
                if (progressBar) progressBar.style.width = pct + '%';
            }
            window.addEventListener('scroll', updateScrollProgress, { passive: true });
            updateScrollProgress();

            // Back-to-top button
            const backToTop = document.getElementById('backToTop');
            function toggleBackToTop() {
                if (backToTop) backToTop.classList.toggle('is-visible', window.scrollY > 600);
            }
            window.addEventListener('scroll', toggleBackToTop, { passive: true });
            toggleBackToTop();
            if (backToTop) {
                backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
            }

            // Count-up animation for stat cards
            const countUps = document.querySelectorAll('.count-up');
            countUps.forEach(el => {
                const target = parseInt(el.dataset.target);
                if (target > 0) {
                    let current = 0;
                    const step = Math.max(1, Math.floor(target / 30));
                    const interval = setInterval(() => {
                        current += step;
                        if (current >= target) {
                            current = target;
                            clearInterval(interval);
                        }
                        el.textContent = current;
                    }, 40);
                }
            });

            // Search functionality
            function filterTechs(query) {
                const q = query.toLowerCase().trim();
                let visibleCount = 0;

                // Filter pills
                techPills.forEach(pill => {
                    const tech = pill.dataset.tech || '';
                    const cat = pill.dataset.category || '';
                    if (!q || tech.includes(q) || cat.includes(q)) {
                        pill.classList.remove('is-hidden');
                        if (q && tech.includes(q)) {
                            pill.classList.add('is-highlighted');
                        } else {
                            pill.classList.remove('is-highlighted');
                        }
                        visibleCount++;
                    } else {
                        pill.classList.add('is-hidden');
                        pill.classList.remove('is-highlighted');
                    }
                });

                // Filter detailed rows
                techRows.forEach(row => {
                    const name = row.dataset.techName || '';
                    if (!q || name.includes(q)) {
                        row.classList.remove('is-hidden');
                    } else {
                        row.classList.add('is-hidden');
                    }
                });

                // Show/hide categories based on visible rows
                techCategories.forEach(cat => {
                    const visibleRows = cat.querySelectorAll('.tech-row:not(.is-hidden)');
                    cat.style.display = visibleRows.length > 0 ? '' : 'none';
                });

                // Show empty state
                if (techGridEmpty) {
                    techGridEmpty.style.display = (q && visibleCount === 0) ? 'block' : 'none';
                }

                // Clear button visibility
                if (clearBtn) {
                    clearBtn.classList.toggle('visible', q.length > 0);
                }
            }

            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    filterTechs(this.value);
                });
            }

            if (clearBtn) {
                clearBtn.addEventListener('click', function() {
                    if (searchInput) {
                        searchInput.value = '';
                        filterTechs('');
                        searchInput.focus();
                    }
                });
            }

            if (resetBtn) {
                resetBtn.addEventListener('click', function() {
                    if (searchInput) {
                        searchInput.value = '';
                        filterTechs('');
                        searchInput.focus();
                    }
                });
            }

            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                const tag = (document.activeElement && document.activeElement.tagName) || '';
                const typing = tag === 'INPUT' || tag === 'TEXTAREA';
                if (e.key === '/' && !typing) {
                    e.preventDefault();
                    if (searchInput) { searchInput.focus(); searchInput.select(); }
                }
                if (e.key === 'Escape' && searchInput && searchInput === document.activeElement) {
                    searchInput.value = '';
                    filterTechs('');
                    searchInput.blur();
                }
            });

            // Category filter chips
            const catChips = document.querySelectorAll('.cat-chip');
            let activeCat = null;
            catChips.forEach(chip => {
                chip.addEventListener('click', function() {
                    const cat = this.dataset.cat;
                    activeCat = (activeCat === cat) ? null : cat;
                    catChips.forEach(c => c.classList.toggle('is-active', c.dataset.cat === activeCat));

                    techCategories.forEach(section => {
                        const sectionCat = (section.dataset.category || '').toLowerCase();
                        section.style.display = (!activeCat || sectionCat === activeCat) ? '' : 'none';
                    });

                    techPills.forEach(pill => {
                        const pillCat = pill.dataset.category || '';
                        pill.classList.toggle('is-hidden', !!activeCat && pillCat !== activeCat);
                    });

                    if (activeCat && searchInput) {
                        searchInput.value = '';
                        filterTechs('');
                    }
                });
            });

            // Hint chips
            hintChips.forEach(chip => {
                chip.addEventListener('click', function() {
                    const hint = this.dataset.hint;
                    if (searchInput) {
                        searchInput.value = hint;
                        filterTechs(hint);
                        searchInput.focus();
                    }
                });
            });

            // Copy-all button with toast feedback
            const copyBtn = document.getElementById('copyAll');
            if (copyBtn) {
                copyBtn.addEventListener('click', function() {
                    const names = Array.from(document.querySelectorAll('.tech-pill .tech-pill-name'))
                        .map(el => el.textContent.trim());
                    if (!names.length) return;
                    const text = names.join(', ');
                    (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject())
                        .then(() => showToast('Copied ' + names.length + ' technologies 📋'))
                        .catch(() => showToast('Copy failed 😕'));
                });
            }

            // Download embedded JSON
            const dlBtn = document.getElementById('downloadJson');
            if (dlBtn) {
                dlBtn.addEventListener('click', function() {
                    const dataEl = document.getElementById('report-data');
                    if (!dataEl) return;
                    const blob = new Blob([dataEl.textContent], { type: 'application/json' });
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = 'tech_report_' + location.pathname.replace(/[^a-z0-9]+/gi, '_') + '.json';
                    a.click();
                    URL.revokeObjectURL(a.href);
                    showToast('JSON exported ⬇');
                });
            }

            // Expand All button
            const expandBtn = document.getElementById('expandAll');
            if (expandBtn) {
                expandBtn.addEventListener('click', function() {
                    const itemsLists = document.querySelectorAll('.tech-items-list');
                    const toggles = document.querySelectorAll('.tech-items-toggle');
                    const isAnyHidden = Array.from(itemsLists).some(list => !list.classList.contains('is-visible'));

                    itemsLists.forEach(list => {
                        list.classList.toggle('is-visible', isAnyHidden);
                    });
                    toggles.forEach(toggle => {
                        toggle.classList.toggle('is-open', isAnyHidden);
                    });
                    this.textContent = isAnyHidden ? 'Hide Details' : 'Show Details';
                });
            }
        });

        // Toast notification helper
        function showToast(message) {
            const toast = document.getElementById('toast');
            if (!toast) return;
            toast.textContent = message;
            toast.classList.add('is-visible');
            clearTimeout(toast._t);
            toast._t = setTimeout(() => toast.classList.remove('is-visible'), 2200);
        }

        // Global functions for inline onclick
        function toggleAccordion(id) {
            const content = document.getElementById(id);
            const trigger = content.previousElementSibling;
            if (content && trigger) {
                content.classList.toggle('is-visible');
                trigger.classList.toggle('is-open');
            }
        }

        function toggleTechItems(btn) {
            const list = btn.nextElementSibling;
            if (list) {
                list.classList.toggle('is-visible');
                btn.classList.toggle('is-open');
            }
        }

        function filterByTech(techName) {
            const searchInput = document.getElementById('techSearch');
            if (searchInput) {
                searchInput.value = techName;
                searchInput.dispatchEvent(new Event('input'));
            }
        }
        """
