---
name: agent-eyes
description: |
  Browser automation for visual testing, accessibility audits, and DOM inspection using Playwright.
  Use this skill when users need to: (1) Run accessibility (a11y) audits on websites and generate reports,
  (2) Take screenshots of web pages (full-page or elements), (3) Compare screenshots to detect visual changes,
  (4) Inspect or select DOM elements interactively to get context for modifications,
  (5) Connect to an existing browser session or navigate to URLs for testing.
  Triggers on: "a11y audit", "accessibility check", "screenshot", "visual diff", "compare screenshots",
  "element picker", "inspect element", "DOM context", "what's on this page", "browser automation".
---

# Agent Eyes

Browser automation toolkit for accessibility audits, screenshots, visual diffs, and DOM inspection.

## Prerequisites

Install dependencies before first use:

```bash
uv pip install playwright Pillow
playwright install chromium
```

## Browser Connection Modes

### 1. Connect to Existing Browser (Recommended for interactive work)

Start Chrome with remote debugging:
```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222

# Windows
chrome.exe --remote-debugging-port=9222
```

Scripts then connect via `--cdp-url http://localhost:9222`.

### 2. Navigate to URL (For automated tasks)

Scripts launch a new browser and navigate to the specified URL. Use `--headless` for CI/automation.

## Workflows

### Accessibility Audit

Generate an a11y report for any website:

```bash
# Audit URL directly
uv run scripts/a11y_audit.py --url https://example.com

# Audit current page in connected browser
uv run scripts/a11y_audit.py --cdp-url http://localhost:9222

# Custom standards (wcag2a, wcag2aa, wcag21aa, best-practice)
uv run scripts/a11y_audit.py --url https://example.com --standards wcag21aa
```

Output: `a11y-[domain].md` with severity levels, affected elements, and remediation links.

### Screenshot Capture

```bash
# Basic screenshot
uv run scripts/screenshot.py --url https://example.com -o screenshot.png

# Full-page capture
uv run scripts/screenshot.py --url https://example.com --full-page -o full.png

# Screenshot specific element
uv run scripts/screenshot.py --url https://example.com --selector "#hero" -o hero.png

# Custom viewport
uv run scripts/screenshot.py --url https://example.com --width 375 --height 812 -o mobile.png

# From connected browser
uv run scripts/screenshot.py --cdp-url http://localhost:9222 -o current.png
```

### Visual Diff Comparison

Compare two screenshots to detect visual regressions:

```bash
# Basic diff (highlights changes in red)
uv run scripts/visual_diff.py --before baseline.png --after current.png -o diff.png

# Side-by-side comparison
uv run scripts/visual_diff.py --before a.png --after b.png --mode side-by-side -o compare.png

# Adjust sensitivity (lower = more sensitive)
uv run scripts/visual_diff.py --before a.png --after b.png --threshold 5 -o diff.png

# JSON output with metrics
uv run scripts/visual_diff.py --before a.png --after b.png --json
```

### Element Picker (Edit Mode)

Interactively select elements to get DOM context:

```bash
# Pick from connected browser
uv run scripts/element_picker.py --cdp-url http://localhost:9222

# Pick from URL
uv run scripts/element_picker.py --url https://example.com

# Basic context only
uv run scripts/element_picker.py --cdp-url http://localhost:9222 --context basic
```

Returns JSON with:
- CSS selector
- Element attributes
- Computed styles
- outerHTML/innerHTML
- Parent chain, siblings, children (extended context)

### Browser Info

Get information about the current page:

```bash
uv run scripts/browser.py info --cdp-url http://localhost:9222
```

## Common Patterns

### A11y Audit Workflow

When user asks "Is this website accessible?" or "Run an a11y audit":

1. Determine target (URL or connected browser)
2. Run `a11y_audit.py` with appropriate standards
3. Read the generated report
4. Summarize critical/serious issues
5. Provide remediation guidance

### Visual Regression Workflow

When comparing before/after changes:

1. Capture baseline: `screenshot.py --url [url] -o baseline.png`
2. User makes changes
3. Capture current: `screenshot.py --url [url] -o current.png`
4. Generate diff: `visual_diff.py --before baseline.png --after current.png`
5. Report findings with diff percentage

### DOM Context Workflow

When user needs to modify specific elements:

1. Run `element_picker.py` to let user select element
2. Use the returned selector and context
3. Provide modification suggestions based on element structure

## Script Reference

| Script | Purpose |
|--------|---------|
| `browser.py` | Core browser connection and page info |
| `a11y_audit.py` | Accessibility auditing with axe-core |
| `screenshot.py` | Screenshot capture (viewport, full-page, element) |
| `visual_diff.py` | Compare screenshots and generate diffs |
| `element_picker.py` | Interactive DOM element selection |

## Error Handling

- **"playwright not installed"**: Run `uv pip install playwright && playwright install chromium`
- **"No browser contexts found"**: Open a page in the browser before connecting
- **"Failed to connect"**: Ensure browser started with `--remote-debugging-port=9222`
- **"Element not found"**: Verify selector exists on page
