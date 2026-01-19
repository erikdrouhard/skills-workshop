#!/usr/bin/env python3
"""
Visual diff comparison script for screenshots.

Compares two screenshots and generates a diff image highlighting changes.

Usage:
    # Compare two screenshots
    python visual_diff.py --before before.png --after after.png --output diff.png

    # Compare with threshold (0-100, lower = more sensitive)
    python visual_diff.py --before a.png --after b.png --threshold 5 --output diff.png

    # Generate side-by-side comparison
    python visual_diff.py --before a.png --after b.png --mode side-by-side --output compare.png

    # JSON output with diff metrics
    python visual_diff.py --before a.png --after b.png --json
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
except ImportError:
    print("Error: Pillow not installed. Run: uv pip install Pillow")
    sys.exit(1)


def calculate_diff_percentage(img1: Image.Image, img2: Image.Image) -> float:
    """Calculate the percentage of pixels that differ between two images."""
    if img1.size != img2.size:
        return 100.0  # Completely different if sizes don't match

    diff = ImageChops.difference(img1.convert("RGB"), img2.convert("RGB"))
    diff_gray = diff.convert("L")

    # Count non-zero pixels
    pixels = list(diff_gray.getdata())
    total = len(pixels)
    changed = sum(1 for p in pixels if p > 0)

    return (changed / total) * 100


def create_diff_image(
    before: Image.Image,
    after: Image.Image,
    threshold: int = 10
) -> tuple[Image.Image, dict]:
    """Create a diff image highlighting changes."""
    # Resize to match if needed
    if before.size != after.size:
        after = after.resize(before.size, Image.Resampling.LANCZOS)

    before_rgb = before.convert("RGB")
    after_rgb = after.convert("RGB")

    # Calculate difference
    diff = ImageChops.difference(before_rgb, after_rgb)
    diff_gray = diff.convert("L")

    # Apply threshold
    threshold_value = int(threshold * 2.55)  # Convert 0-100 to 0-255
    diff_binary = diff_gray.point(lambda p: 255 if p > threshold_value else 0)

    # Create highlighted diff image
    result = after_rgb.copy()
    result_pixels = result.load()
    diff_pixels = diff_binary.load()
    width, height = result.size

    changed_regions = []
    current_region = None

    for y in range(height):
        for x in range(width):
            if diff_pixels[x, y] > 0:
                # Highlight changed pixel in red
                r, g, b = result_pixels[x, y]
                result_pixels[x, y] = (255, int(g * 0.3), int(b * 0.3))

                # Track regions (simple bounding box)
                if current_region is None:
                    current_region = [x, y, x, y]
                else:
                    current_region[2] = max(current_region[2], x)
                    current_region[3] = max(current_region[3], y)

    # Calculate diff stats
    total_pixels = width * height
    changed_pixels = sum(1 for y in range(height) for x in range(width) if diff_pixels[x, y] > 0)
    diff_percentage = (changed_pixels / total_pixels) * 100

    stats = {
        "total_pixels": total_pixels,
        "changed_pixels": changed_pixels,
        "diff_percentage": round(diff_percentage, 2),
        "dimensions": {"width": width, "height": height}
    }

    return result, stats


def create_side_by_side(
    before: Image.Image,
    after: Image.Image,
    diff: Image.Image = None
) -> Image.Image:
    """Create a side-by-side comparison image."""
    # Resize to match heights
    max_height = max(before.height, after.height)
    if diff:
        max_height = max(max_height, diff.height)

    def resize_to_height(img, target_height):
        ratio = target_height / img.height
        new_width = int(img.width * ratio)
        return img.resize((new_width, target_height), Image.Resampling.LANCZOS)

    before = resize_to_height(before, max_height)
    after = resize_to_height(after, max_height)
    if diff:
        diff = resize_to_height(diff, max_height)

    # Create combined image
    gap = 20
    images = [before, after] + ([diff] if diff else [])
    total_width = sum(img.width for img in images) + gap * (len(images) - 1)

    combined = Image.new("RGB", (total_width, max_height), (40, 40, 40))

    # Add labels
    draw = ImageDraw.Draw(combined)

    x_offset = 0
    labels = ["BEFORE", "AFTER"] + (["DIFF"] if diff else [])

    for img, label in zip(images, labels):
        combined.paste(img, (x_offset, 0))

        # Add label background
        label_height = 30
        draw.rectangle(
            [x_offset, 0, x_offset + img.width, label_height],
            fill=(0, 0, 0, 180)
        )
        draw.text(
            (x_offset + 10, 5),
            label,
            fill=(255, 255, 255)
        )

        x_offset += img.width + gap

    return combined


def create_overlay_diff(
    before: Image.Image,
    after: Image.Image,
    opacity: float = 0.5
) -> Image.Image:
    """Create an overlay diff with before/after blended."""
    if before.size != after.size:
        after = after.resize(before.size, Image.Resampling.LANCZOS)

    before_rgb = before.convert("RGBA")
    after_rgb = after.convert("RGBA")

    # Blend images
    blended = Image.blend(before_rgb, after_rgb, opacity)

    return blended


def main():
    parser = argparse.ArgumentParser(description="Compare screenshots visually")
    parser.add_argument("--before", "-b", required=True,
                       help="Path to before/baseline screenshot")
    parser.add_argument("--after", "-a", required=True,
                       help="Path to after/current screenshot")
    parser.add_argument("--output", "-o",
                       help="Output file path for diff image")
    parser.add_argument("--mode", choices=["diff", "side-by-side", "overlay"],
                       default="diff",
                       help="Comparison mode (default: diff)")
    parser.add_argument("--threshold", type=int, default=10,
                       help="Diff threshold 0-100 (default: 10, lower = more sensitive)")
    parser.add_argument("--json", action="store_true",
                       help="Output results as JSON")

    args = parser.parse_args()

    # Load images
    try:
        before = Image.open(args.before)
        after = Image.open(args.after)
    except Exception as e:
        print(f"Error loading images: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate output filename if not provided
    output = args.output
    if not output:
        before_path = Path(args.before)
        output = f"{before_path.stem}-diff.png"

    # Create comparison based on mode
    if args.mode == "diff":
        result, stats = create_diff_image(before, after, args.threshold)
    elif args.mode == "side-by-side":
        diff_img, stats = create_diff_image(before, after, args.threshold)
        result = create_side_by_side(before, after, diff_img)
    elif args.mode == "overlay":
        result = create_overlay_diff(before, after)
        stats = {
            "diff_percentage": calculate_diff_percentage(before, after),
            "mode": "overlay"
        }

    # Save result
    result.save(output)

    # Output results
    output_data = {
        "success": True,
        "output": str(Path(output).absolute()),
        "before": args.before,
        "after": args.after,
        "mode": args.mode,
        "threshold": args.threshold,
        **stats
    }

    if args.json:
        print(json.dumps(output_data, indent=2))
    else:
        print(f"Diff saved to: {output}", file=sys.stderr)
        print(f"Changed pixels: {stats.get('changed_pixels', 'N/A')}", file=sys.stderr)
        print(f"Diff percentage: {stats.get('diff_percentage', 'N/A')}%", file=sys.stderr)

        # Interpretation
        diff_pct = stats.get("diff_percentage", 0)
        if diff_pct == 0:
            print("Result: Images are identical", file=sys.stderr)
        elif diff_pct < 1:
            print("Result: Minor differences (likely anti-aliasing or rendering)", file=sys.stderr)
        elif diff_pct < 5:
            print("Result: Small visual changes detected", file=sys.stderr)
        elif diff_pct < 20:
            print("Result: Moderate visual changes detected", file=sys.stderr)
        else:
            print("Result: Significant visual changes detected", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
