#!/usr/bin/env python3
"""
Core browser automation module using Playwright.

Supports two modes:
1. Connect to existing browser session (via CDP)
2. Launch new browser and navigate to URLs

Usage:
    # Connect to existing browser (start Chrome with: --remote-debugging-port=9222)
    python browser.py connect --cdp-url ws://localhost:9222

    # Navigate to a URL in a new browser
    python browser.py navigate --url https://example.com

    # Get current page info from connected browser
    python browser.py info --cdp-url ws://localhost:9222
"""

import argparse
import asyncio
import json
import sys
from urllib.parse import urlparse

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: playwright not installed. Run: uv pip install playwright && playwright install chromium")
    sys.exit(1)


async def connect_to_browser(cdp_url: str) -> dict:
    """Connect to an existing browser via CDP and return page info."""
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(cdp_url)
            contexts = browser.contexts
            if not contexts:
                return {"error": "No browser contexts found. Open a page in the browser first."}

            pages = contexts[0].pages
            if not pages:
                return {"error": "No pages found in browser context."}

            page = pages[0]

            return {
                "url": page.url,
                "title": await page.title(),
                "viewport": page.viewport_size,
                "connected": True
            }
        except Exception as e:
            return {"error": f"Failed to connect: {str(e)}"}


async def navigate_to_url(url: str, headless: bool = False) -> dict:
    """Launch browser and navigate to URL."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="networkidle")
            result = {
                "url": page.url,
                "title": await page.title(),
                "viewport": page.viewport_size,
                "success": True
            }
        except Exception as e:
            result = {"error": f"Navigation failed: {str(e)}"}
        finally:
            await browser.close()

        return result


async def get_page_info(cdp_url: str) -> dict:
    """Get detailed information about the current page."""
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(cdp_url)
            contexts = browser.contexts
            if not contexts or not contexts[0].pages:
                return {"error": "No page available"}

            page = contexts[0].pages[0]

            # Get page metadata
            info = await page.evaluate("""() => {
                return {
                    url: window.location.href,
                    title: document.title,
                    doctype: document.doctype ? document.doctype.name : null,
                    charset: document.characterSet,
                    lang: document.documentElement.lang,
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight,
                        devicePixelRatio: window.devicePixelRatio
                    },
                    meta: {
                        description: document.querySelector('meta[name="description"]')?.content,
                        keywords: document.querySelector('meta[name="keywords"]')?.content,
                        author: document.querySelector('meta[name="author"]')?.content
                    },
                    links: {
                        total: document.links.length,
                        external: Array.from(document.links).filter(l => l.hostname !== window.location.hostname).length
                    },
                    images: {
                        total: document.images.length,
                        withoutAlt: Array.from(document.images).filter(i => !i.alt).length
                    },
                    headings: {
                        h1: document.querySelectorAll('h1').length,
                        h2: document.querySelectorAll('h2').length,
                        h3: document.querySelectorAll('h3').length
                    }
                };
            }""")

            return info

        except Exception as e:
            return {"error": f"Failed to get page info: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="Browser automation with Playwright")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to existing browser")
    connect_parser.add_argument("--cdp-url", default="http://localhost:9222",
                               help="Chrome DevTools Protocol URL")

    # Navigate command
    nav_parser = subparsers.add_parser("navigate", help="Navigate to URL in new browser")
    nav_parser.add_argument("--url", required=True, help="URL to navigate to")
    nav_parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    # Info command
    info_parser = subparsers.add_parser("info", help="Get current page info")
    info_parser.add_argument("--cdp-url", default="http://localhost:9222",
                            help="Chrome DevTools Protocol URL")

    args = parser.parse_args()

    if args.command == "connect":
        result = asyncio.run(connect_to_browser(args.cdp_url))
    elif args.command == "navigate":
        result = asyncio.run(navigate_to_url(args.url, args.headless))
    elif args.command == "info":
        result = asyncio.run(get_page_info(args.cdp_url))

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
