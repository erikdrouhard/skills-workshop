#!/usr/bin/env python3
"""
Interactive element picker using Playwright's DevTools-style selection.

Injects a selection overlay that allows users to click elements and get DOM context.

Usage:
    # Start element picker on connected browser
    python element_picker.py --cdp-url ws://localhost:9222

    # Start picker on a specific URL
    python element_picker.py --url https://example.com

    # Pick element and get extended context (parents, siblings)
    python element_picker.py --cdp-url ws://localhost:9222 --context extended
"""

import argparse
import asyncio
import json
import sys

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: playwright not installed. Run: uv pip install playwright && playwright install chromium")
    sys.exit(1)


# JavaScript for the element picker overlay
PICKER_SCRIPT = """
(function() {
    if (window.__agentEyesPicker) {
        window.__agentEyesPicker.destroy();
    }

    const picker = {
        overlay: null,
        tooltip: null,
        selectedElement: null,
        isActive: true,
        resolve: null,

        init: function() {
            // Create overlay
            this.overlay = document.createElement('div');
            this.overlay.id = '__agent-eyes-overlay';
            this.overlay.style.cssText = `
                position: fixed;
                pointer-events: none;
                border: 2px solid #4285f4;
                background: rgba(66, 133, 244, 0.1);
                z-index: 2147483647;
                transition: all 0.1s ease;
                display: none;
            `;
            document.body.appendChild(this.overlay);

            // Create tooltip
            this.tooltip = document.createElement('div');
            this.tooltip.id = '__agent-eyes-tooltip';
            this.tooltip.style.cssText = `
                position: fixed;
                background: #333;
                color: white;
                padding: 6px 10px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
                z-index: 2147483647;
                pointer-events: none;
                max-width: 400px;
                word-wrap: break-word;
                display: none;
            `;
            document.body.appendChild(this.tooltip);

            // Create instruction banner
            this.banner = document.createElement('div');
            this.banner.id = '__agent-eyes-banner';
            this.banner.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #4285f4;
                color: white;
                padding: 10px;
                text-align: center;
                font-family: system-ui, sans-serif;
                font-size: 14px;
                z-index: 2147483647;
            `;
            this.banner.innerHTML = '🎯 <strong>Element Picker Active</strong> - Click any element to select it. Press <kbd>Escape</kbd> to cancel.';
            document.body.appendChild(this.banner);

            // Bind events
            document.addEventListener('mousemove', this.onMouseMove.bind(this), true);
            document.addEventListener('click', this.onClick.bind(this), true);
            document.addEventListener('keydown', this.onKeyDown.bind(this), true);

            return this;
        },

        getSelector: function(el) {
            if (el.id) return '#' + el.id;

            const path = [];
            while (el && el.nodeType === Node.ELEMENT_NODE) {
                let selector = el.tagName.toLowerCase();

                if (el.id) {
                    selector = '#' + el.id;
                    path.unshift(selector);
                    break;
                }

                if (el.className && typeof el.className === 'string') {
                    const classes = el.className.trim().split(/\\s+/).filter(c => c && !c.startsWith('__'));
                    if (classes.length > 0) {
                        selector += '.' + classes.slice(0, 2).join('.');
                    }
                }

                const parent = el.parentElement;
                if (parent) {
                    const siblings = Array.from(parent.children).filter(c => c.tagName === el.tagName);
                    if (siblings.length > 1) {
                        const index = siblings.indexOf(el) + 1;
                        selector += ':nth-of-type(' + index + ')';
                    }
                }

                path.unshift(selector);
                el = parent;

                if (path.length > 5) break;
            }

            return path.join(' > ');
        },

        getElementInfo: function(el) {
            const rect = el.getBoundingClientRect();
            const styles = window.getComputedStyle(el);

            return {
                tagName: el.tagName.toLowerCase(),
                id: el.id || null,
                className: el.className || null,
                selector: this.getSelector(el),
                text: (el.textContent || '').trim().substring(0, 200),
                attributes: Array.from(el.attributes).reduce((acc, attr) => {
                    acc[attr.name] = attr.value;
                    return acc;
                }, {}),
                rect: {
                    x: Math.round(rect.x),
                    y: Math.round(rect.y),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height)
                },
                computedStyle: {
                    display: styles.display,
                    position: styles.position,
                    color: styles.color,
                    backgroundColor: styles.backgroundColor,
                    fontSize: styles.fontSize,
                    fontFamily: styles.fontFamily
                },
                outerHTML: el.outerHTML.substring(0, 1000),
                innerHTML: el.innerHTML.substring(0, 500)
            };
        },

        getExtendedContext: function(el) {
            const info = this.getElementInfo(el);

            // Get parent chain
            const parents = [];
            let parent = el.parentElement;
            let depth = 0;
            while (parent && depth < 3) {
                parents.push({
                    tagName: parent.tagName.toLowerCase(),
                    id: parent.id || null,
                    className: parent.className || null,
                    selector: this.getSelector(parent)
                });
                parent = parent.parentElement;
                depth++;
            }

            // Get siblings
            const siblings = [];
            if (el.parentElement) {
                Array.from(el.parentElement.children).forEach((sibling, index) => {
                    if (sibling !== el) {
                        siblings.push({
                            index: index,
                            tagName: sibling.tagName.toLowerCase(),
                            id: sibling.id || null,
                            className: sibling.className || null
                        });
                    }
                });
            }

            // Get children
            const children = Array.from(el.children).slice(0, 10).map(child => ({
                tagName: child.tagName.toLowerCase(),
                id: child.id || null,
                className: child.className || null
            }));

            return {
                ...info,
                parents: parents,
                siblings: siblings.slice(0, 5),
                children: children,
                childCount: el.children.length
            };
        },

        onMouseMove: function(e) {
            if (!this.isActive) return;

            const el = document.elementFromPoint(e.clientX, e.clientY);
            if (!el || el.id?.startsWith('__agent-eyes')) return;

            const rect = el.getBoundingClientRect();

            this.overlay.style.display = 'block';
            this.overlay.style.top = rect.top + 'px';
            this.overlay.style.left = rect.left + 'px';
            this.overlay.style.width = rect.width + 'px';
            this.overlay.style.height = rect.height + 'px';

            const selector = this.getSelector(el);
            this.tooltip.textContent = selector;
            this.tooltip.style.display = 'block';
            this.tooltip.style.top = Math.max(50, rect.top - 30) + 'px';
            this.tooltip.style.left = rect.left + 'px';
        },

        onClick: function(e) {
            if (!this.isActive) return;

            const el = document.elementFromPoint(e.clientX, e.clientY);
            if (!el || el.id?.startsWith('__agent-eyes')) return;

            e.preventDefault();
            e.stopPropagation();

            this.selectedElement = el;
            this.complete();
        },

        onKeyDown: function(e) {
            if (e.key === 'Escape') {
                this.cancel();
            }
        },

        complete: function() {
            this.isActive = false;
            const result = window.__agentEyesExtendedContext
                ? this.getExtendedContext(this.selectedElement)
                : this.getElementInfo(this.selectedElement);
            this.destroy();
            if (this.resolve) this.resolve(result);
        },

        cancel: function() {
            this.isActive = false;
            this.destroy();
            if (this.resolve) this.resolve({ cancelled: true });
        },

        destroy: function() {
            this.overlay?.remove();
            this.tooltip?.remove();
            this.banner?.remove();
            document.removeEventListener('mousemove', this.onMouseMove, true);
            document.removeEventListener('click', this.onClick, true);
            document.removeEventListener('keydown', this.onKeyDown, true);
            window.__agentEyesPicker = null;
        }
    };

    window.__agentEyesPicker = picker.init();
})();
"""


