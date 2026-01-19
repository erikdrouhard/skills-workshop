#!/usr/bin/env python3
"""
Accessibility audit script using Playwright and axe-core.

Generates comprehensive a11y reports in Markdown format.

Usage:
    # Audit a URL directly
    python a11y_audit.py --url https://example.com --output a11y-example.md

    # Audit current page in connected browser
    python a11y_audit.py --cdp-url ws://localhost:9222 --output a11y-report.md

    # Audit with specific standards (wcag2a, wcag2aa, wcag21aa, best-practice)
    python a11y_audit.py --url https://example.com --standards wcag2aa,best-practice
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: playwright not installed. Run: uv pip install playwright && playwright install chromium")
    sys.exit(1)

# axe-core CDN URL
AXE_CORE_URL = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.3/axe.min.js"

SEVERITY_ORDER = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
SEVERITY_EMOJI = {"critical": "🔴", "serious": "🟠", "moderate": "🟡", "minor": "🔵"}


async def inject_axe(page) -> bool:
    """Inject axe-core into the page."""
    try:
        # Check if axe is already loaded
        has_axe = await page.evaluate("() => typeof window.axe !== 'undefined'")
        if has_axe:
            return True

        # Inject axe-core
        await page.add_script_tag(url=AXE_CORE_URL)
        await page.wait_for_function("() => typeof window.axe !== 'undefined'", timeout=10000)
        return True
    except Exception as e:
        print(f"Warning: Failed to inject axe-core: {e}", file=sys.stderr)
        return False


async def run_axe_audit(page, standards: list[str] = None) -> dict:
    """Run axe-core accessibility audit."""
    # Configure axe options
    config = {
        "resultTypes": ["violations", "incomplete", "inapplicable", "passes"]
    }

    if standards:
        config["runOnly"] = {
            "type": "tag",
            "values": standards
        }

    results = await page.evaluate(f"""
        async () => {{
            const config = {json.dumps(config)};
            return await axe.run(document, config);
        }}
    """)

    return results


def generate_markdown_report(results: dict, url: str, standards: list[str]) -> str:
    """Generate a Markdown accessibility report."""
    violations = results.get("violations", [])
    incomplete = results.get("incomplete", [])
    passes = results.get("passes", [])

    # Sort violations by severity
    violations.sort(key=lambda v: SEVERITY_ORDER.get(v.get("impact", "minor"), 4))

    domain = urlparse(url).netloc.replace("www.", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        f"# Accessibility Audit: {domain}",
        "",
        f"**URL:** {url}",
        f"**Date:** {timestamp}",
        f"**Standards:** {', '.join(standards) if standards else 'All'}",
        "",
        "## Summary",
        "",
        f"| Category | Count |",
        f"|----------|-------|",
        f"| 🔴 Violations | {len(violations)} |",
        f"| ⚠️ Needs Review | {len(incomplete)} |",
        f"| ✅ Passed | {len(passes)} |",
        "",
    ]

    # Severity breakdown
    severity_counts = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
    for v in violations:
        impact = v.get("impact", "minor")
        severity_counts[impact] = severity_counts.get(impact, 0) + 1

    if violations:
        lines.extend([
            "### Severity Breakdown",
            "",
            "| Severity | Count |",
            "|----------|-------|",
        ])
        for sev in ["critical", "serious", "moderate", "minor"]:
            if severity_counts[sev] > 0:
                lines.append(f"| {SEVERITY_EMOJI[sev]} {sev.capitalize()} | {severity_counts[sev]} |")
        lines.append("")

    # Violations details
    if violations:
        lines.extend([
            "## Violations",
            "",
        ])

        for i, v in enumerate(violations, 1):
            impact = v.get("impact", "minor")
            emoji = SEVERITY_EMOJI.get(impact, "⚪")
            lines.extend([
                f"### {i}. {emoji} {v['help']}",
                "",
                f"**Impact:** {impact.capitalize()}",
                f"**Rule ID:** `{v['id']}`",
                "",
                v.get("description", ""),
                "",
            ])

            # Affected elements
            nodes = v.get("nodes", [])
            if nodes:
                lines.append(f"**Affected Elements:** ({len(nodes)} found)")
                lines.append("")
                for j, node in enumerate(nodes[:5], 1):  # Limit to 5 examples
                    target = node.get("target", ["unknown"])[0]
                    lines.append(f"{j}. `{target}`")
                    if node.get("html"):
                        html_snippet = node["html"][:200] + ("..." if len(node["html"]) > 200 else "")
                        lines.append(f"   ```html")
                        lines.append(f"   {html_snippet}")
                        lines.append(f"   ```")

                if len(nodes) > 5:
                    lines.append(f"   ... and {len(nodes) - 5} more")
                lines.append("")

            # How to fix
            if v.get("helpUrl"):
                lines.append(f"**Learn more:** [{v['id']}]({v['helpUrl']})")
                lines.append("")

    # Needs review section
    if incomplete:
        lines.extend([
            "## Needs Manual Review",
            "",
            "These elements could not be automatically verified and require manual testing:",
            "",
        ])

        for item in incomplete[:10]:  # Limit to 10
            lines.append(f"- **{item['help']}** (`{item['id']}`)")

        if len(incomplete) > 10:
            lines.append(f"- ... and {len(incomplete) - 10} more")
        lines.append("")

    # Passing rules
    if passes:
        lines.extend([
            "## Passing Rules",
            "",
            f"<details>",
            f"<summary>{len(passes)} rules passed</summary>",
            "",
        ])
        for p in passes:
            lines.append(f"- ✅ {p['help']}")
        lines.extend(["", "</details>", ""])

    # Footer
    lines.extend([
        "---",
        "",
        "*Report generated by agent-eyes using [axe-core](https://github.com/dequelabs/axe-core)*",
    ])

    return "\n".join(lines)


async def audit_url(url: str, output: str, standards: list[str], headless: bool = True):
    """Audit a URL directly."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()

        try:
            print(f"Navigating to {url}...", file=sys.stderr)
            await page.goto(url, wait_until="networkidle")

            print("Injecting axe-core...", file=sys.stderr)
            if not await inject_axe(page):
                print("Error: Failed to inject axe-core", file=sys.stderr)
                return False

            print("Running accessibility audit...", file=sys.stderr)
            results = await run_axe_audit(page, standards)

            report = generate_markdown_report(results, url, standards)

            # Write report
            output_path = Path(output)
            output_path.write_text(report)
            print(f"Report saved to: {output_path}", file=sys.stderr)

            # Print summary
            violations = results.get("violations", [])
            print(f"\nFound {len(violations)} accessibility violations", file=sys.stderr)

            return True

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return False
        finally:
            await browser.close()


