#!/usr/bin/env python3
"""Generate a QR code from a URL and display in terminal, save to file, or copy to clipboard."""

import argparse
import io
import platform
import subprocess
import sys

try:
    import qrcode
    from qrcode.image.svg import SvgPathImage
except ImportError:
    print("Error: qrcode package required. Install with: pip install qrcode", file=sys.stderr)
    sys.exit(1)


def generate_png(qr, output_path=None):
    """Generate PNG image. Returns bytes if no output_path, otherwise saves to file."""
    try:
        from PIL import Image
    except ImportError:
        print("Error: pillow package required for PNG. Install with: pip install pillow", file=sys.stderr)
        sys.exit(1)

    img = qr.make_image(fill_color="black", back_color="white")

    if output_path:
        img.save(output_path)
        return None
    else:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()


def generate_svg(qr, output_path=None):
    """Generate SVG image. Returns string if no output_path, otherwise saves to file."""
    img = qr.make_image(image_factory=SvgPathImage)

    if output_path:
        img.save(output_path)
        return None
    else:
        buffer = io.BytesIO()
        img.save(buffer)
        return buffer.getvalue().decode("utf-8")


def copy_to_clipboard(png_bytes):
    """Copy PNG image to system clipboard."""
    system = platform.system()

    if system == "Darwin":  # macOS
        # Use osascript to set clipboard to PNG data
        process = subprocess.Popen(
            ["osascript", "-e", 'set the clipboard to (read (POSIX file "/dev/stdin") as «class PNGf»)'],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # osascript can't read binary from stdin easily, so we use a temp file approach
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_bytes)
            temp_path = f.name

        subprocess.run(
            ["osascript", "-e", f'set the clipboard to (read (POSIX file "{temp_path}") as «class PNGf»)'],
            check=True
        )
        import os
        os.unlink(temp_path)

    elif system == "Linux":
        # Try xclip first, then xsel
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard", "-t", "image/png"],
                input=png_bytes,
                check=True
            )
        except FileNotFoundError:
            try:
                subprocess.run(
                    ["xsel", "--clipboard", "--input"],
                    input=png_bytes,
                    check=True
                )
            except FileNotFoundError:
                print("Error: xclip or xsel required on Linux. Install with: sudo apt install xclip", file=sys.stderr)
                sys.exit(1)

    elif system == "Windows":
        # Windows clipboard handling requires win32clipboard or similar
        print("Error: Windows clipboard not yet supported. Use --output instead.", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Error: Unsupported platform for clipboard: {system}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a QR code from a URL and display in terminal, save to file, or copy to clipboard"
    )
    parser.add_argument("url", help="URL to encode as QR code")
    parser.add_argument(
        "-o", "--output",
        help="Save QR code to file (supports .png and .svg extensions)"
    )
    parser.add_argument(
        "-c", "--clipboard",
        action="store_true",
        help="Copy QR code image to clipboard (PNG format)"
    )

    args = parser.parse_args()

    qr = qrcode.QRCode(border=1)
    qr.add_data(args.url)
    qr.make(fit=True)

    print(f"\nURL: {args.url}\n")

    if args.output:
        ext = args.output.lower().split(".")[-1]
        if ext == "svg":
            generate_svg(qr, args.output)
            print(f"✓ Saved SVG to: {args.output}")
        elif ext == "png":
            generate_png(qr, args.output)
            print(f"✓ Saved PNG to: {args.output}")
        else:
            print(f"Error: Unsupported format '.{ext}'. Use .png or .svg", file=sys.stderr)
            sys.exit(1)

    if args.clipboard:
        png_bytes = generate_png(qr)
        copy_to_clipboard(png_bytes)
        print("✓ Copied to clipboard (PNG)")

    # Show ASCII in terminal if no output options specified, or always as preview
    if not args.output and not args.clipboard:
        qr.print_ascii(invert=True)
    elif args.output or args.clipboard:
        # Still show ASCII as a preview when saving/copying
        print("\nPreview:")
        qr.print_ascii(invert=True)


if __name__ == "__main__":
    main()
