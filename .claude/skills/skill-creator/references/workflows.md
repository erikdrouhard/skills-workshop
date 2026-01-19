# Workflow Patterns

Use these patterns when skills involve multi-step processes.

## Sequential Workflows

For tasks with ordered steps, provide an overview of the process:

```markdown
## PDF Form Filling Workflow

Follow these stages in order:

1. **Analyze form** - Identify all fillable fields and their types
2. **Create field mapping** - Map input data to form field names
3. **Validate mapping** - Verify all required fields have values
4. **Fill form** - Populate fields using pdftk or equivalent
5. **Verify output** - Confirm all fields filled correctly
```

## Conditional Workflows

For tasks requiring decision-making branches:

```markdown
## Document Modification Workflow

First, determine the modification type:

**Creating a new document?**
→ Follow the Creation workflow below

**Editing an existing document?**
→ Follow the Editing workflow below

### Creation Workflow
1. Initialize document structure
2. Add content sections
3. Apply formatting
4. Save and validate

### Editing Workflow
1. Load existing document
2. Locate target content
3. Apply modifications
4. Preserve formatting
5. Save and validate
```

## Best Practices

- Provide process overview at the beginning
- Number steps for sequential tasks
- Use clear decision points for branches
- Keep each step focused and actionable