async def audit_connected_browser(cdp_url: str, output: str, standards: list[str]):
    """Audit the current page in a connected browser."""
    async with async_playwright() as p:
        try:
            print(f"Connecting to browser at {cdp_url}...", file=sys.stderr)
            browser = await p.chromium.connect_over_cdp(cdp_url)

            contexts = browser.contexts
            if not contexts or not contexts[0].pages:
                print("Error: No page available in browser", file=sys.stderr)
                return False

            page = contexts[0].pages[0]
            url = page.url

            print(f"Auditing: {url}", file=sys.stderr)

            print("Injecting axe-core...", file=sys.stderr)
            if not await inject_axe(page):
                print("Error: Failed to inject axe-core", file=sys.stderr)
                return False

            print("Running accessibility audit...", file=sys.stderr)
            results = await run_axe_audit(page, standards)

            report = generate_markdown_report(results, url, standards)

            # Generate output filename if not specified
            if output == "auto":
                domain = urlparse(url).netloc.replace("www.", "").replace(".", "-")
                output = f"a11y-{domain}.md"

            output_path = Path(output)
            output_path.write_text(report)
            print(f"Report saved to: {output_path}", file=sys.stderr)

            violations = results.get("violations", [])
            print(f"\nFound {len(violations)} accessibility violations", file=sys.stderr)

            return True

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return False


def main():
    parser = argparse.ArgumentParser(description="Run accessibility audit on a webpage")
    parser.add_argument("--url", help="URL to audit (launches new browser)")
    parser.add_argument("--cdp-url", help="Connect to existing browser via CDP")
    parser.add_argument("--output", "-o", default="auto",
                       help="Output file path (default: auto-generated from domain)")
    parser.add_argument("--standards", default="wcag2aa,best-practice",
                       help="Comma-separated a11y standards: wcag2a, wcag2aa, wcag21aa, best-practice")
    parser.add_argument("--headless", action="store_true",
                       help="Run in headless mode (only for --url)")

    args = parser.parse_args()

    if not args.url and not args.cdp_url:
        parser.error("Either --url or --cdp-url must be specified")

    standards = [s.strip() for s in args.standards.split(",")]

    if args.url:
        output = args.output if args.output != "auto" else None
        if not output:
            domain = urlparse(args.url).netloc.replace("www.", "").replace(".", "-")
            output = f"a11y-{domain}.md"
        success = asyncio.run(audit_url(args.url, output, standards, args.headless))
    else:
        success = asyncio.run(audit_connected_browser(args.cdp_url, args.output, standards))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
