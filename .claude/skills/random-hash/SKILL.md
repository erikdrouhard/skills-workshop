---
name: random-hash
description: Generate salted hash URLs with QR codes displayed in terminal. Use when user wants to create a unique URL with a random salt appended to an identifier, or needs a QR code linking to a user profile page. Triggers on /random-hash commands.
---

# Random Hash QR Generator

Generate unique salted URLs and display them as QR codes in the terminal.

## Usage

```
/random-hash <identifier>
```

Example: `/random-hash erik-1246` generates a URL like `https://example.com/user/erik-1246-@92s_1!`

## Execution

Run the script with uv:

```bash
uv run --with qrcode scripts/generate_qr.py <identifier> [--domain DOMAIN] [--salt-length N]
```

**Arguments:**
- `identifier` (required): Base identifier for the URL (e.g., `erik-1246`)
- `--domain`: Target domain (default: `example.com`)
- `--salt-length`: Length of random salt suffix (default: 7)

## Output

The script displays:
1. The full salted URL
2. ASCII QR code in terminal
3. The salted identifier for reference
