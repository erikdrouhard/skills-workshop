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

### Review Current File or Directory

```bash
codex --model gpt-5.2-codex --approval-mode full-auto "Review this code for bugs, security issues, and architecture problems. Be specific about file paths and line numbers."
```

### Review Specific Files

```bash
codex --model gpt-5.2-codex --approval-mode full-auto "Review <file_path> for bugs, security issues, and architecture problems. Be specific about file paths and line numbers."
```

### Review Recent Changes

```bash
codex --model gpt-5.2-codex --approval-mode full-auto "Review the recent git changes for bugs, security issues, and architecture problems. Use git diff to see what changed."
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

1. Determine what to review (current directory, specific files, or git changes)
2. Select appropriate review prompt from examples above or customize
3. Run codex command with `--model gpt-5.2-codex --approval-mode full-auto`
4. Present findings to user with file paths and line numbers
5. Offer to help address any issues identified

## Reference

For detailed GPT-5.2 prompting patterns, see [references/gpt52-prompting.md](references/gpt52-prompting.md).
