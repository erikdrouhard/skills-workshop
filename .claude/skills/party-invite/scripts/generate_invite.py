#!/usr/bin/env python3
"""
Party Invite Generator - Creates personalized party invitations from a template.

Usage:
    python generate_invite.py --name "John" --date "Saturday, Feb 15th at 7pm" --dress-code "Casual"

Output:
    Creates party-invite-{name}.md in the current directory
"""

import argparse
import re
import sys
from pathlib import Path


def generate_invite(name: str, date: str, dress_code: str, output_dir: str = ".") -> str:
    """Generate a party invite from the template and save to file."""

    # Find the template relative to this script
    script_dir = Path(__file__).parent.parent
    template_path = script_dir / "assets" / "invite-template.txt"

    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        sys.exit(1)

    # Read template
    template = template_path.read_text()

    # Substitute placeholders
    invite_text = template.replace("{{name}}", name)
    invite_text = invite_text.replace("{{date}}", date)
    invite_text = invite_text.replace("{{dress_code}}", dress_code)

    # Create safe filename from name
    safe_name = re.sub(r'[^\w\-]', '-', name.lower()).strip('-')

    # Save to output file
    output_path = Path(output_dir) / f"party-invite-{safe_name}.md"
    output_path.write_text(invite_text)

    print(f"✓ Invite created: {output_path}")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a personalized party invitation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_invite.py --name "Alice" --date "Saturday, March 1st at 8pm" --dress-code "Smart Casual"
  python generate_invite.py -n "Bob" -d "Friday night" -c "Costume party!"
        """
    )

    parser.add_argument(
        "-n", "--name",
        required=True,
        help="Name of the person to invite"
    )
    parser.add_argument(
        "-d", "--date",
        required=True,
        help="Date and time of the party"
    )
    parser.add_argument(
        "-c", "--dress-code",
        required=True,
        help="Dress code for the party"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Directory to save the invite (default: current directory)"
    )

    args = parser.parse_args()
    generate_invite(args.name, args.date, args.dress_code, args.output_dir)


if __name__ == "__main__":
    main()
