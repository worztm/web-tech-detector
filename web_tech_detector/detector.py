"""
Technology detection module - Analyzes HTML content to identify web technologies.
Supports 100+ technologies with version extraction, confidence scoring, and evidence tracking.
"""

import re
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


# Technology detection patterns organized by category
# Each tech has: patterns (list of regex), and optionally version_patterns
TECHNOLOGY_PATTERNS: Dict[str, Dict[str, dict]] = {
    "JavaScript Frameworks": {
        "React": {
            "patterns": [
                r"react(?:\.min)?\.js",
                r"react-dom(?:\.min)?\.js",
                r"react\.js",
                r"__NEXT_DATA__",
                r"next/static",
                r"data-reactroot",
                r"data-reactid",
                r"data-react-checksum",
                r"_reactRootContainer",
                r"__reactFiber",
                r"React\.[a-zA-Z]",
            ],
            "version_patterns": [r"react@([\d\.]+)", r"react/([\d\.]+)", r"version: '?([\d\.]+)"],
            "category": "JavaScript Frameworks",
        },
        "Vue.js": {
            "patterns": [
                r"vue(?:\.min)?\.js",
                r"vue\.runtime",
                r"v-cloak",
                r"v-if",
                r"v-for",
                r"v-bind",
                r"v-model",
                r"v-on:",
                r"__VUE__",
                r"Vue\.(?:component|directive|mixin)",
                r"vue-router",
                r"nuxt",
            ],
            "version_patterns": [r"vue@([\d\.]+)", r"vue/([\d\.]+)", r"Vue\.version\s*=\s*['\"]([\d\.]+)"],
            "category": "JavaScript Frameworks",
        },
        "Angular": {
            "patterns": [
                r"angular(?:\.min)?\.js",
                r"ng-version",
                r"ng-app",
                r"ng-controller",
                r"ng-repeat",
                r"ng-model",
                r"ng-bind",
                r"ng-if",
                r"ng-show",
                r"ng-hide",
                r"ng-click",
                r"ng-class",
                r"ng-style",
                r"ng-include",
                r"ng-view",
                r"ngRoute",
                r"ngSanitize",
            ],
            "version_patterns": [r"angular@([\d\.]+)", r"angular/([\d\.]+)", r"ng-version=\"?([\d\.]+)"],
            "category": "JavaScript Frameworks",
        },
        "Svelte": {
            "patterns": [r"svelte(?:\.min)?\.js", r"__svelte", r"sveltekit", r"\$: ", r"createSvelte"],
            "version_patterns": [r"svelte@([\d\.]+)", r"svelte/([\d\.]+)"],
            "category": "JavaScript Frameworks",
        },
        "Solid.js": {
            "patterns": [r"solid(?:\.min)?\.js", r"solid-js", r"createSignal", r"createEffect", r"createMemo"],
            "version_patterns": [r"solid-js@([\d\.]+)"],
            "category": "JavaScript Frameworks",
        },
        "Preact": {
            "patterns": [r"preact(?:\.min)?\.js", r"preact\.js", r"__preact"],
            "version_patterns": [r"preact@([\d\.]+)"],
            "category": "JavaScript Frameworks",
        },
        "Alpine.js": {
            "patterns": [r"alpine(?:\.min)?\.js", r"x-data", r"x-init", r"x-show", r"x-bind", r"x-on", r"x-if", r"x-for", r"x-model", r"x-text", r"x-html", r"x-cloak", r"x-teleport", r"x-ref"],
            "version_patterns": [r"alpinejs@([\d\.]+)"],
            "category": "JavaScript Frameworks",
        },
        "Stimulus": {
            "patterns": [r"stimulus(?:\.min)?\.js", r"data-controller", r"data-target", r"data-action"],
            "version_patterns": [r"stimulus@([\d\.]+)"],
            "category": "JavaScript Frameworks",
        },
        "jQuery": {
            "patterns": [
                r"jquery(?:\.min)?\.js",
                r"jquery-\d[\d\.]+",
                r"jquery\.js",
                r"window\.jQuery",
                r"jQuery\s*\(",
            ],
            "version_patterns": [r"jquery-([\d\.]+)", r"jQuery.*v?([\d\.]+)"],
            "category": "JavaScript Frameworks",
        },
        "Backbone.js": {
            "patterns": [r"backbone(?:\.min)?\.js", r"Backbone\."],
            "category": "JavaScript Frameworks",
        },
        "Ember.js": {
            "patterns": [r"ember(?:\.min)?\.js", r"Ember\."],
            "category": "JavaScript Frameworks",
        },
        "MooTools": {
            "patterns": [r"mootools(?:\.min)?\.js", r"MooTools"],
            "category": "JavaScript Frameworks",
        },
        "Dojo": {
            "patterns": [r"dojo(?:\.min)?\.js", r"dojo\.js", r"dijit"],
            "category": "JavaScript Frameworks",
        },
        "HTMX": {
            "patterns": [r"htmx(?:\.min)?\.js", r"hx-get", r"hx-post", r"hx-put", r"hx-delete", r"hx-target", r"hx-trigger", r"hx-swap", r"hx-boost"],
            "version_patterns": [r"htmx@([\d\.]+)"],
            "category": "JavaScript Frameworks",
        },
        "Lit": {
            "patterns": [r"lit(?:\.min)?\.js", r"lit-element", r"lit-html", r"@lit"],
            "category": "JavaScript Frameworks",
        },
        "Petite Vue": {
            "patterns": [r"petite-vue", r"PetiteVue"],
            "category": "JavaScript Frameworks",
        },
        "Qwik": {
            "patterns": [r"qwikloader", r"qwik(?:\.min)?\.js", r"on:click", r"preventdefault:click", r"builder\.io/qwik"],
            "version_patterns": [r"qwik@([\d\.]+)"],
            "category": "JavaScript Frameworks",
        },
        "SolidStart": {
            "patterns": [r"solid-start", r"_solidstart", r"solidstart", r"@solidjs/start"],
            "category": "JavaScript Frameworks",
        },
        "Fresh (Deno)": {
            "patterns": [r"fresh-runtime", r"deno\.land/x/fresh", r"__FRSH_STATE"],
            "category": "JavaScript Frameworks",
        },
        "Turbo (Hotwire)": {
            "patterns": [r"turbo-frame", r"turbo-stream", r"@hotwired/turbo", r"Turbo\.session", r"turbo-es2017"],
            "category": "JavaScript Frameworks",
        },
        "Knockout.js": {
            "patterns": [r"knockout(?:\.min)?\.js", r"data-bind"],
            "category": "JavaScript Frameworks",
        },
        "Riot.js": {
            "patterns": [r"riot(?:\.min)?\.js", r"riot@\d[\d\.]*"],
            "category": "JavaScript Frameworks",
        },
        "Aurelia": {
            "patterns": [r"aurelia(?:\.min)?\.js", r"aurelia-app"],
            "category": "JavaScript Frameworks",
        },
        "Marko": {
            "patterns": [r"marko(?:\.min)?\.js", r"\$global\.Marko", r"marko-prettyerror"],
            "category": "JavaScript Frameworks",
        },
    },
    "CSS Frameworks & Libraries": {
        "Bootstrap": {
            "patterns": [
                r"bootstrap(?:\.min)?\.css",
                r"bootstrap(?:\.min)?\.js",
                r"bootstrap\.css",
                r"bootstrap\.bundle",
                r"data-bs-",
                r"carousel-item",
                r"accordion-body",
            ],
            "version_patterns": [r"bootstrap@([\d\.]+)", r"bootstrap-([\d\.]+)", r"Bootstrap\s+v?([\d\.]+)"],
            "category": "CSS Frameworks & Libraries",
        },
        "Tailwind CSS": {
            "patterns": [
                r"tailwind(?:\.min)?\.css",
                r"tailwindcss",
                r"@tailwind",
                r"cdn\.tailwindcss\.com",
                r"(?:hover|focus|dark|sm|md|lg|xl|2xl):[a-z]+-[^\s\"']{2,}",
                r"\b(?:grid-cols|col-span|row-span)-\d",
                r"\b(?:w|h)-(?:px|screen|full|fit)\b",
                r"backdrop-blur",
            ],
            "version_patterns": [r"tailwindcss@([\d\.]+)"],
            "category": "CSS Frameworks & Libraries",
        },
        "Bulma": {
            "patterns": [r"bulma(?:\.min)?\.css", r"bulma\.css", r"is-primary", r"is-info", r"is-success", r"is-warning", r"is-danger", r"columns is-", r"navbar-menu", r"hero is-"],
            "version_patterns": [r"bulma@([\d\.]+)"],
            "category": "CSS Frameworks & Libraries",
        },
        "Foundation": {
            "patterns": [r"foundation(?:\.min)?\.css", r"foundation\.css", r"data-magellan", r"data-sticky-container", r"data-responsive-menu", r"foundation\.js"],
            "category": "CSS Frameworks & Libraries",
        },
        "Materialize CSS": {
            "patterns": [r"materialize(?:\.min)?\.css", r"materialize\.css"],
            "category": "CSS Frameworks & Libraries",
        },
        "Ant Design": {
            "patterns": [r"antd(?:\.min)?\.css", r"antd\.css", r"ant-", r"anticon", r"ant-btn", r"ant-layout", r"ant-menu"],
            "version_patterns": [r"antd@([\d\.]+)"],
            "category": "CSS Frameworks & Libraries",
        },
        "Chakra UI": {
            "patterns": [r"chakra-ui", r"@chakra", r"chakra\.css"],
            "category": "CSS Frameworks & Libraries",
        },
        "Radix UI": {
            "patterns": [r"@radix-ui", r"radix-ui"],
            "category": "CSS Frameworks & Libraries",
        },
        "shadcn/ui": {
            "patterns": [r"shadcn", r"shadcnui", r"cn\(\)", r"lucide-react", r"class-variance-authority", r"tailwind-merge", r"clsx"],
            "category": "CSS Frameworks & Libraries",
        },
        "UnoCSS": {
            "patterns": [r"unocss", r"@unocss"],
            "category": "CSS Frameworks & Libraries",
        },
        "Open Props": {
            "patterns": [r"open-props", r"openprops"],
            "category": "CSS Frameworks & Libraries",
        },
        "Pico CSS": {
            "patterns": [r"picocss", r"pico\..*\.css"],
            "category": "CSS Frameworks & Libraries",
        },
        "Windi CSS": {
            "patterns": [r"windi", r"windi-css"],
            "category": "CSS Frameworks & Libraries",
        },
        "Emotion": {
            "patterns": [r"@emotion", r"emotion-icons", r"emotion-server"],
            "category": "CSS Frameworks & Libraries",
        },
        "Styled Components": {
            "patterns": [r"styled-components", r"styled\..*`"],
            "category": "CSS Frameworks & Libraries",
        },
        "Vuetify": {
            "patterns": [r"vuetify(?:\.min)?\.(?:css|js)", r"v-application--wrap", r"v-toolbar", r"v-navigation-drawer", r"v-main"],
            "version_patterns": [r"vuetify@([\d\.]+)"],
            "category": "CSS Frameworks & Libraries",
        },
        "Quasar": {
            "patterns": [r"quasar(?:\.min)?\.(?:css|js|umd|prod)", r"[\"' ]q-(?:btn|layout|header|drawer|table)"],
            "category": "CSS Frameworks & Libraries",
        },
        "Element Plus": {
            "patterns": [r"element-plus", r"[\"' ]el-(?:button|input|table|dialog)"],
            "category": "CSS Frameworks & Libraries",
        },
        "Naive UI": {
            "patterns": [r"naive-ui", r"[\"' ]n-(?:button|card|layout)", r"--n-[a-z-]+:"],
            "category": "CSS Frameworks & Libraries",
        },
        "Mantine": {
            "patterns": [r"@mantine", r"mantine(?:\.min)?\.css", r"mantine-[a-z0-9]+"],
            "category": "CSS Frameworks & Libraries",
        },
        "PrimeReact": {
            "patterns": [r"primereact", r"primeicons", r"[\"' ]p-component"],
            "category": "CSS Frameworks & Libraries",
        },
        "PrimeVue": {
            "patterns": [r"primevue", r"primeicons", r"[\"' ]p-component"],
            "category": "CSS Frameworks & Libraries",
        },
        "HeroUI (NextUI)": {
            "patterns": [r"@heroui", r"heroui", r"@nextui-org", r"nextui"],
            "category": "CSS Frameworks & Libraries",
        },
        "daisyUI": {
            "patterns": [r"daisyui", r"mockup-browser", r"[\"' ]steps[\"' ].*step-"],
            "category": "CSS Frameworks & Libraries",
        },
        "Flowbite": {
            "patterns": [r"flowbite"],
            "category": "CSS Frameworks & Libraries",
        },
    },
    "Static Site Generators & Bundlers": {
        "Next.js": {
            "patterns": [r"__NEXT_DATA__", r"next/static", r"next/head", r"_next/", r"next\.js", r"__NEXT_REGISTER_PAGE"],
            "version_patterns": [r"next@([\d\.]+)", r"_next/static/chunks/(\d+)", r"\"version\":\"?([\d\.]+)\"?"],
            "category": "Static Site Generators & Bundlers",
        },
        "Nuxt.js": {
            "patterns": [r"__NUXT__", r"nuxt\.js", r"nuxt\.config", r"_nuxt/"],
            "version_patterns": [r"nuxt@([\d\.]+)", r"nuxt/([\d\.]+)"],
            "category": "Static Site Generators & Bundlers",
        },
        "Gatsby": {
            "patterns": [r"___gatsby", r"gatsby-", r"/gatsby/", r"gatsby-image"],
            "version_patterns": [r"gatsby@([\d\.]+)"],
            "category": "Static Site Generators & Bundlers",
        },
        "Hugo": {
            "patterns": [r"generator.*hugo", r"/hugo/", r"hugo-extended", r"powered by hugo"],
            "version_patterns": [r"Hugo\s+([\d\.]+)"],
            "category": "Static Site Generators & Bundlers",
        },
        "Jekyll": {
            "patterns": [r"powered by jekyll", r"generator.*jekyll", r"github-pages.*jekyll"],
            "category": "Static Site Generators & Bundlers",
        },
        "Astro": {
            "patterns": [r"astro-island", r"/_astro/", r"@astrojs", r"astro\.dev"],
            "version_patterns": [r"astro@([\d\.]+)"],
            "category": "Static Site Generators & Bundlers",
        },
        "Vite": {
            "patterns": [r"vite/client", r"@vite", r"__vite__", r"import\.meta\.env"],
            "version_patterns": [r"vite@([\d\.]+)", r"vite/([\d\.]+)"],
            "category": "Static Site Generators & Bundlers",
        },
        "Remix": {
            "patterns": [r"__remixContext", r"@remix-run", r"/build/remix", r"remix-run"],
            "version_patterns": [r"remix@([\d\.]+)"],
            "category": "Static Site Generators & Bundlers",
        },
        "Webpack": {
            "patterns": [r"webpack", r"__webpack_require__", r"webpackJsonp", r"chunk-vendors"],
            "version_patterns": [r"webpack@([\d\.]+)"],
            "category": "Static Site Generators & Bundlers",
        },
        "Parcel": {
            "patterns": [r"parcel-bundler", r"parcelRequire", r"@parcel"],
            "category": "Static Site Generators & Bundlers",
        },
        "Rollup": {
            "patterns": [r"rollup", r"rollup-plugin"],
            "category": "Static Site Generators & Bundlers",
        },
        "ESBuild": {
            "patterns": [r"esbuild", r"esbuild-loader"],
            "category": "Static Site Generators & Bundlers",
        },
        "SvelteKit": {
            "patterns": [r"sveltekit", r"__sveltekit"],
            "version_patterns": [r"sveltekit@([\d\.]+)"],
            "category": "Static Site Generators & Bundlers",
        },
        "Eleventy (11ty)": {
            "patterns": [r"eleventy", r"11ty"],
            "category": "Static Site Generators & Bundlers",
        },
        "Zola": {
            "patterns": [r"generator.*zola", r"powered by zola"],
            "category": "Static Site Generators & Bundlers",
        },
        "Bridgetown": {
            "patterns": [r"bridgetown", r"/_bridgetown/"],
            "category": "Static Site Generators & Bundlers",
        },
        "Docusaurus": {
            "patterns": [r"docusaurus", r"__DOCUSAURUS", r"/docusaurus/"],
            "version_patterns": [r"docusaurus@([\d\.]+)"],
            "category": "Static Site Generators & Bundlers",
        },
        "VuePress": {
            "patterns": [r"vuepress", r"/vuepress/", r"data-v-app.*vuepress"],
            "category": "Static Site Generators & Bundlers",
        },
        "Starlight": {
            "patterns": [r"starlight", r"astro-starlight", r"@astrojs/starlight"],
            "category": "Static Site Generators & Bundlers",
        },
        "MkDocs": {
            "patterns": [r"mkdocs", r"mkdocs-material"],
            "category": "Static Site Generators & Bundlers",
        },
        "Hexo": {
            "patterns": [r"hexo", r"generator.*hexo"],
            "category": "Static Site Generators & Bundlers",
        },
    },
    "CMS": {
        "WordPress": {
            "patterns": [
                r"wp-content",
                r"wp-includes",
                r"wordpress",
                r"wp-json",
                r"wp-admin",
                r"wp-login",
                r"xmlrpc\.php",
                r"wp-emoji",
                r"wp-embed",
                r"wp-block",
                r"wp-block-library",
                r"generator.*wordpress",
            ],
            "version_patterns": [r"generator.*wordpress\s*(\d[\d\.]+)", r"ver=([\d\.]+)"],
            "category": "CMS",
        },
        "WordPress Plugins": {
            "patterns": [
                r"wp-content/plugins/([^/]+)",
                r"wp-content/plugins/",
            ],
            "extract_patterns": [r"wp-content/plugins/([^/\"' ]+)"],
            "category": "CMS",
        },
        "WordPress Themes": {
            "patterns": [
                r"wp-content/themes/([^/]+)",
                r"wp-content/themes/",
            ],
            "extract_patterns": [r"wp-content/themes/([^/\"' ]+)"],
            "category": "CMS",
        },
        "Drupal": {
            "patterns": [r"drupal", r"sites/default/files", r"Drupal\.settings", r"drupalSettings"],
            "version_patterns": [r"Drupal\s+([\d\.]+)", r"drupal/([\d\.]+)"],
            "category": "CMS",
        },
        "Joomla": {
            "patterns": [r"joomla", r"com_content", r"com_contact", r"com_users", r"option=com_"],
            "category": "CMS",
        },
        "Wix": {
            "patterns": [r"wixstatic\.com", r"wix\.com", r"wix-code", r"_wixCssStates"],
            "category": "CMS",
        },
        "Squarespace": {
            "patterns": [r"squarespace", r"sqsp", r"static1\.squarespace", r"squarewebsites"],
            "category": "CMS",
        },
        "Ghost": {
            "patterns": [r"ghost-portal", r"content_api_key", r"generator.*ghost", r"ghost\.min\.js"],
            "version_patterns": [r"Ghost\s+([\d\.]+)"],
            "category": "CMS",
        },
        "Contentful": {
            "patterns": [r"ctfassets\.net", r"contentful\.com", r"contentful"],
            "category": "CMS",
        },
        "Webflow": {
            "patterns": [r"webflow\.(?:js|css)", r"data-wf-", r"assets\.website-files\.com", r"cdn\.prod\.website-files\.com", r"generator.*webflow"],
            "category": "CMS",
        },
        "TYPO3": {
            "patterns": [r"typo3"],
            "category": "CMS",
        },
        "Strapi": {
            "patterns": [r"strapi\.io", r"@strapi", r"/strapi/", r"strapi-plugin"],
            "category": "CMS",
        },
        "Sanity": {
            "patterns": [r"@sanity", r"sanity\.io", r"cdn\.sanity\.io", r"sanity-studio"],
            "category": "CMS",
        },
        "Umbraco": {
            "patterns": [r"umbraco"],
            "category": "CMS",
        },
        "Craft CMS": {
            "patterns": [r"craftcms", r"craft\s+cms"],
            "category": "CMS",
        },
        "Kirby CMS": {
            "patterns": [r"kirby(?:cms)?\.(?:js|css)", r"generator.*kirby", r"media/kirby"],
            "category": "CMS",
        },
        "Statamic": {
            "patterns": [r"statamic", r"/statamic/"],
            "category": "CMS",
        },
        "October CMS": {
            "patterns": [r"octobercms", r"october\s+cms", r"/modules/system/assets"],
            "category": "CMS",
        },
        "ExpressionEngine": {
            "patterns": [r"expressionengine", r"act=expressionengine"],
            "category": "CMS",
        },
        "ProcessWire": {
            "patterns": [r"processwire", r"/site/templates/", r"/site/modules/"],
            "category": "CMS",
        },
        "Silverstripe": {
            "patterns": [r"silverstripe", r"/framework/", r"SilverStripe"],
            "category": "CMS",
        },
        "Prismic": {
            "patterns": [r"prismic", r"images\.prismic\.io", r"@prismicio"],
            "category": "CMS",
        },
        "Storyblok": {
            "patterns": [r"storyblok", r"@storyblok", r"a\.storyblok\.com"],
            "category": "CMS",
        },
        "Payload CMS": {
            "patterns": [r"payloadcms", r"@payloadcms", r"payload-api"],
            "category": "CMS",
        },
        "Directus": {
            "patterns": [r"directus", r"@directus"],
            "category": "CMS",
        },
    },
    "E-commerce": {
        "Shopify": {
            "patterns": [r"shopify", r"cdn\.shopify\.com", r"myshopify\.com", r"Shopify\.", r"x-shopify-"],
            "category": "E-commerce",
        },
        "WooCommerce": {
            "patterns": [r"woocommerce", r"wc-", r"woocommerce-mini-cart", r"add_to_cart", r"wc-block"],
            "version_patterns": [r"WooCommerce\s+([\d\.]+)"],
            "category": "E-commerce",
        },
        "BigCommerce": {
            "patterns": [r"bigcommerce"],
            "category": "E-commerce",
        },
        "Magento": {
            "patterns": [r"magento", r"mage\."],
            "category": "E-commerce",
        },
        "OpenCart": {
            "patterns": [r"opencart", r"route=common/home"],
            "category": "E-commerce",
        },
        "PrestaShop": {
            "patterns": [r"prestashop"],
            "category": "E-commerce",
        },
        "Squarespace Commerce": {
            "patterns": [r"squarespace.*commerce", r"sqsp-cart"],
            "category": "E-commerce",
        },
        "Ecwid": {
            "patterns": [r"ecwid"],
            "category": "E-commerce",
        },
        "Stripe": {
            "patterns": [r"stripe\.com", r"stripe-", r"Stripe\.js", r"pk_(?:live|test)_"],
            "category": "E-commerce",
        },
        "Snipcart": {
            "patterns": [r"snipcart"],
            "category": "E-commerce",
        },
        "Gumroad": {
            "patterns": [r"gumroad"],
            "category": "E-commerce",
        },
        "Lemon Squeezy": {
            "patterns": [r"lemonsqueezy", r"lmsq"],
            "category": "E-commerce",
        },
        "Medusa": {
            "patterns": [r"medusa-js", r"@medusajs", r"store\.medusa"],
            "category": "E-commerce",
        },
        "Saleor": {
            "patterns": [r"saleor", r"@saleor"],
            "category": "E-commerce",
        },
        "Shopify Hydrogen": {
            "patterns": [r"@shopify/hydrogen", r"shopify-hydrogen", r"hydrogen-shopify"],
            "category": "E-commerce",
        },
    },
    "Analytics & Marketing": {
        "Google Analytics": {
            "patterns": [
                r"google-analytics\.com",
                r"gtag\s*\(",
                r"ga\.js",
                r"analytics\.js.*google",
                r"gtag/js\?id=G-[A-Z0-9]+",
                r"G-[A-Z0-9]{8,}",
                r"UA-\d+-\d+",
                r"ga\(",
                r"gaq\.push",
                r"_gaq",
                r"google_tag_manager",
            ],
            "version_patterns": [r"analytics\.js.*v=([\w\.]+)"],
            "category": "Analytics & Marketing",
        },
        "Google Tag Manager": {
            "patterns": [r"googletagmanager\.com", r"gtm\.js", r"GTM-[A-Z0-9]+", r"dataLayer"],
            "category": "Analytics & Marketing",
        },
        "Facebook Pixel": {
            "patterns": [r"fbevents\.js", r"facebook\.com/tr", r"fbq\("],
            "category": "Analytics & Marketing",
        },
        "Hotjar": {
            "patterns": [r"hotjar\.com", r"_hjSettings", r"hj\("],
            "category": "Analytics & Marketing",
        },
        "Mixpanel": {
            "patterns": [r"cdn\.mxpnl\.com", r"mixpanel\.com", r"mixpanel\.track", r"window\.mixpanel"],
            "category": "Analytics & Marketing",
        },
        "Segment": {
            "patterns": [r"cdn\.segment\.com", r"segment\.io/analytics", r"analytics\.load\("],
            "category": "Analytics & Marketing",
        },
        "Plausible": {
            "patterns": [r"plausible\.io", r"plausible"],
            "category": "Analytics & Marketing",
        },
        "Matomo": {
            "patterns": [r"matomo", r"piwik"],
            "category": "Analytics & Marketing",
        },
        "Amplitude": {
            "patterns": [r"amplitude\.com", r"amplitude(?:\.min)?\.js", r"window\.amplitude"],
            "category": "Analytics & Marketing",
        },
        "Heap": {
            "patterns": [r"heapanalytics\.com", r"heap\.app"],
            "category": "Analytics & Marketing",
        },
        "FullStory": {
            "patterns": [r"fullstory\.com", r"_fs_ready", r"window\.FS"],
            "category": "Analytics & Marketing",
        },
        "Microsoft Clarity": {
            "patterns": [r"clarity\.ms", r"\(function\(c,l,a,r,i,e,t,y\)"],
            "category": "Analytics & Marketing",
        },
        "LinkedIn Insight Tag": {
            "patterns": [r"linkedin\.com/trk", r"_linkedin"],
            "category": "Analytics & Marketing",
        },
        "Twitter Pixel": {
            "patterns": [r"static\.ads-twitter\.com", r"\btwq\("],
            "category": "Analytics & Marketing",
        },
        "Reddit Pixel": {
            "patterns": [r"redditstatic\.com/ads", r"\brtq\("],
            "category": "Analytics & Marketing",
        },
        "HubSpot": {
            "patterns": [r"hubspot", r"hs-analytics", r"hs-script"],
            "category": "Analytics & Marketing",
        },
        "Intercom": {
            "patterns": [r"intercomcdn\.com", r"widget\.intercom\.io", r"intercom\.io", r"window\.Intercom"],
            "category": "Analytics & Marketing",
        },
        "Crisp Chat": {
            "patterns": [r"crisp\.chat", r"window\.\$crisp", r"Crisp\("],
            "category": "Analytics & Marketing",
        },
        "Tidio": {
            "patterns": [r"code\.tidio\.co", r"tidio\.co"],
            "category": "Analytics & Marketing",
        },
        "Drift": {
            "patterns": [r"drift\.com/embed", r"driftt\.com", r"window\.drift", r"drift-widget"],
            "category": "Analytics & Marketing",
        },
        "Mouseflow": {
            "patterns": [r"cdn\.mouseflow\.com", r"mouseflow\.com"],
            "category": "Analytics & Marketing",
        },
        "Crazy Egg": {
            "patterns": [r"script\.crazyegg\.com", r"crazyegg\.com"],
            "category": "Analytics & Marketing",
        },
        "VWO": {
            "patterns": [r"visualwebsiteoptimizer\.com", r"vwo\.com", r"window\.VWO"],
            "category": "Analytics & Marketing",
        },
        "Optimizely": {
            "patterns": [r"cdn\.optimizely\.com", r"optimizely\.com", r"window\.optimizely"],
            "category": "Analytics & Marketing",
        },
        "Google Ads": {
            "patterns": [r"googleads", r"googlesyndication", r"pagead2\.googlesyndication"],
            "category": "Analytics & Marketing",
        },
    },
    "Web Servers": {
        "Nginx": {
            "patterns": [r"nginx"],
            "version_patterns": [r"nginx/([\d\.]+)"],
            "category": "Web Servers",
        },
        "Apache": {
            "patterns": [r"apache"],
            "version_patterns": [r"Apache/([\d\.]+)"],
            "category": "Web Servers",
        },
        "LiteSpeed": {
            "patterns": [r"litespeed"],
            "version_patterns": [r"LiteSpeed\s*([\d\.]+)"],
            "category": "Web Servers",
        },
        "IIS": {
            "patterns": [r"Microsoft-IIS"],
            "version_patterns": [r"Microsoft-IIS/([\d\.]+)"],
            "category": "Web Servers",
        },
        "Caddy": {
            "patterns": [r"caddy"],
            "version_patterns": [r"Caddy/([\d\.]+)"],
            "category": "Web Servers",
        },
        "Cloudflare Server": {
            "patterns": [r"cloudflare"],
            "category": "Web Servers",
        },
        "OpenResty": {
            "patterns": [r"openresty"],
            "category": "Web Servers",
        },
        "Tomcat": {
            "patterns": [r"tomcat", r"Tomcat"],
            "version_patterns": [r"Tomcat/([\d\.]+)"],
            "category": "Web Servers",
        },
    },
    "Programming Languages & Runtimes": {
        "PHP": {
            "patterns": [r"\.php", r"x-powered-by.*php", r"PHP/", r"wp-content"],
            "version_patterns": [r"PHP/([\d\.]+)", r"x-powered-by.*PHP/([\d\.]+)"],
            "category": "Programming Languages & Runtimes",
        },
        "Python": {
            "patterns": [r"Python/", r"wsgi", r"pythonanywhere", r"x-powered-by.*python"],
            "version_patterns": [r"Python/([\d\.]+)"],
            "category": "Programming Languages & Runtimes",
        },
        "Ruby": {
            "patterns": [r"X-Ruby-Version", r"phusion passenger", r"ruby-lang", r"x-request-id.*rack"],
            "version_patterns": [r"Ruby\s*([\d\.]+)"],
            "category": "Programming Languages & Runtimes",
        },
        "Node.js": {
            "patterns": [r"node\.js", r"x-powered-by.*node", r"next-server", r"__node"],
            "version_patterns": [r"Node\.?js?/([\d\.]+)", r"node/([\d\.]+)"],
            "category": "Programming Languages & Runtimes",
        },
        ".NET": {
            "patterns": [r"asp\.net", r"dotnet", r"\.aspx", r"\.ashx", r"\.asmx", r"__VIEWSTATE", r"__EVENTVALIDATION"],
            "version_patterns": [r"X-AspNet-Version: ([\d\.]+)", r"\.NET\s+([\d\.]+)"],
            "category": "Programming Languages & Runtimes",
        },
        "Java": {
            "patterns": [r"servlet", r"\bjsp\b", r"JVM", r"x-powered-by.*(?:java|jsp|servlet)"],
            "version_patterns": [r"Java\s*([\d\._]+)"],
            "category": "Programming Languages & Runtimes",
        },
        "Go": {
            "patterns": [r"golang", r"go\s+version"],
            "category": "Programming Languages & Runtimes",
        },
        "Rust": {
            "patterns": [r"\brust\b"],
            "category": "Programming Languages & Runtimes",
        },
        "Django": {
            "patterns": [r"django", r"csrftoken", r"__django"],
            "version_patterns": [r"Django\s+([\d\.]+)", r"django/([\d\.]+)"],
            "category": "Programming Languages & Runtimes",
        },
        "Flask": {
            "patterns": [r"werkzeug", r"jinja2", r"x-powered-by.*flask", r"flask-session"],
            "category": "Programming Languages & Runtimes",
        },
        "Ruby on Rails": {
            "patterns": [r"rails", r"<%= ", r"<% ", r"csrf-param"],
            "version_patterns": [r"Rails\s+([\d\.]+)"],
            "category": "Programming Languages & Runtimes",
        },
        "Express": {
            "patterns": [r"x-powered-by.*express", r"express-session", r"express-validator", r"etag.*x-powered"],
            "version_patterns": [r"Express\s*([\d\.]+)"],
            "category": "Programming Languages & Runtimes",
        },
        "FastAPI": {
            "patterns": [r"fastapi"],
            "category": "Programming Languages & Runtimes",
        },
        "Deno": {
            "patterns": [r"deno"],
            "category": "Programming Languages & Runtimes",
        },
        "Bun": {
            "patterns": [r"bun\.sh", r"bun@\d[\d\.]*", r"node_modules/bun", r"\bBun\s+v?\d"],
            "category": "Programming Languages & Runtimes",
        },
    },
    "Hosting & CDN": {
        "Cloudflare": {
            "patterns": [r"cloudflare", r"cf-ray", r"__cfduid", r"_cfuvid"],
            "category": "Hosting & CDN",
        },
        "AWS": {
            "patterns": [r"amazonaws\.com", r"aws", r"aws-", r"s3\.", r"ec2-", r"cloudfront"],
            "category": "Hosting & CDN",
        },
        "Netlify": {
            "patterns": [r"netlify", r"x-nf-", r"Netlify"],
            "category": "Hosting & CDN",
        },
        "Vercel": {
            "patterns": [r"vercel", r"now\.sh", r"x-vercel"],
            "category": "Hosting & CDN",
        },
        "Google Cloud": {
            "patterns": [r"googleapis\.com", r"gcp", r"googlecloud", r"storage\.googleapis"],
            "category": "Hosting & CDN",
        },
        "Azure": {
            "patterns": [r"azure", r"azurewebsites", r"azureedge"],
            "category": "Hosting & CDN",
        },
        "Heroku": {
            "patterns": [r"herokuapp\.com", r"heroku"],
            "category": "Hosting & CDN",
        },
        "GitHub Pages": {
            "patterns": [r"github\.io", r"github-pages"],
            "category": "Hosting & CDN",
        },
        "GitLab Pages": {
            "patterns": [r"gitlab\.io"],
            "category": "Hosting & CDN",
        },
        "Cloudflare Pages": {
            "patterns": [r"pages\.dev", r"cloudflare-pages"],
            "category": "Hosting & CDN",
        },
        "Railway": {
            "patterns": [r"railway\.app"],
            "category": "Hosting & CDN",
        },
        "Render": {
            "patterns": [r"onrender\.com"],
            "category": "Hosting & CDN",
        },
        "Fastly": {
            "patterns": [r"fastly"],
            "category": "Hosting & CDN",
        },
        "Akamai": {
            "patterns": [r"akamai"],
            "category": "Hosting & CDN",
        },
        "KeyCDN": {
            "patterns": [r"keycdn"],
            "category": "Hosting & CDN",
        },
        "CloudFront": {
            "patterns": [r"cloudfront\.net", r"cloudfront"],
            "category": "Hosting & CDN",
        },
        "bunny.net": {
            "patterns": [r"bunnycdn", r"bunny\.net"],
            "category": "Hosting & CDN",
        },
        "jsDelivr": {
            "patterns": [r"cdn\.jsdelivr\.net"],
            "category": "Hosting & CDN",
        },
        "unpkg": {
            "patterns": [r"unpkg\.com"],
            "category": "Hosting & CDN",
        },
        "cdnjs": {
            "patterns": [r"cdnjs\.cloudflare\.com"],
            "category": "Hosting & CDN",
        },
    },
    "UI Libraries & Components": {
        "Material UI": {
            "patterns": [r"@mui", r"material-ui", r"MUI", r"makeStyles", r"withStyles"],
            "version_patterns": [r"@mui/material@([\d\.]+)"],
            "category": "UI Libraries & Components",
        },
        "Radix UI": {
            "patterns": [r"@radix-ui"],
            "category": "UI Libraries & Components",
        },
        "Headless UI": {
            "patterns": [r"@headlessui", r"headlessui"],
            "category": "UI Libraries & Components",
        },
        "Framer Motion": {
            "patterns": [r"framer-motion", r"framer\.com/motion"],
            "version_patterns": [r"framer-motion@([\d\.]+)"],
            "category": "UI Libraries & Components",
        },
        "GSAP": {
            "patterns": [r"gsap(?:\.min)?\.js", r"gsap\.js", r"greensock", r"TweenMax", r"TimelineMax"],
            "version_patterns": [r"GSAP\s+([\d\.]+)"],
            "category": "UI Libraries & Components",
        },
        "Three.js": {
            "patterns": [r"three(?:\.min)?\.js", r"three\.js", r"THREE\."],
            "version_patterns": [r"three@([\d\.]+)", r"Three\.js\s+r?([\d\.]+)"],
            "category": "UI Libraries & Components",
        },
        "D3.js": {
            "patterns": [r"d3(?:\.min)?\.js", r"d3\.v", r"d3\."],
            "version_patterns": [r"d3@([\d\.]+)"],
            "category": "UI Libraries & Components",
        },
        "Chart.js": {
            "patterns": [r"chart(?:\.min)?\.js", r"Chart\.js", r"Chart\s*\("],
            "version_patterns": [r"chart\.js@([\d\.]+)", r"Chart\.js\s+v?([\d\.]+)"],
            "category": "UI Libraries & Components",
        },
        "ECharts": {
            "patterns": [r"echarts(?:\.min)?\.js", r"echarts"],
            "category": "UI Libraries & Components",
        },
        "Anime.js": {
            "patterns": [r"anime(?:\.min)?\.js"],
            "category": "UI Libraries & Components",
        },
        "Swiper": {
            "patterns": [r"swiper(?:\.min)?\.js", r"swiper\.js", r"swiper-bundle"],
            "version_patterns": [r"Swiper@([\d\.]+)", r"swiper/([\d\.]+)"],
            "category": "UI Libraries & Components",
        },
        "React Router": {
            "patterns": [r"react-router", r"ReactRouter"],
            "category": "UI Libraries & Components",
        },
        "React Query": {
            "patterns": [r"react-query", r"@tanstack/react-query"],
            "category": "UI Libraries & Components",
        },
        "Redux": {
            "patterns": [r"redux", r"Redux", r"__REDUX"],
            "category": "UI Libraries & Components",
        },
        "Zustand": {
            "patterns": [r"zustand"],
            "category": "UI Libraries & Components",
        },
        "Pinia": {
            "patterns": [r"pinia"],
            "category": "UI Libraries & Components",
        },
        "Vuex": {
            "patterns": [r"vuex"],
            "category": "UI Libraries & Components",
        },
        "Prism.js": {
            "patterns": [r"prism(?:\.min)?\.js", r"prism\.css"],
            "category": "UI Libraries & Components",
        },
        "Highlight.js": {
            "patterns": [r"highlight(?:\.min)?\.js", r"highlight\.js", r"hljs"],
            "category": "UI Libraries & Components",
        },
        "AOS": {
            "patterns": [r"aos\.js", r"aos\.css", r"data-aos"],
            "category": "UI Libraries & Components",
        },
        "Lodash": {
            "patterns": [r"lodash(?:\.min)?\.js", r"lodash\.js", r"_\.(?:debounce|throttle|cloneDeep)"],
            "version_patterns": [r"lodash@([\d\.]+)"],
            "category": "UI Libraries & Components",
        },
        "Moment.js": {
            "patterns": [r"moment(?:\.min)?\.js", r"moment\.js", r"moment-timezone"],
            "version_patterns": [r"moment@([\d\.]+)"],
            "category": "UI Libraries & Components",
        },
        "Day.js": {
            "patterns": [r"dayjs", r"day\.js"],
            "category": "UI Libraries & Components",
        },
        "date-fns": {
            "patterns": [r"date-fns"],
            "category": "UI Libraries & Components",
        },
        "Axios": {
            "patterns": [r"axios(?:\.min)?\.js", r"axios"],
            "category": "UI Libraries & Components",
        },
        "Socket.io": {
            "patterns": [r"socket\.io", r"io\("],
            "category": "UI Libraries & Components",
        },
        "Font Awesome": {
            "patterns": [r"fontawesome", r"font-awesome", r"fa-", r"fa[srldb]?\s+fa-"],
            "version_patterns": [r"FontAwesome\s+([\d\.]+)", r"font-awesome@([\d\.]+)"],
            "category": "UI Libraries & Components",
        },
        "Google Fonts": {
            "patterns": [r"fonts\.googleapis\.com", r"fonts\.gstatic\.com"],
            "category": "UI Libraries & Components",
        },
        "Adobe Fonts": {
            "patterns": [r"typekit", r"use\.typekit\.net", r"p.typekit"],
            "category": "UI Libraries & Components",
        },
        "Lucide Icons": {
            "patterns": [r"lucide-react", r"lucide-vue", r"lucide"],
            "category": "UI Libraries & Components",
        },
        "Heroicons": {
            "patterns": [r"heroicons"],
            "category": "UI Libraries & Components",
        },
        "Material Symbols & Icons": {
            "patterns": [r"material-symbols", r"material-icons", r"Material\+Icons", r"Material\+Symbols"],
            "category": "UI Libraries & Components",
        },
        "Ionicons": {
            "patterns": [r"ionicons", r"<ion-icon"],
            "category": "UI Libraries & Components",
        },
        "Tabler Icons": {
            "patterns": [r"@tabler/icons", r"tabler-icons", r"[\"' ]ti ti-"],
            "category": "UI Libraries & Components",
        },
        "Phosphor Icons": {
            "patterns": [r"@phosphor-icons", r"phosphoricons", r"[\"' ]ph ph-", r"[\"' ]ph-[a-z]+-light"],
            "category": "UI Libraries & Components",
        },
        "Remix Icon": {
            "patterns": [r"remixicon", r"[\"' ]ri-[a-z0-9]+-(?:line|fill)"],
            "category": "UI Libraries & Components",
        },
        "Bootstrap Icons": {
            "patterns": [r"bootstrap-icons", r"[\"' ]bi-[a-z0-9]"],
            "category": "UI Libraries & Components",
        },
        "Feather Icons": {
            "patterns": [r"feather-icons", r"feather(?:\.min)?\.js", r"data-feather"],
            "category": "UI Libraries & Components",
        },
        "Boxicons": {
            "patterns": [r"boxicons", r"[\"' ]bx[bxs]? [lb]-"],
            "category": "UI Libraries & Components",
        },
        "Iconify": {
            "patterns": [r"iconify", r"@iconify", r"<iconify-icon"],
            "category": "UI Libraries & Components",
        },
    },
    "Security": {
        "reCAPTCHA": {
            "patterns": [r"recaptcha", r"grecaptcha", r"google\.com/recaptcha"],
            "category": "Security",
        },
        "hCaptcha": {
            "patterns": [r"hcaptcha", r"hcaptcha\.com"],
            "category": "Security",
        },
        "Cloudflare Turnstile": {
            "patterns": [r"turnstile", r"challenges\.cloudflare\.com"],
            "category": "Security",
        },
        "CSP": {
            "patterns": [r"content-security-policy", r"Content-Security-Policy"],
            "category": "Security",
        },
        "HSTS": {
            "patterns": [r"strict-transport-security", r"Strict-Transport-Security"],
            "category": "Security",
        },
        "CORS": {
            "patterns": [r"access-control-allow-origin", r"Access-Control-Allow-Origin"],
            "category": "Security",
        },
        "Sucuri": {
            "patterns": [r"sucuri"],
            "category": "Security",
        },
        "Wordfence": {
            "patterns": [r"wordfence"],
            "category": "Security",
        },
        "ModSecurity": {
            "patterns": [r"mod_security", r"ModSecurity"],
            "category": "Security",
        },
    },
    "Features & Standards": {
        "Schema.org": {
            "patterns": [r"schema\.org", r"application/ld\+json"],
            "category": "Features & Standards",
        },
        "Open Graph": {
            "patterns": [r"og:title", r"og:description", r"og:image", r"og:url", r"og:type", r"og:site_name", r"property=\"og:"],
            "category": "Features & Standards",
        },
        "Twitter Cards": {
            "patterns": [r"twitter:card", r"twitter:site", r"twitter:creator", r"name=\"twitter:"],
            "category": "Features & Standards",
        },
        "PWA": {
            "patterns": [r"manifest\.json", r"service-worker", r"serviceWorker", r"display:\s*'?standalone'?"],
            "category": "Features & Standards",
        },
        "GraphQL": {
            "patterns": [r"/graphql", r"graphql", r"__typename", r"apollo-client"],
            "category": "Features & Standards",
        },
        "REST API": {
            "patterns": [r"/api/v\d", r"application/vnd\.api", r"x-api-key", r"api-version"],
            "category": "Features & Standards",
        },
        "Lazy Loading": {
            "patterns": [r"loading=\"?lazy\"?", r"loading=\"?eager\"?"],
            "category": "Features & Standards",
        },
        "Preload": {
            "patterns": [r"rel=\"?preload\"?", r"rel=\"?prefetch\"?", r"rel=\"?preconnect\"?"],
            "category": "Features & Standards",
        },
        "Microdata": {
            "patterns": [r"itemscope", r"itemprop", r"itemtype"],
            "category": "Features & Standards",
        },
        "RSS Feed": {
            "patterns": [r"application/rss\+xml", r"application/atom\+xml", r"/feed\.xml", r"/rss\.xml", r"/atom\.xml"],
            "category": "Features & Standards",
        },
        "Sitemap": {
            "patterns": [r"rel=\"sitemap\"", r"urlset", r"sitemapindex"],
            "category": "Features & Standards",
        },
        "Robots.txt": {
            "patterns": [r"robots\.txt"],
            "category": "Features & Standards",
        },
        "Meta Viewport": {
            "patterns": [r"name=\"?viewport\"?"],
            "category": "Features & Standards",
        },
        "CSS Custom Properties": {
            "patterns": [r"--[\w-]+:"],
            "category": "Features & Standards",
        },
        "HTTP/2": {
            "patterns": [r"http2", r"http/2", r"h2-\d+"],
            "category": "Features & Standards",
        },
        "HTTP/3": {
            "patterns": [r"http3", r"http/3", r"alt-svc"],
            "category": "Features & Standards",
        },
    },
    "Databases": {
        "MySQL": {
            "patterns": [r"mysql", r"mysqli"],
            "category": "Databases",
        },
        "PostgreSQL": {
            "patterns": [r"postgresql", r"postgres", r"pgsql"],
            "category": "Databases",
        },
        "MongoDB": {
            "patterns": [r"mongodb", r"mongo"],
            "category": "Databases",
        },
        "Redis": {
            "patterns": [r"redis"],
            "category": "Databases",
        },
        "Elasticsearch": {
            "patterns": [r"elasticsearch", r"elastic"],
            "category": "Databases",
        },
        "Firebase": {
            "patterns": [r"firebase", r"firebaseio\.com", r"firestore"],
            "category": "Databases",
        },
        "Supabase": {
            "patterns": [r"supabase"],
            "category": "Databases",
        },
        "SQLite": {
            "patterns": [r"sqlite"],
            "category": "Databases",
        },
        "Prisma": {
            "patterns": [r"prisma"],
            "category": "Databases",
        },
    },
    "DevOps & CI/CD": {
        "Docker": {
            "patterns": [r"docker\.io", r"docker-compose", r"Dockerfile", r"containerd"],
            "category": "DevOps & CI/CD",
        },
        "Kubernetes": {
            "patterns": [r"kubernetes\.io", r"k8s\.io", r"x-kubernetes"],
            "category": "DevOps & CI/CD",
        },
        "GitHub Actions": {
            "patterns": [r"github\.com/.*/actions", r"github\.actions"],
            "category": "DevOps & CI/CD",
        },
        "CircleCI": {
            "patterns": [r"circleci", r"circle\.ci"],
            "category": "DevOps & CI/CD",
        },
        "Travis CI": {
            "patterns": [r"travis-ci"],
            "category": "DevOps & CI/CD",
        },
        "Jenkins": {
            "patterns": [r"jenkins"],
            "category": "DevOps & CI/CD",
        },
        "Sentry": {
            "patterns": [r"sentry\.io", r"browser\.sentry-cdn\.com", r"@sentry", r"Sentry\.init"],
            "category": "DevOps & CI/CD",
        },
        "Datadog": {
            "patterns": [r"datadog(?:hq)?\.com", r"DD_RUM", r"dd-api-root"],
            "category": "DevOps & CI/CD",
        },
        "New Relic": {
            "patterns": [r"newrelic", r"new-relic"],
            "category": "DevOps & CI/CD",
        },
    },
}


