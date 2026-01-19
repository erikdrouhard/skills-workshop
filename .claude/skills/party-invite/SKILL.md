---
name: party-invite
description: Generate personalized party invitation emails. Use when user wants to create a party invite, send a party invitation, or write an invite email for an event or celebration.
---

# Party Invite Generator

Generate party invitations using the template in `assets/invite-template.txt`.

## Usage

Run the script with the guest's details:

```bash
python scripts/generate_invite.py --name "NAME" --date "DATE" --dress-code "DRESS_CODE"
```

**Required arguments:**
- `--name` / `-n` — Guest's name
- `--date` / `-d` — Party date and time
- `--dress-code` / `-c` — Dress code

**Optional:**
- `--output-dir` / `-o` — Where to save (default: current directory)

## Example

```bash
python scripts/generate_invite.py \
  --name "Sarah" \
  --date "Saturday, February 15th at 7pm" \
  --dress-code "Smart Casual"
```

Creates `party-invite-sarah.md` with the personalized invitation.

## Workflow

1. Collect from user: name, date, dress code
2. Run the script with those values
3. Show user the generated invite file
