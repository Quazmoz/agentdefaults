---
title: "Launch film prompt v2: phone/watch form-factor modes"
author: Quinn
date: 2026-10-20
branch: main
cost: { minutes: 5, tokens: 98383 }
touches:
  - prompts/marketing/README.md
  - prompts/marketing/app-launch-film-v2.txt
---

## Decided
- prompts/marketing/app-launch-film-v2.txt is a new file; app-launch-film.txt stays untouched. README row + summary paragraph added.
- Four modes from repo evidence: PHONE, WATCH, PAIR_INDEPENDENT, PAIR_CONNECTED. Cross-device claims ("syncs", "send to watch") need code trace AND paired-emulator runtime capture; "works without your phone" needs standalone=true AND an unpaired-watch run.
- Different applicationId/signing between phone and watch modules = Data Layer link cannot work; mode falls to PAIR_INDEPENDENT.
- Story budget table sums to 84 s (the v1 default story summed to 83–103 s, overrunning its own 75–90 s target).

## Tried and ruled out
- Showing a code-proven-but-unpaired sync as an EXPLAINED diagram: rejected, a code path can be dead; cut the scene and report the pairing blocker instead.

## Watch out
- validate-agentdefaults.py fails on baseline from ~759 broken Markdown links under local-audits/; not caused by prompt edits. Filter with grep -v local-audits.
- Tile DEBUG_SURFACE adb syntax and Android Studio emulator pairing flow were not executed; the prompt tells agents to verify current docs.
