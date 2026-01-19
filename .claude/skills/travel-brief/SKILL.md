---
name: travel-brief
description: Generate comprehensive travel briefs with destination research and packing checklists. Use when user wants to plan a trip, prepare travel documentation, or asks for destination information combined with packing needs. Triggers on /travel-brief commands or requests like "help me prepare for my trip to [destination]".
---

# Travel Brief

Create a complete travel brief document combining destination research with a personalized packing checklist.

## Workflow

### 1. Gather Trip Details

Use AskUserQuestion to collect:

```yaml
questions:
  - question: "Where are you traveling to?"
    header: "Destination"
    options:
      - label: "Europe"
        description: "European countries"
      - label: "Asia"
        description: "Asian countries"
      - label: "Americas"
        description: "North/South America"
      - label: "Other"
        description: "Other regions"
    multiSelect: false
  - question: "What time of year will you be traveling?"
    header: "Season"
    options:
      - label: "Spring (Mar-May)"
        description: "Mild temperatures"
      - label: "Summer (Jun-Aug)"
        description: "Warm/hot weather"
      - label: "Fall (Sep-Nov)"
        description: "Cooling temperatures"
      - label: "Winter (Dec-Feb)"
        description: "Cold weather"
    multiSelect: false
```

Follow up to get the specific city/country if they selected a region.

### 2. Research Destination

Use WebSearch to find current information about:

- **Currency**: Local currency and exchange considerations
- **Language**: Official language(s) and common phrases
- **Popular attractions**: Top 5-7 must-see places
- **Weather**: Typical conditions for the travel season
- **Practical tips**: Visa requirements, power outlets, tipping customs

### 3. Generate Packing Checklist

Invoke the `travel-packing-list` skill using the Skill tool:

```
skill: "travel-packing-list"
```

This will guide the user through selecting packing categories and items. The checklist will be written to `checklist.md`.

### 4. Create Travel Brief Document

After gathering all information, create `trip-[location].md` (use lowercase, hyphenated location name):

```markdown
# Trip to [Location]

**Travel Period:** [Season/Dates]

## Destination Overview

### Essential Info
| | |
|---|---|
| **Currency** | [currency name and code] |
| **Language** | [official language(s)] |
| **Time Zone** | [timezone] |
| **Power Outlets** | [outlet type and voltage] |

### Weather
[Brief description of expected weather for the travel season]

## Top Attractions

1. **[Attraction Name]** - [Brief description]
2. **[Attraction Name]** - [Brief description]
[etc.]

## Practical Tips

- [Visa/entry requirements]
- [Tipping customs]
- [Transportation tips]
- [Safety considerations]

## Packing Checklist

[Insert the checklist content from checklist.md here]

---
*Generated with Travel Brief skill*
```

### 5. Cleanup

After creating the combined travel brief:
- Delete the separate `checklist.md` file (content is now in the brief)
- Inform the user their travel brief is ready
