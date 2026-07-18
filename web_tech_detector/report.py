"""
HTML report generator module - Creates beautiful shadcn/ui-inspired reports.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from string import Template


# Category icons (emoji)
CATEGORY_ICONS: Dict[str, str] = {
    "JavaScript Frameworks": "⚡",
    "CSS Frameworks": "🎨",
    "Static Site Generators": "🚀",
    "CMS": "📝",
    "E-commerce": "🛒",
    "Analytics": "📊",
    "Web Servers": "🖥️",
    "Programming Languages": "💻",
    "Hosting & CDN": "☁️",
    "Libraries": "📚",
    "Security": "🔒",
    "Features": "✨",
    "Server Headers": "📡",
}

# Category color classes
CATEGORY_COLORS: Dict[str, str] = {
    "JavaScript Frameworks": "blue",
    "CSS Frameworks": "purple",
    "Static Site Generators": "pink",
    "CMS": "orange",
    "E-commerce": "green",
    "Analytics": "yellow",
    "Web Servers": "red",
    "Programming Languages": "cyan",
    "Hosting & CDN": "indigo",
    "Libraries": "emerald",
    "Security": "amber",
    "Features": "violet",
    "Server Headers": "slate",
}


class ReportGenerator:
    """Generates HTML reports with shadcn/ui-inspired design."""

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
        )

    def save(self, output_path: str) -> str:
        """
        Generate and save the HTML report.

        Args:
            output_path: Directory to save the report

        Returns:
            Full path to the saved file
        """
        html_content = self.generate()

        # Generate filename
        safe_domain = self.domain.replace(".", "_").replace(":", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tech_report_{safe_domain}_{timestamp}.html"

        full_path = os.path.join(output_path, filename)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return full_path

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
        html_techs: Dict[str, List[str]],
        json_ld: List[Dict],
    ) -> str:
        """Build the complete HTML document."""

        # Build sections
        stats_section = self._build_stats_section(total_count, total_categories, status_code, json_ld_count)
        meta_section = self._build_meta_section(meta_techs)
        server_section = self._build_server_section(server_info)
        tech_sections = self._build_tech_sections(html_techs)
        json_ld_section = self._build_json_ld_section(json_ld)

        return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tech Report - {self._escape(self.title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        {self._get_styles()}
    </style>
</head>
<body>
    <div class="min-h-screen bg-background">
        <!-- Header -->
        <header class="sticky top-0 z-50 w-full border-b border-border/40 bg-background-95 backdrop-blur supports-backdrop-bg-background-60">
            <div class="container mx-auto px-4 py-4 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary-foreground">
                            <circle cx="11" cy="11" r="8"></circle>
                            <path d="m21 21-4.3-4.3"></path>
                        </svg>
                    </div>
                    <div>
                        <h1 class="text-lg font-semibold">Tech Detector</h1>
                        <p class="text-xs text-muted-foreground">Web Technology Analyzer</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <span class="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors border-transparent bg-primary text-primary-foreground shadow">
                        v1.0.0
                    </span>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="container mx-auto px-4 py-8">
            <!-- URL Card -->
            <div class="rounded-xl border bg-card text-card-foreground shadow-sm mb-6">
                <div class="p-6">
                    <div class="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                        </svg>
                        Analyzed URL
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="h-10 w-10 rounded-lg bg-muted flex items-center justify-center">
                            <span class="text-xl">🌐</span>
                        </div>
                        <div>
                            <p class="text-xl font-semibold">{self._escape(self.title)}</p>
                            <p class="text-sm text-muted-foreground font-mono">{self._escape(self.url)}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stats Grid -->
            {stats_section}

            <!-- Meta Information -->
            {meta_section}

            <!-- Server Information -->
            {server_section}

            <!-- Detected Technologies -->
            {tech_sections}

            <!-- JSON-LD Data -->
            {json_ld_section}
        </main>

        <!-- Footer -->
        <footer class="border-t border-border">
            <div class="container mx-auto px-4 py-6 text-center text-sm text-muted-foreground">
                Generated on {self.results.get('detected_at', 'N/A')} • Web Technology Detector
            </div>
        </footer>
    </div>
</body>
</html>"""

    def _build_stats_section(self, total_count: int, total_categories: int, status_code: int, json_ld_count: int) -> str:
        """Build the statistics cards section."""
        stats = [
            {"label": "Technologies", "value": total_count, "icon": "🔬"},
            {"label": "Categories", "value": total_categories, "icon": "📂"},
            {"label": "Status Code", "value": status_code, "icon": "📡"},
            {"label": "JSON-LD", "value": json_ld_count, "icon": "📋"},
        ]

        cards = ""
        for stat in stats:
            cards += f"""
            <div class="rounded-xl border bg-card text-card-foreground shadow-sm">
                <div class="p-6">
                    <div class="flex items-center justify-between mb-2">
                        <p class="text-sm font-medium text-muted-foreground">{stat['label']}</p>
                        <span class="text-lg">{stat['icon']}</span>
                    </div>
                    <div class="text-3xl font-bold">{stat['value']}</div>
                </div>
            </div>"""

        return f"""
        <div class="grid grid-cols-2 stats-grid gap-4 mb-6">
            {cards}
        </div>"""

    def _build_meta_section(self, meta_techs: Dict) -> str:
        """Build the meta information section."""
        if not meta_techs:
            return ""

        items = ""
        for key, value in meta_techs.items():
            items += f"""
            <div class="flex items-center justify-between p-3 rounded-lg bg-muted-50">
                <span class="text-sm text-muted-foreground">{self._escape(key)}</span>
                <span class="text-sm font-medium">{self._escape(value)}</span>
            </div>"""

        return f"""
        <div class="rounded-xl border bg-card text-card-foreground shadow-sm mb-6">
            <div class="p-4 border-b">
                <h2 class="text-lg font-semibold flex items-center gap-2">
                    <span class="text-xl">🏷️</span>
                    Meta Information
                </h2>
            </div>
            <div class="p-4 space-y-2">
                {items}
            </div>
        </div>"""

    def _build_server_section(self, server_info: Dict) -> str:
        """Build the server information section."""
        if not server_info:
            return ""

        items = ""
        for key, value in server_info.items():
            items += f"""
            <div class="flex items-center justify-between p-3 rounded-lg bg-muted-50">
                <span class="text-sm text-muted-foreground">{self._escape(key)}</span>
                <span class="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold border-transparent bg-primary text-primary-foreground">
                    {self._escape(value)}
                </span>
            </div>"""

        return f"""
        <div class="rounded-xl border bg-card text-card-foreground shadow-sm mb-6">
            <div class="p-4 border-b">
                <h2 class="text-lg font-semibold flex items-center gap-2">
                    <span class="text-xl">🖥️</span>
                    Server Information
                </h2>
            </div>
            <div class="p-4 space-y-2">
                {items}
            </div>
        </div>"""

    def _build_tech_sections(self, html_techs: Dict[str, List[str]]) -> str:
        """Build the technology detection sections."""
        sections = ""

        for category, techs in html_techs.items():
            if not techs:
                continue

            icon = CATEGORY_ICONS.get(category, "📦")
            color_class = CATEGORY_COLORS.get(category, "slate")

            badges = ""
            for tech in techs:
                badges += f"""
                    <span class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors badge-{color_class}">
                        {self._escape(tech)}
                    </span>"""

            sections += f"""
            <div class="rounded-xl border bg-card text-card-foreground shadow-sm mb-6">
                <div class="p-4 border-b">
                    <h2 class="text-lg font-semibold flex items-center gap-2">
                        <span class="text-xl">{icon}</span>
                        {self._escape(category)}
                    </h2>
                </div>
                <div class="p-4">
                    <div class="flex flex-wrap gap-2">
                        {badges}
                    </div>
                </div>
            </div>"""

        if not sections:
            return """
            <div class="rounded-xl border bg-card text-card-foreground shadow-sm mb-6">
                <div class="p-8 text-center">
                    <div class="text-4xl mb-4 opacity-50">🔍</div>
                    <p class="text-muted-foreground">No technologies detected in the HTML source</p>
                </div>
            </div>"""

        return sections

    def _build_json_ld_section(self, json_ld: List[Dict]) -> str:
        """Build the JSON-LD structured data section."""
        if not json_ld:
            return ""

        items = ""
        for i, item in enumerate(json_ld):
            formatted = json.dumps(item, indent=2)
            items += f"""
            <div class="rounded-lg bg-muted p-4 overflow-x-auto">
                <pre class="text-sm font-mono text-emerald-400 whitespace-pre-wrap">{self._escape(formatted)}</pre>
            </div>"""

        return f"""
        <div class="rounded-xl border bg-card text-card-foreground shadow-sm mb-6">
            <div class="p-4 border-b">
                <h2 class="text-lg font-semibold flex items-center gap-2">
                    <span class="text-xl">📋</span>
                    JSON-LD Structured Data
                </h2>
            </div>
            <div class="p-4 space-y-4">
                {items}
            </div>
        </div>"""

    def _get_styles(self) -> str:
        """Return the CSS styles for the report."""
        return """
        :root {
            --background: 0 0% 100%;
            --foreground: 224 71% 4%;
            --card: 0 0% 100%;
            --card-foreground: 224 71% 4%;
            --primary: 220 70% 50%;
            --primary-foreground: 210 40% 98%;
            --secondary: 220 14% 96%;
            --secondary-foreground: 220 9% 46%;
            --muted: 220 14% 96%;
            --muted-foreground: 220 9% 46%;
            --accent: 220 14% 96%;
            --accent-foreground: 224 71% 4%;
            --destructive: 0 84% 60%;
            --border: 220 13% 91%;
            --ring: 220 70% 50%;
            --radius: 0.75rem;
        }

        .dark {
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
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            border-color: hsl(var(--border));
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: hsl(var(--background));
            color: hsl(var(--foreground));
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }

        .min-h-screen {
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
        }

        .mx-auto {
            margin-left: auto;
            margin-right: auto;
        }

        .px-4 {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .py-4 {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        .py-6 {
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
        }

        .py-8 {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .p-3 {
            padding: 0.75rem;
        }

        .p-4 {
            padding: 1rem;
        }

        .p-6 {
            padding: 1.5rem;
        }

        .p-8 {
            padding: 2rem;
        }

        .mb-2 {
            margin-bottom: 0.5rem;
        }

        .mb-4 {
            margin-bottom: 1rem;
        }

        .mb-6 {
            margin-bottom: 1.5rem;
        }

        .text-center {
            text-align: center;
        }

        .flex {
            display: flex;
        }

        .items-center {
            align-items: center;
        }

        .justify-between {
            justify-content: space-between;
        }

        .gap-2 {
            gap: 0.5rem;
        }

        .gap-3 {
            gap: 0.75rem;
        }

        .grid {
            display: grid;
        }

        .grid-cols-2 {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .space-y-2 > * + * {
            margin-top: 0.5rem;
        }

        .space-y-4 > * + * {
            margin-top: 1rem;
        }

        .rounded-xl {
            border-radius: 0.75rem;
        }

        .rounded-lg {
            border-radius: 0.5rem;
        }

        .rounded-full {
            border-radius: 9999px;
        }

        .border {
            border-width: 1px;
            border-style: solid;
        }

        .border-t {
            border-top-width: 1px;
            border-top-style: solid;
        }

        .border-b {
            border-bottom-width: 1px;
            border-bottom-style: solid;
        }

        .border-transparent {
            border-color: transparent;
        }

        .bg-card {
            background-color: hsl(var(--card));
        }

        .bg-primary {
            background-color: hsl(var(--primary));
        }

        .bg-muted {
            background-color: hsl(var(--muted));
        }

        .bg-muted-50 {
            background-color: hsl(var(--muted) / 0.5);
        }

        .text-card-foreground {
            color: hsl(var(--card-foreground));
        }

        .text-primary-foreground {
            color: hsl(var(--primary-foreground));
        }

        .text-muted-foreground {
            color: hsl(var(--muted-foreground));
        }

        .text-foreground {
            color: hsl(var(--foreground));
        }

        .text-emerald-400 {
            color: #34d399;
        }

        .text-xl {
            font-size: 1.25rem;
            line-height: 1.75rem;
        }

        .text-lg {
            font-size: 1.125rem;
            line-height: 1.75rem;
        }

        .text-sm {
            font-size: 0.875rem;
            line-height: 1.25rem;
        }

        .text-xs {
            font-size: 0.75rem;
            line-height: 1rem;
        }

        .text-3xl {
            font-size: 1.875rem;
            line-height: 2.25rem;
        }

        .font-semibold {
            font-weight: 600;
        }

        .font-bold {
            font-weight: 700;
        }

        .font-medium {
            font-weight: 500;
        }

        .font-mono {
            font-family: 'JetBrains Mono', monospace;
        }

        .whitespace-pre-wrap {
            white-space: pre-wrap;
        }

        .overflow-x-auto {
            overflow-x: auto;
        }

        .inline-flex {
            display: inline-flex;
        }

        .flex-wrap {
            flex-wrap: wrap;
        }

        .w-full {
            width: 100%;
        }

        .h-8 {
            height: 2rem;
        }

        .w-8 {
            width: 2rem;
        }

        .h-10 {
            height: 2.5rem;
        }

        .w-10 {
            width: 2.5rem;
        }

        .shadow-sm {
            box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        }

        .sticky {
            position: sticky;
        }

        .top-0 {
            top: 0;
        }

        .z-50 {
            z-index: 50;
        }

        .backdrop-blur {
            backdrop-filter: blur(8px);
        }

        .bg-background-95 {
            background-color: hsl(var(--background) / 0.95);
        }

        .backdrop-blur {
            background-color: hsl(var(--background) / 0.95);
        }

        /* Badge colors */
        .badge-blue { background-color: #3b82f6; color: white; border-color: transparent; }
        .badge-purple { background-color: #8b5cf6; color: white; border-color: transparent; }
        .badge-pink { background-color: #ec4899; color: white; border-color: transparent; }
        .badge-orange { background-color: #f97316; color: white; border-color: transparent; }
        .badge-green { background-color: #22c55e; color: white; border-color: transparent; }
        .badge-yellow { background-color: #eab308; color: black; border-color: transparent; }
        .badge-red { background-color: #ef4444; color: white; border-color: transparent; }
        .badge-cyan { background-color: #06b6d4; color: white; border-color: transparent; }
        .badge-indigo { background-color: #6366f1; color: white; border-color: transparent; }
        .badge-emerald { background-color: #10b981; color: white; border-color: transparent; }
        .badge-amber { background-color: #f59e0b; color: black; border-color: transparent; }
        .badge-violet { background-color: #8b5cf6; color: white; border-color: transparent; }
        .badge-slate { background-color: #64748b; color: white; border-color: transparent; }

        @media (min-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(4, minmax(0, 1fr));
            }
        }

        @media (max-width: 768px) {
            .container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
        """