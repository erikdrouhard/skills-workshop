# GPT-5.2 Prompting Guide for Code Review

Reference: https://cookbook.openai.com/examples/gpt-5/gpt-5-2_prompting_guide

## Key Behavioral Characteristics

GPT-5.2 delivers more deliberate scaffolding and stronger instruction adherence compared to earlier versions. Shows improved performance specifically on coding tasks.

## Prompting Patterns for Code Review

### Verbosity Control

Give clear and concrete length constraints. For code review:
- "Keep response under 500 words"
- "Brief yes/no assessment only"
- "Detailed multi-point analysis with examples"

### Scope Discipline

Explicitly forbid scope drift:
- "No extra features, no added components"
- "Focus only on bugs and security, not style"
- "Identify issues only, do not suggest refactoring code"

### Structured Output

For extraction tasks (security issues, design patterns), provide a schema:

```
Output as JSON:
{
  "issues": [
    {
      "file": "path/to/file.ts",
      "line": 42,
      "severity": "HIGH|MEDIUM|LOW",
      "category": "security|bug|architecture",
      "description": "Brief description"
    }
  ]
}
```

### Grounded Claims

Request specific file locations rather than generic statements:
- "Cite file paths and line numbers for each issue"
- "Reference specific function names"
- "Quote the problematic code snippet"

## Tool Usage Optimization

### Parallelization

When reviewing multiple files, Codex can read them simultaneously. Structure prompts to enable this:
- "Review src/auth.ts, src/api.ts, and src/db.ts in parallel"

### Follow-up Validation

After identifying issues, request:
- "Briefly restate what you found, where (file path), and severity"
- "Confirm each issue with the actual code location"

## Code Review Specific Patterns

### Security Audit Template

```
Perform a security audit. Check for:
1. Injection vulnerabilities (SQL, command, XSS, path traversal)
2. Authentication bypass opportunities
3. Authorization/access control issues
4. Sensitive data exposure
5. Insecure dependencies

For each finding:
- File and line number
- Vulnerability type
- Severity (CRITICAL/HIGH/MEDIUM/LOW)
- Brief remediation suggestion
```

### Bug Detection Template

```
Scan for bugs and logic errors:
1. Null/undefined reference errors
2. Off-by-one errors
3. Race conditions
4. Resource leaks
5. Unhandled edge cases

Output format: file:line - severity - description
Focus on actual bugs, not style preferences.
```

### Architecture Review Template

```
Analyze architecture for:
1. Tight coupling between modules
2. Circular dependencies
3. Single points of failure
4. Violation of separation of concerns
5. Missing error boundaries

Be specific with file paths. Identify patterns, not just individual issues.
```
