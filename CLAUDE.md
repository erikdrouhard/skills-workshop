# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a skills workshop repository for learning how to create Claude Code skills. Skills are portable folders of expertise that extend Claude's capabilities with specialized knowledge, workflows, and tools.

## Repository Structure

```
skills-workshop/
├── .claude/skills/       # All skills live here
├── NOTES.md              # Workshop lecture notes
└── *.md                  # Example outputs (hr-letter variants)
```

## Skill Structure

Every skill follows this pattern:

```
skill-name/
├── SKILL.md              # Required: frontmatter (name, description) + instructions
├── scripts/              # Optional: executable Python/Bash for deterministic tasks
├── references/           # Optional: docs loaded as needed to save tokens
└── assets/               # Optional: templates, images, data files (never loaded into context)
```

## Creating Skills

Use the `skill-creator` skill or run scripts directly:

```bash
# Initialize a new skill from template
python .claude/skills/skill-creator/scripts/init_skill.py <skill-name> --path .claude/skills

# Validate a skill
python .claude/skills/skill-creator/scripts/quick_validate.py .claude/skills/<skill-name>

# Package for distribution
python .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/<skill-name>
```

## Preferences

- Do NOT run `package_skill.py` when creating skills. The `.skill` file is only needed for distribution and should only be created when explicitly requested.

## Key Constraints

- Skill names: lowercase, digits, hyphens only; no starting/ending/double hyphens; max 64 chars
- Descriptions: max 1024 chars; must explain both what the skill does AND when to trigger it
- SKILL.md body: keep under 500 lines; move detailed docs to references/
- References: keep flat (one level deep from SKILL.md)

## Available Skills

**Writing/Copywriting:**
- `halbert-style`, `sugarman-style`, `ogilvy-style` — Rewrite content in legendary copywriter styles
- `carlton-subject` — Generate catchy email subject lines
- `british-spelling`, `british-slang` — American to British conversions

**Utilities:**
- `password-generator` — Secure passwords and passphrases via script
- `party-invite` — Generate invitations from template asset
- `skill-creator` — Guide and scripts for creating new skills
- `internal-comms` — Templates for company communications

**Simple:**
- `hello-world`, `current-date` — Basic demonstration skills


## Running scripts

## Python
- Unless instructed otherwise, always use the `uv` Python environment and package manager for Python.
  - `uv run ...` for running a python script.
  - `uvx ...` for running program directly from a PyPI package.
  - `uv ... ...` for managing environments, installing packages, etc...

**JavaScript/Node/TypeScript**:
- preffered to use `bunx` to run scripts in bun environment with dependencies isolated