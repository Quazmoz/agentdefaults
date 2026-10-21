---
title: "Silent product film: phone + Wear OS both required"
author: Quinn
date: 2026-10-21
branch: main
cost: { minutes: 4, tokens: 89545 }
touches:
  - prompts/marketing/README.md
  - prompts/marketing/app-product-film-silent-phone-watch.txt
---

## Decided
- New prompts/marketing/app-product-film-silent-phone-watch.txt; app-product-film-silent.txt untouched. README row + paragraph added.
- Section 3A defines presence: watch module needs a user surface (activity, tile, complication, watch face, ongoing activity); setup-only phone module or headless watch module doesn't count. COMPANION_REPO setting covers phone/watch split across repos.
- When both present: each device focal >=25% of runtime, one real moment each, a shared shot at real scale, both established within 8 s. Gate G5.10; no override.

## Tried and ruled out
- Dropping an uncapturable watch to reach "completed": rejected; rebuild from source with PARTIAL fidelity instead.

## Watch out
- In PAIR_INDEPENDENT a shared-element handoff phone->watch, or identical user data on both screens, implies sync. The prompt bans both.
