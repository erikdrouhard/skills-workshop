---
name: qr-code
description: Generate QR codes from URLs displayed in terminal. Use when user wants to create a QR code from a URL, link, or web address. Triggers on /qr-code commands.
---

# QR Code Generator

Generate QR codes from any URL and display them directly in the terminal, save to file, or copy to clipboard.

## Usage

```
/qr-code <url>
/qr-code <url> --output qr.png
/qr-code <url> --output qr.svg
/qr-code <url> --clipboard
```

Examples:
- `/qr-code https://claude.ai` — Display in terminal
- `/qr-code https://claude.ai --output qr.png` — Save as PNG file
- `/qr-code https://claude.ai --output qr.svg` — Save as SVG file
- `/qr-code https://claude.ai --clipboard` — Copy to clipboard for pasting into Figma, PowerPoint, etc.
- `/qr-code https://claude.ai -o qr.png -c` — Save to file AND copy to clipboard

## Execution

Run the script with uv:

```bash
# Terminal display only
uv run --with qrcode scripts/generate_qr.py <url>

# Save to PNG (requires pillow)
uv run --with qrcode --with pillow scripts/generate_qr.py <url> --output qr.png

# Save to SVG
uv run --with qrcode scripts/generate_qr.py <url> --output qr.svg

# Copy to clipboard (requires pillow)
uv run --with qrcode --with pillow scripts/generate_qr.py <url> --clipboard
```

**Arguments:**
- `url` (required): The URL to encode as a QR code
- `--output`, `-o` (optional): Save to file (.png or .svg)
- `--clipboard`, `-c` (optional): Copy PNG to system clipboard

## Output

Depending on options:
1. **Default**: ASCII QR code in terminal (scannable with phone camera)
2. **--output**: Saves image file + shows ASCII preview
3. **--clipboard**: Copies PNG to clipboard + shows ASCII preview

## Platform Support

- **macOS**: Full support (clipboard uses osascript)
- **Linux**: Clipboard requires `xclip` or `xsel`
- **Windows**: File output only (clipboard not yet supported)
