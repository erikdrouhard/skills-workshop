#!/usr/bin/env python3
"""
Screenshot capture script using Playwright.

Supports full-page screenshots, viewport screenshots, and element screenshots.

Usage:
    # Screenshot a URL
    python screenshot.py --url https://example.com --output example.png

    # Screenshot current page in connected browser
    python screenshot.py --cdp-url ws://localhost:9222 --output page.png

    # Full-page screenshot
    python screenshot.py --url https://example.com --full-page --output full.png

    # Screenshot specific element
    python screenshot.py --url https://example.com --selector "#main" --output main.png

    # Screenshot with specific viewport
    python screenshot.py --url https://example.com --width 1920 --height 1080 --output desktop.png
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: playwright not installed. Run: uv pip install playwright && playwright install chromium")
    sys.exit(1)


async def capture_url_screenshot(
    url: str,
    output: str,
    full_page: bool = False,
    selector: str = None,
    width: int = 1280,
    height: int = 720,
    headless: bool = True,
    wait_for: str = None,
    delay: int = 0
) -> dict:
    """Capture screenshot of a URL."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page(viewport={"width": width, "height": height})

        try:
            print(f"Navigating to {url}...", file=sys.stderr)
            await page.goto(url, wait_until="networkidle")

            # Optional wait for specific element
            if wait_for:
                print(f"Waiting for {wait_for}...", file=sys.stderr)
                await page.wait_for_selector(wait_for, timeout=10000)

            # Optional delay
            if delay > 0:
                print(f"Waiting {delay}ms...", file=sys.stderr)
                await asyncio.sleep(delay / 1000)

            # Capture screenshot
            if selector:
                print(f"Capturing element: {selector}...", file=sys.stderr)
                element = await page.query_selector(selector)
                if not element:
                    return {"error": f"Element not found: {selector}"}
                await element.screenshot(path=output)
            else:
                print(f"Capturing {'full page' if full_page else 'viewport'}...", file=sys.stderr)
                await page.screenshot(path=output, full_page=full_page)

            # Get image info
            output_path = Path(output)
            file_size = output_path.stat().st_size

            result = {
                "success": True,
                "output": str(output_path.absolute()),
                "url": url,
                "viewport": {"width": width, "height": height},
                "full_page": full_page,
                "file_size": file_size,
                "file_size_human": f"{file_size / 1024:.1f} KB"
            }

            print(f"Screenshot saved to: {output}", file=sys.stderr)
            return result

        except Exception as e:
            return {"error": str(e)}
        finally:
            await browser.close()


async def capture_connected_screenshot(
    cdp_url: str,
    output: str,
    full_page: bool = False,
    selector: str = None
) -> dict:
    """Capture screenshot from connected browser."""
    async with async_playwright() as p:
        try:
            print(f"Connecting to browser at {cdp_url}...", file=sys.stderr)
            browser = await p.chromium.connect_over_cdp(cdp_url)

            contexts = browser.contexts
            if not contexts or not contexts[0].pages:
                return {"error": "No page available in browser"}

            page = contexts[0].pages[0]
            url = page.url

            # Generate output filename if auto
            if output == "auto":
                domain = urlparse(url).netloc.replace("www.", "").replace(".", "-")
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                output = f"screenshot-{domain}-{timestamp}.png"

            # Capture screenshot
            if selector:
                print(f"Capturing element: {selector}...", file=sys.stderr)
                element = await page.query_selector(selector)
                if not element:
                    return {"error": f"Element not found: {selector}"}
                await element.screenshot(path=output)
            else:
                print(f"Capturing {'full page' if full_page else 'viewport'}...", file=sys.stderr)
                await page.screenshot(path=output, full_page=full_page)

            output_path = Path(output)
            file_size = output_path.stat().st_size

            result = {
                "success": True,
                "output": str(output_path.absolute()),
                "url": url,
                "full_page": full_page,
                "file_size": file_size,
                "file_size_human": f"{file_size / 1024:.1f} KB"
            }

            print(f"Screenshot saved to: {output}", file=sys.stderr)
            return result

        except Exception as e:
            return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Capture webpage screenshots")
    parser.add_argument("--url", help="URL to screenshot (launches new browser)")
    parser.add_argument("--cdp-url", help="Connect to existing browser via CDP")
    parser.add_argument("--output", "-o", default="auto",
                       help="Output file path (default: auto-generated)")
    parser.add_argument("--full-page", action="store_true",
                       help="Capture full scrollable page")
    parser.add_argument("--selector", "-s",
                       help="CSS selector to screenshot specific element")
    parser.add_argument("--width", type=int, default=1280,
                       help="Viewport width (default: 1280)")
    parser.add_argument("--height", type=int, default=720,
                       help="Viewport height (default: 720)")
    parser.add_argument("--headless", action="store_true",
                       help="Run in headless mode")
    parser.add_argument("--wait-for",
                       help="Wait for selector before screenshot")
    parser.add_argument("--delay", type=int, default=0,
                       help="Delay in ms before screenshot")

    args = parser.parse_args()

    if not args.url and not args.cdp_url:
        parser.error("Either --url or --cdp-url must be specified")

    if args.url:
        output = args.output
        if output == "auto":
            domain = urlparse(args.url).netloc.replace("www.", "").replace(".", "-")
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output = f"screenshot-{domain}-{timestamp}.png"

        result = asyncio.run(capture_url_screenshot(
            args.url,
            output,
            full_page=args.full_page,
            selector=args.selector,
            width=args.width,
            height=args.height,
            headless=args.headless,
            wait_for=args.wait_for,
            delay=args.delay
        ))
    else:
        result = asyncio.run(capture_connected_screenshot(
            args.cdp_url,
            args.output,
            full_page=args.full_page,
            selector=args.selector
        ))

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