async def run_element_picker(page, extended_context: bool = False) -> dict:
    """Run the element picker on a page and wait for selection."""
    # Set context mode
    await page.evaluate(f"window.__agentEyesExtendedContext = {str(extended_context).lower()}")

    # Inject picker
    await page.evaluate(PICKER_SCRIPT)

    # Wait for user selection
    print("Element picker active. Click an element to select it, or press Escape to cancel.", file=sys.stderr)

    result = await page.evaluate("""
        () => new Promise(resolve => {
            window.__agentEyesPicker.resolve = resolve;
        })
    """)

    return result


async def pick_from_connected(cdp_url: str, extended_context: bool = False) -> dict:
    """Run element picker on connected browser."""
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(cdp_url)

            contexts = browser.contexts
            if not contexts or not contexts[0].pages:
                return {"error": "No page available in browser"}

            page = contexts[0].pages[0]
            result = await run_element_picker(page, extended_context)

            return result

        except Exception as e:
            return {"error": str(e)}


async def pick_from_url(url: str, extended_context: bool = False) -> dict:
    """Launch browser, navigate to URL, and run element picker."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="networkidle")
            result = await run_element_picker(page, extended_context)
            return result

        except Exception as e:
            return {"error": str(e)}
        finally:
            await browser.close()


def main():
    parser = argparse.ArgumentParser(description="Interactive element picker")
    parser.add_argument("--url", help="URL to open (launches new browser)")
    parser.add_argument("--cdp-url", default="http://localhost:9222",
                       help="Connect to existing browser via CDP")
    parser.add_argument("--context", choices=["basic", "extended"], default="extended",
                       help="Context level: basic (element only) or extended (with parents/siblings)")

    args = parser.parse_args()

    extended = args.context == "extended"

    if args.url:
        result = asyncio.run(pick_from_url(args.url, extended))
    else:
        result = asyncio.run(pick_from_connected(args.cdp_url, extended))

    print(json.dumps(result, indent=2))

    if result.get("cancelled"):
        sys.exit(1)
    elif result.get("error"):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
