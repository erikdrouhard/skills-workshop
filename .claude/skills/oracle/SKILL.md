---
name: oracle
description: Run GPT-5.2 Codex (gpt-5.2-codex high) via OpenAI Codex CLI to review code for bugs, issues, and architecture problems. Use when the user wants a second opinion on code, requests a code review from an external model, says "ask the oracle", "get codex review", "run oracle", or wants GPT-5.2 to analyze their codebase for issues.
---

# Oracle - GPT-5.2 Codex Code Review

Run OpenAI's Codex CLI with gpt-5.2-codex high to get an expert second opinion on code quality, bugs, and architecture.

## Prerequisites

Codex CLI must be installed. If not available, install with:

```bash
npm install -g @openai/codex
```

Requires `OPENAI_API_KEY` environment variable to be set.

## Usage

Use the `codex review` subcommand for non-interactive code reviews. The `-m` flag sets the model.

### Review Specific Files

```bash
codex -m gpt-5.2-codex review "Review <file_path> for bugs, security issues, and architecture problems. Output format: file:line - [HIGH/MEDIUM/LOW] - description. Focus only on actual issues, not style."
```

### Review Uncommitted Changes

```bash
codex -m gpt-5.2-codex review --uncommitted "Review these changes for bugs, security issues, and architecture problems."
```

### Review Changes Against a Branch

```bash
codex -m gpt-5.2-codex review --base main "Review changes against main branch for bugs and issues."
```

### Review a Specific Commit

```bash
codex -m gpt-5.2-codex review --commit <sha> "Review this commit for bugs and issues."
```

## Prompting GPT-5.2 Codex Effectively

GPT-5.2 responds best to:

1. **Explicit length constraints** - Specify if you want brief or detailed analysis
2. **Scope discipline** - "Focus only on bugs and security, no refactoring suggestions"
3. **Structured output requests** - "List issues as: file:line - severity - description"
4. **Grounded claims** - Ask it to cite specific file paths and line numbers

### Example Review Prompts

**Quick bug scan:**
```
Review this codebase for bugs and security vulnerabilities. Output format:
- file:line - [HIGH/MEDIUM/LOW] - description
Keep response under 500 words. Focus only on actual issues, not style.
```

**Architecture review:**
```
Analyze the architecture of this codebase. Identify:
1. Coupling issues between modules
2. Single points of failure
3. Scalability concerns
4. Missing abstractions
Be specific with file paths. No refactoring code, just identify issues.
```

**Security audit:**
```
Security audit this code. Check for:
- Injection vulnerabilities (SQL, command, XSS)
- Authentication/authorization issues
- Data exposure risks
- Dependency vulnerabilities
List each finding with file:line and severity rating.
```

## Workflow

1. Determine what to review (specific files, uncommitted changes, branch diff, or commit)
2. Select appropriate review prompt from examples above or customize
3. Run `codex -m gpt-5.2-codex review` with the appropriate flags
4. Present findings to user with file paths and line numbers
5. Offer to help address any issues identified

## CLI Reference

```
codex review [OPTIONS] [PROMPT]

Options:
  --uncommitted        Review staged, unstaged, and untracked changes
  --base <BRANCH>      Review changes against the given base branch
  --commit <SHA>       Review the changes introduced by a commit
  --title <TITLE>      Optional commit title to display in the review summary
  -m, --model <MODEL>  Model to use (e.g., gpt-5.2-codex)
  -c, --config <k=v>   Override config values (e.g., -c approval=never)
```

## Reference

For detailed GPT-5.2 prompting patterns, see [references/gpt52-prompting.md](references/gpt52-prompting.md).
