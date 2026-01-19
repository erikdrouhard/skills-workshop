#!/usr/bin/env python3
"""
Skill Validator - Validates skill definitions for compliance.

Usage:
    python quick_validate.py <path/to/skill-folder>

Example:
    python quick_validate.py ./my-skill
"""

import argparse
import re
import sys
from pathlib import Path

# Try to import yaml, fall back to basic parsing if not available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from SKILL.md content."""
    if not content.startswith("---"):
        return None

    # Find the closing ---
    end_match = re.search(r'\n---\s*\n', content[3:])
    if not end_match:
        return None

    frontmatter_text = content[3:end_match.start() + 3]

    if HAS_YAML:
        try:
            return yaml.safe_load(frontmatter_text)
        except yaml.YAMLError:
            return None
    else:
        # Basic parsing without yaml library
        result = {}
        for line in frontmatter_text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip().strip('"\'')
        return result


def validate_name(name: str) -> list:
    """Validate skill name and return list of errors."""
    errors = []

    if not name:
        errors.append("Missing required field: name")
        return errors

    if len(name) > 64:
        errors.append(f"Name is too long ({len(name)} chars, max 64)")

    if name.startswith("-") or name.endswith("-"):
        errors.append("Name cannot start or end with a hyphen")

    if "--" in name:
        errors.append("Name cannot contain consecutive hyphens")

    if not all(c.islower() or c.isdigit() or c == "-" for c in name):
        errors.append("Name must use only lowercase letters, digits, and hyphens")

    return errors


def validate_description(description: str) -> list:
    """Validate skill description and return list of errors."""
    errors = []

    if not description:
        errors.append("Missing required field: description")
        return errors

    if len(description) > 1024:
        errors.append(f"Description is too long ({len(description)} chars, max 1024)")

    if "<" in description or ">" in description:
        errors.append("Description cannot contain < or > characters")

    return errors


ALLOWED_PROPERTIES = {"name", "description", "license", "allowed-tools", "metadata"}


def validate_frontmatter(frontmatter: dict) -> list:
    """Validate frontmatter properties and return list of errors."""
    errors = []

    if frontmatter is None:
        errors.append("Invalid or missing YAML frontmatter")
        return errors

    # Check for unknown top-level properties
    for key in frontmatter.keys():
        if key not in ALLOWED_PROPERTIES:
            errors.append(f"Unknown frontmatter property: {key}")

    return errors


def validate_skill(skill_path: str) -> bool:
    """Validate a skill and return True if valid, False otherwise."""

    skill_dir = Path(skill_path)
    errors = []

    # Check directory exists
    if not skill_dir.exists():
        print(f"Error: Path does not exist: {skill_dir}")
        return False

    if not skill_dir.is_dir():
        print(f"Error: Path is not a directory: {skill_dir}")
        return False

    # Check for SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"Error: SKILL.md not found in {skill_dir}")
        return False

    # Parse and validate frontmatter
    content = skill_md.read_text()
    frontmatter = parse_frontmatter(content)

    errors.extend(validate_frontmatter(frontmatter))

    if frontmatter:
        errors.extend(validate_name(frontmatter.get("name", "")))
        errors.extend(validate_description(frontmatter.get("description", "")))

    # Report results
    if errors:
        print(f"Validation errors for {skill_dir.name}:")
        for error in errors:
            print(f"  - {error}")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Validate a skill definition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quick_validate.py ./my-skill
        """
    )
    parser.add_argument(
        "skill_path",
        help="Path to the skill folder to validate"
    )

    args = parser.parse_args()

    if validate_skill(args.skill_path):
        print(f"✓ Skill is valid: {args.skill_path}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
