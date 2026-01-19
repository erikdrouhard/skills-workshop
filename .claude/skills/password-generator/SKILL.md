---
name: password-generator
description: Generate secure random passwords or memorable passphrases. Use when user needs a password, passphrase, secret key, or asks for help creating secure credentials.
---

# Password Generator

Generate cryptographically secure passwords using `scripts/generate_password.py`.

## Quick Reference

```bash
# Random password (16 chars, mixed case, digits, symbols)
python scripts/generate_password.py

# Longer password
python scripts/generate_password.py -l 24

# Memorable passphrase
python scripts/generate_password.py --passphrase

# Multiple passwords
python scripts/generate_password.py -n 5
```

## Options

**Random passwords:**
- `-l, --length` — Character count (default: 16)
- `--no-upper` — Exclude uppercase
- `--no-lower` — Exclude lowercase
- `--no-digits` — Exclude numbers
- `--no-symbols` — Exclude special characters
- `--exclude-ambiguous` — Skip confusing chars (0/O/l/1/I)

**Passphrases:**
- `-p, --passphrase` — Switch to passphrase mode
- `-w, --words` — Word count (default: 4)
- `-s, --separator` — Word separator (default: -)
- `--capitalize` — Capitalize each word

## Examples

| Need | Command |
|------|---------|
| Standard secure password | `python scripts/generate_password.py` |
| Extra long | `python scripts/generate_password.py -l 32` |
| No symbols (legacy systems) | `python scripts/generate_password.py --no-symbols` |
| Easy to type | `python scripts/generate_password.py --exclude-ambiguous` |
| Memorable passphrase | `python scripts/generate_password.py -p` |
| Stronger passphrase | `python scripts/generate_password.py -p -w 6` |
| Multiple options | `python scripts/generate_password.py -n 5` |
