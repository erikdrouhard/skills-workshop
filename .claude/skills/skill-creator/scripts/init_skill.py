#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill directory from a template.

Usage:
    python init_skill.py <skill-name> --path <output-directory>

Example:
    python init_skill.py my-awesome-skill --path ~/.claude/skills
"""

import argparse
import os
import stat
import sys
from pathlib import Path


def to_title_case(skill_name: str) -> str:
    """Convert hyphenated skill name to title case."""
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def validate_skill_name(name: str) -> bool:
    """Validate skill name follows hyphen-case convention."""
    if not name:
        return False
    if name.startswith("-") or name.endswith("-"):
        return False
    if "--" in name:
        return False
    if not all(c.islower() or c.isdigit() or c == "-" for c in name):
        return False
    if len(name) > 64:
        return False
    return True


def create_skill_md(skill_name: str) -> str:
    """Generate the SKILL.md template content."""
    title = to_title_case(skill_name)
    return f'''---
name: {skill_name}
description: TODO - Describe what this skill does and when it should be used. Include specific triggers and contexts.
---

# {title}

TODO: Add overview of what this skill does.

## Quick Start

TODO: Add basic usage instructions.

## Features

TODO: List the main features/capabilities.

## Resources

This skill includes the following resources:

- **scripts/**: Executable scripts for automation tasks
- **references/**: Documentation and reference materials
- **assets/**: Templates, images, and other output files

TODO: Update or remove sections based on what your skill actually includes.
'''


def create_example_script() -> str:
    """Generate an example Python script."""
    return '''#!/usr/bin/env python3
"""
Example script - Replace or delete this file.

This is a placeholder to demonstrate the scripts/ directory structure.
Add your own scripts here for tasks that need deterministic reliability.
"""

def main():
    print("Hello from example script!")
    # TODO: Implement your script logic here

if __name__ == "__main__":
    main()
'''


def create_example_reference() -> str:
    """Generate an example reference document."""
    return '''# Example Reference

This is a placeholder reference file. Replace or delete it.

## When to Use References

Store documentation here that Claude should reference while working:
- API documentation
- Database schemas
- Domain knowledge
- Company policies
- Detailed workflow guides

## Best Practices

- Keep SKILL.md lean by moving detailed information here
- Structure longer files with a table of contents
- Use grep-searchable patterns for large files (>10k words)
'''


def create_example_asset() -> str:
    """Generate an example asset placeholder."""
    return '''# Example Asset

This is a placeholder file in the assets/ directory.

Assets are files used in output (not loaded into context):
- Templates (HTML, DOCX, PPTX, etc.)
- Images and icons
- Fonts
- Boilerplate code
- Sample documents

Replace or delete this file and add your actual assets.
'''


def init_skill(skill_name: str, output_path: str) -> None:
    """Initialize a new skill directory with template files."""

    # Validate skill name
    if not validate_skill_name(skill_name):
        print(f"Error: Invalid skill name '{skill_name}'")
        print("Skill names must:")
        print("  - Use lowercase letters, digits, and hyphens only")
        print("  - Not start or end with a hyphen")
        print("  - Not contain consecutive hyphens")
        print("  - Be 64 characters or less")
        sys.exit(1)

    # Create skill directory path
    skill_dir = Path(output_path) / skill_name

    if skill_dir.exists():
        print(f"Error: Directory already exists: {skill_dir}")
        sys.exit(1)

    # Create directory structure
    directories = [
        skill_dir,
        skill_dir / "scripts",
        skill_dir / "references",
        skill_dir / "assets",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created: {directory}")

    # Create SKILL.md
    skill_md_path = skill_dir / "SKILL.md"
    skill_md_path.write_text(create_skill_md(skill_name))
    print(f"Created: {skill_md_path}")

    # Create example files
    example_script = skill_dir / "scripts" / "example.py"
    example_script.write_text(create_example_script())
    # Make script executable
    example_script.chmod(example_script.stat().st_mode | stat.S_IEXEC)
    print(f"Created: {example_script}")

    example_ref = skill_dir / "references" / "example.md"
    example_ref.write_text(create_example_reference())
    print(f"Created: {example_ref}")

    example_asset = skill_dir / "assets" / "example.md"
    example_asset.write_text(create_example_asset())
    print(f"Created: {example_asset}")

    print()
    print(f"✓ Skill '{skill_name}' initialized successfully!")
    print()
    print("Next steps:")
    print(f"  1. Edit {skill_md_path} to add your skill's instructions")
    print(f"  2. Add scripts, references, and assets as needed")
    print(f"  3. Delete any example files you don't need")
    print(f"  4. Run package_skill.py when ready to distribute")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new skill from a template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python init_skill.py my-skill --path ~/.claude/skills
  python init_skill.py pdf-editor --path ./skills
        """
    )
    parser.add_argument(
        "skill_name",
        help="Name of the skill (hyphen-case, e.g., 'my-awesome-skill')"
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Output directory where the skill folder will be created"
    )

    args = parser.parse_args()
    init_skill(args.skill_name, args.path)


if __name__ == "__main__":
    main()
