#!/usr/bin/env python3
"""Generate a salted hash URL and display as QR code in terminal."""

import argparse
import random
import string
import sys

try:
    import qrcode
except ImportError:
    print("Error: qrcode package required. Install with: pip install qrcode", file=sys.stderr)
    sys.exit(1)


def generate_salt(length: int = 7) -> str:
    """Generate a random salt with special characters, letters, and numbers."""
    chars = string.ascii_lowercase + string.digits + "@#$%&*!_"
    return "".join(random.choice(chars) for _ in range(length))


def generate_qr_terminal(url: str) -> str:
    """Generate QR code as ASCII art for terminal display."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Build ASCII representation
    lines = []
    for row in qr.modules:
        line = ""
        for cell in row:
            line += "██" if cell else "  "
        lines.append(line)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a salted hash URL and display as QR code"
    )
    parser.add_argument("identifier", help="Base identifier (e.g., erik-1246)")
    parser.add_argument(
        "--domain",
        default="example.com",
        help="Domain for the URL (default: example.com)",
    )
    parser.add_argument(
        "--salt-length",
        type=int,
        default=7,
        help="Length of the salt suffix (default: 7)",
    )

    args = parser.parse_args()

    salt = generate_salt(args.salt_length)
    salted_id = f"{args.identifier}-{salt}"
    url = f"https://{args.domain}/user/{salted_id}"

    qr_ascii = generate_qr_terminal(url)

    print(f"\nURL: {url}\n")
    print(qr_ascii)
    print(f"\nSalted ID: {salted_id}")


if __name__ == "__main__":
    main()
