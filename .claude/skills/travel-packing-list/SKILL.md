---
name: travel-packing-list
description: Generate personalized travel packing checklists. Use when user wants to create a packing list, prepare for a trip, or asks what to pack for travel. Triggers on /travel-packing-list commands or travel packing requests.
---

# Travel Packing List

Help the user build a packing checklist based on what they tell you they need. Do not assume or suggest items—ask the user directly.

## Workflow

### 1. Ask What Categories to Include

Use AskUserQuestion tool if available:

```
questions:
  - question: "What categories do you want in your packing list?"
    header: "Categories"
    options:
      - label: "Clothing"
        description: "Shirts, pants, shoes, etc."
      - label: "Toiletries"
        description: "Personal care items"
      - label: "Electronics"
        description: "Devices, chargers, adapters"
      - label: "Documents"
        description: "Passport, tickets, reservations"
    multiSelect: true
```

If AskUserQuestion is unavailable, ask in chat: "What categories would you like in your packing list? (e.g., clothing, toiletries, electronics, documents, gear, medications, etc.)"

### 2. Ask What Items for Each Category

For each category the user selected, ask them to list the specific items they want to bring.

Example prompt: "What clothing items do you want to pack?"

Let the user tell you exactly what they need. Do not pre-populate or suggest items unless the user explicitly asks for suggestions.

### 3. Generate Checklist

Create `checklist.md` containing only the items the user specified:

```markdown
# Travel Packing Checklist

## [Category 1]
- [ ] [item user specified]
- [ ] [item user specified]

## [Category 2]
- [ ] [item user specified]
- [ ] [item user specified]
```

Write the checklist to `checklist.md` in the current directory.
