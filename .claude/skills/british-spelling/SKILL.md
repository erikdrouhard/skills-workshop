---
name: british-spelling
description: Converts American English spelling to British English spelling. Usage: /british-spelling <word>
---

Convert the following American English word to its British English spelling: {{args}}

Rules for conversion:
- -or → -our (color → colour, honor → honour, favor → favour)
- -ize → -ise (organize → organise, realize → realise)
- -er → -re (center → centre, theater → theatre, meter → metre)
- -og → -ogue (catalog → catalogue, dialog → dialogue)
- -ense → -ence (defense → defence, offense → offence, license → licence)
- -l- → -ll- before suffixes (traveling → travelling, canceled → cancelled)
- -e- dropped in American (aging → ageing, judgment → judgement)

If the word is already in British spelling or has no British variant, state that.

Respond with:
**American:** [input word]
**British:** [converted word]
