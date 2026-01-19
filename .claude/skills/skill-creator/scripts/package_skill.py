#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file from a skill folder.

Usage:
    python package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python package_skill.py ./my-skill
    python package_skill.py ./my-skill ./dist
"""

import argparse
import os
import sys
import zipfile
from pathlib import Path

# Import validation from sibling module
from quick_validate import validate_skill


def package_skill(skill_path: str, output_dir: str = None) -> None:
    """Package a skill folder into a .skill file."""

    skill_dir = Path(skill_path)

    # Validate path exists and is a directory
    if not skill_dir.exists():
        print(f"Error: Path does not exist: {skill_dir}")
        sys.exit(1)

    if not skill_dir.is_dir():
        print(f"Error: Path is not a directory: {skill_dir}")
        sys.exit(1)

    # Check for required SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"Error: SKILL.md not found in {skill_dir}")
        sys.exit(1)

    # Run validation first
    print(f"Validating skill: {skill_dir.name}")
    if not validate_skill(str(skill_dir)):
        print("Error: Validation failed. Fix errors and try again.")
        sys.exit(1)

    print("✓ Validation passed")

    # Determine output location
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    # Create .skill file (zip with .skill extension)
    skill_name = skill_dir.name
    skill_file = output_path / f"{skill_name}.skill"

    print(f"Packaging skill: {skill_name}")

    with zipfile.ZipFile(skill_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    print()
    print(f"✓ Skill packaged successfully: {skill_file}")
    print(f"  Size: {skill_file.stat().st_size:,} bytes")


def main():
    parser = argparse.ArgumentParser(
        description="Package a skill folder into a distributable .skill file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python package_skill.py ./my-skill
  python package_skill.py ./my-skill ./dist
        """
    )
    parser.add_argument(
        "skill_path",
        help="Path to the skill folder to package"
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="Output directory for the .skill file (default: current directory)"
    )

    args = parser.parse_args()
    package_skill(args.skill_path, args.output_dir)


if __name__ == "__main__":
    main()