class TechnologyDetector:
    """Detects web technologies from HTML content and HTTP headers."""

    def __init__(self):
        self.patterns = TECHNOLOGY_PATTERNS

    def detect_all(self, html: str, soup: BeautifulSoup, http_headers: Dict[str, str]) -> Dict[str, list]:
        """
        Run all detection methods and return combined results with evidence and versions.

        Args:
            html: Raw HTML content
            soup: Parsed BeautifulSoup object
            http_headers: HTTP response headers

        Returns:
            Dictionary of category -> list of dicts with tech name, version, evidence, confidence
        """
        results: Dict[str, list] = {}

        # Detect from HTML content
        html_detections = self._detect_from_html(html, soup)
        results = html_detections

        # Detect from HTTP headers
        header_detections = self._detect_from_headers(http_headers)
        if header_detections:
            results.setdefault("Server Headers", []).extend(header_detections)

        # Deduplicate
        for category in results:
            seen = set()
            unique = []
            for item in results[category]:
                key = item["name"]
                if key not in seen:
                    seen.add(key)
                    unique.append(item)
            results[category] = unique

        return results

    def _detect_from_html(self, html: str, soup: BeautifulSoup) -> Dict[str, list]:
        """Detect technologies by pattern matching against HTML source."""
        detected: Dict[str, list] = {}

        for category, techs in self.patterns.items():
            category_matches = []

            for tech_name, tech_info in techs.items():
                patterns = tech_info.get("patterns", [])
                version_patterns = tech_info.get("version_patterns", [])
                extract_patterns = tech_info.get("extract_patterns", [])
                matched = False
                evidence = []
                version = None
                confidence = "low"

                for pattern in patterns:
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    if matches:
                        matched = True
                        if len(matches) > 3:
                            confidence = "high"
                        elif len(matches) > 1:
                            confidence = "medium"
                        evidence.append(pattern)

                # Try to extract version
                if matched and version_patterns:
                    for vp in version_patterns:
                        v_match = re.search(vp, html, re.IGNORECASE)
                        if v_match:
                            version = v_match.group(1)
                            confidence = "high"
                            break

                # For extract_patterns (like WordPress plugins), extract names
                extracted_items = []
                if matched and extract_patterns:
                    for ep in extract_patterns:
                        for match in re.finditer(ep, html, re.IGNORECASE):
                            extracted_items.append(match.group(1))

                if matched:
                    entry = {
                        "name": tech_name,
                        "version": version,
                        "confidence": confidence,
                        "evidence_count": len(evidence),
                    }
                    if extracted_items:
                        entry["items"] = list(set(extracted_items))  # deduplicate
                    category_matches.append(entry)

            if category_matches:
                detected[category] = category_matches

        # Sort by confidence within each category (high first)
        for category in detected:
            confidence_order = {"high": 0, "medium": 1, "low": 2}
            detected[category].sort(key=lambda x: (confidence_order.get(x.get("confidence", "low"), 3), x["name"]))

        return detected

    def _detect_from_headers(self, headers: Dict[str, str]) -> list:
        """Detect technologies from HTTP response headers."""
        techs = []

        header_checks = {
            "x-powered-by": [
                {"re": r"php", "name": "PHP", "version_re": r"PHP/([\d\.]+)"},
                {"re": r"asp\.net", "name": "ASP.NET", "version_re": None},
                {"re": r"express", "name": "Express", "version_re": None},
                {"re": r"django", "name": "Django", "version_re": None},
                {"re": r"rails", "name": "Ruby on Rails", "version_re": None},
                {"re": r"next\.js", "name": "Next.js", "version_re": None},
                {"re": r"liferay", "name": "Liferay", "version_re": None},
            ],
            "server": [
                {"re": r"nginx", "name": "Nginx", "version_re": r"nginx/([\d\.]+)"},
                {"re": r"apache", "name": "Apache", "version_re": r"Apache/([\d\.]+)"},
                {"re": r"litespeed", "name": "LiteSpeed", "version_re": r"LiteSpeed\s*([\d\.]+)"},
                {"re": r"microsoft-iis", "name": "IIS", "version_re": r"Microsoft-IIS/([\d\.]+)"},
                {"re": r"caddy", "name": "Caddy", "version_re": r"Caddy/([\d\.]+)"},
                {"re": r"gunicorn", "name": "Gunicorn", "version_re": r"Gunicorn/([\d\.]+)"},
                {"re": r"uvicorn", "name": "Uvicorn", "version_re": r"uvicorn/([\d\.]+)"},
                {"re": r"envoy", "name": "Envoy", "version_re": None},
                {"re": r"traefik", "name": "Traefik", "version_re": None},
                {"re": r"kestrel", "name": "Kestrel", "version_re": None},
            ],
            "cf-ray": [{"re": None, "name": "Cloudflare", "version_re": None}],
            "cf-cache-status": [{"re": None, "name": "Cloudflare Cache", "version_re": None}],
            "x-vercel-id": [{"re": None, "name": "Vercel", "version_re": None}],
            "x-nf-request-id": [{"re": None, "name": "Netlify", "version_re": None}],
            "x-amz-cf-id": [{"re": None, "name": "AWS CloudFront", "version_re": None}],
            "x-fastly-request-id": [{"re": None, "name": "Fastly", "version_re": None}],
            "x-shopify-stage": [{"re": None, "name": "Shopify", "version_re": None}],
            "x-github-request-id": [{"re": None, "name": "GitHub", "version_re": None}],
            "x-drupal-cache": [{"re": None, "name": "Drupal", "version_re": None}],
            "x-varnish": [{"re": None, "name": "Varnish", "version_re": None}],
            "x-envoy-upstream-service-time": [{"re": None, "name": "Envoy Proxy", "version_re": None}],
            "via": [{"re": r"varnish", "name": "Varnish", "version_re": None},
                    {"re": r"squid", "name": "Squid", "version_re": None}],
        }

        seen = set()

        def _emit(name, version, header):
            if name and name not in seen:
                seen.add(name)
                techs.append({
                    "name": name,
                    "version": version,
                    "confidence": "high",
                    "evidence_count": 1,
                    "from_header": header,
                })

        for header, checks in header_checks.items():
            if header not in headers:
                continue
            value = headers.get(header, "")
            if not isinstance(value, str):
                continue
            for info in checks:
                # re=None means mere presence of the header is the signal;
                # otherwise match the regex against the header value.
                if info["re"] is not None and not re.search(info["re"], value, re.IGNORECASE):
                    continue
                version = None
                if info["version_re"]:
                    vm = re.search(info["version_re"], value, re.IGNORECASE)
                    if vm:
                        version = vm.group(1)
                _emit(info["name"], version, header)

        return techs

    def _extract_header_version(self, tech: str, header_value: str) -> Optional[str]:
        """Extract version from header value."""
        version_map = {
            "php": r"PHP/([\d\.]+)",
            "nginx": r"nginx/([\d\.]+)",
            "asp.net": r"([\d\.]+)",
        }
        if tech in version_map:
            match = re.search(version_map[tech], header_value, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def detect_meta_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract technology hints from meta tags."""
        meta_info = {}

        if not soup:
            return meta_info

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
            elif "author" in name:
                meta_info["Author"] = content
            elif "keywords" in name:
                meta_info["Keywords"] = content[:200] + "..." if len(content) > 200 else content
            elif "description" in name:
                meta_info["Description"] = content[:200] + "..." if len(content) > 200 else content
            elif "robots" in name:
                meta_info["Robots"] = content
            elif "language" in name:
                meta_info["Language"] = content

        # HTML lang attribute
        if soup.html and soup.html.get("lang"):
            meta_info["HTML Language"] = soup.html["lang"]

        # Character encoding
        charset = soup.find("meta", charset=True)
        if charset:
            meta_info["Charset"] = charset.get("charset", "")

        return meta_info

    def detect_json_ld(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract JSON-LD structured data."""
        json_ld_data = []

        if not soup:
            return json_ld_data

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                raw_data = script.string or script.get_text()
                data = json.loads(raw_data)
                if isinstance(data, list):
                    json_ld_data.extend(item for item in data if isinstance(item, dict))
                elif isinstance(data, dict):
                    json_ld_data.append(data)
            except (json.JSONDecodeError, TypeError):
                pass

        return json_ld_data

    def extract_server_info(self, http_headers: Dict[str, str]) -> Dict[str, str]:
        """Extract server information from HTTP headers."""
        server_info = {}

        header_mapping = {
            "server": "Server",
            "x-powered-by": "Powered By",
            "x-aspnet-version": "ASP.NET Version",
            "x-frame-options": "X-Frame-Options",
            "x-content-type-options": "X-Content-Type-Options",
            "x-xss-protection": "X-XSS-Protection",
            "referrer-policy": "Referrer Policy",
            "permissions-policy": "Permissions Policy",
            "content-security-policy": "Content Security Policy",
            "cache-control": "Cache Control",
            "content-type": "Content Type",
        }

        for header, label in header_mapping.items():
            if header in http_headers:
                value = http_headers[header]
                if len(value) > 100:
                    value = value[:100] + "..."
                server_info[label] = value

        # Detect CDN
        if "cf-ray" in http_headers:
            server_info["CDN"] = "Cloudflare"
        if "x-amz-cf-id" in http_headers:
            server_info["CDN"] = "CloudFront"
        if "x-fastly-request-id" in http_headers:
            server_info["CDN"] = "Fastly"

        return server_info

    def extract_performance_metrics(self, html: str, http_headers: Dict[str, str], elapsed: float) -> Dict:
        """Extract performance-related metrics."""
        metrics = {}

        # Page size
        page_size_bytes = len(html.encode("utf-8"))
        metrics["page_size"] = page_size_bytes
        metrics["page_size_formatted"] = self._format_size(page_size_bytes)

        # Response time
        metrics["response_time_ms"] = round(elapsed * 1000, 2)

        # Compression
        content_encoding = http_headers.get("content-encoding", "")
        metrics["compression"] = content_encoding if content_encoding else "None"

        # Script count
        metrics["script_count"] = len(re.findall(r'<script', html, re.IGNORECASE))
        metrics["stylesheet_count"] = len(re.findall(r'<link[^>]*rel="?stylesheet"?' , html, re.IGNORECASE))
        metrics["image_count"] = len(re.findall(r'<img', html, re.IGNORECASE))

        # Total requests estimate (from resource hints)
        preloads = len(re.findall(r'rel="?preload"?', html, re.IGNORECASE))
        prefetches = len(re.findall(r'rel="?prefetch"?', html, re.IGNORECASE))
        metrics["resource_hints"] = preloads + prefetches

        return metrics

    def analyze_cookies(self, cookies: Dict[str, str]) -> List[Dict]:
        """Analyze cookies for technology hints."""
        findings = []

        cookie_indicators = {
            "PHPSESSID": "PHP Session",
            "wordpress_": "WordPress",
            "wp-settings": "WordPress",
            "shopify": "Shopify",
            "_ga": "Google Analytics",
            "_gid": "Google Analytics",
            "_fbp": "Facebook Pixel",
            "cfduid": "Cloudflare",
            "__cfduid": "Cloudflare",
            "AWSALB": "AWS Load Balancer",
            "laravel_session": "Laravel",
            "XSRF-TOKEN": "Laravel",
            "django": "Django",
            "sessionid": "Django",
            "csrftoken": "Django",
            "connect.sid": "Express",
            "JSESSIONID": "Java/JSP",
            "ASP.NET_SessionId": "ASP.NET",
            ".AspNetCore": "ASP.NET Core",
        }

        for cookie_name in cookies:
            for indicator, tech in cookie_indicators.items():
                if indicator.lower() in cookie_name.lower():
                    findings.append({
                        "tech": tech,
                        "cookie": cookie_name,
                        "confidence": "high",
                    })
                    break

        return findings

    def detect_social_meta(self, soup: BeautifulSoup) -> Dict:
        """Detect social media meta tags."""
        social = {}

        if not soup:
            return social

        # Open Graph
        og_tags = {}
        for meta in soup.find_all("meta"):
            prop = meta.get("property", "") or meta.get("name", "")
            if str(prop).lower().startswith("og:"):
                og_tags[prop] = meta.get("content", "")

        if og_tags:
            social["open_graph"] = og_tags

        # Twitter Cards
        twitter_tags = {}
        for meta in soup.find_all("meta"):
            name = meta.get("name", "")
            if str(name).lower().startswith("twitter:"):
                twitter_tags[name] = meta.get("content", "")

        if twitter_tags:
            social["twitter_cards"] = twitter_tags

        return social

    def detect_links_analysis(self, soup: BeautifulSoup, domain: Optional[str] = None) -> Dict:
        """Analyze links for technology hints.

        Args:
            soup: Parsed BeautifulSoup object
            domain: The site's own domain used to classify links as internal/external
        """
        analysis = {
            "internal_links": 0,
            "external_links": 0,
            "has_mailto": False,
            "has_tel": False,
            "api_endpoints": [],
        }

        if not soup:
            return analysis

        normalized_domain = (domain or "").lower().split(":", 1)[0]

        for a in soup.find_all("a", href=True):
            href = str(a["href"]).strip()
            parsed = urlparse(href)
            link_domain = parsed.netloc.lower().split(":", 1)[0]
            path_parts = [part.lower() for part in parsed.path.split("/") if part]

            href_lower = href.lower()
            if href_lower.startswith("mailto:"):
                analysis["has_mailto"] = True
            elif href_lower.startswith("tel:"):
                analysis["has_tel"] = True
            elif parsed.scheme in {"http", "https", ""} and any(
                part == "api" or part.startswith("api-") for part in path_parts
            ):
                analysis["api_endpoints"].append(href)

            if parsed.scheme not in {"http", "https", ""}:
                continue

            if domain and link_domain:
                # Internal = same domain or a subdomain of it; otherwise external
                if link_domain == normalized_domain or link_domain.endswith("." + normalized_domain):
                    analysis["internal_links"] += 1
                else:
                    analysis["external_links"] += 1
            elif not link_domain:
                # Relative links belong to the same site
                analysis["internal_links"] += 1

        analysis["api_endpoints"] = list(dict.fromkeys(analysis["api_endpoints"]))[:5]

        return analysis

    def detect_script_analysis(self, soup: BeautifulSoup) -> Dict:
        """Analyze script tags for technology hints."""
        analysis = {
            "total_scripts": 0,
            "inline_scripts": 0,
            "external_scripts": 0,
            "module_scripts": 0,
            "deferred_scripts": 0,
            "async_scripts": 0,
            "type_module": 0,
        }

        if not soup:
            return analysis

        for script in soup.find_all("script"):
            analysis["total_scripts"] += 1
            if script.get("src"):
                analysis["external_scripts"] += 1
                if str(script.get("type", "")).lower() == "module":
                    analysis["module_scripts"] += 1
                    analysis["type_module"] += 1
            else:
                analysis["inline_scripts"] += 1

            if script.get("defer") is not None:
                analysis["deferred_scripts"] += 1
            if script.get("async") is not None:
                analysis["async_scripts"] += 1

        return analysis

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format byte size to human readable string."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 ** 2):.2f} MB"
