---
title: "Launch film voice: approve by ear; narration-free product film prompt"
author: Quinn
date: 2026-10-21
branch: main
cost: { minutes: 4, tokens: 54840 }
touches:
  - prompts/marketing/README.md
  - prompts/marketing/app-launch-film-v2.txt
  - prompts/marketing/app-product-film-silent.txt
---

## Decided
- MedTick film's voice was wrong for the brand. Root cause in v2: rubric (c) rejected "flatter" takes, so it rewarded the most animated voice (Chatterbox's single built-in voice, 4.1 st spread); the example brief said "a slight smile"; nobody listened before delivery.
- v2 now has VOICE_PROFILE (default low baritone, General American male, documentary register), VOICE_SOURCE (tts|recording), CHECKPOINTS default "voice" with an audition reel and approval-by-ear gate G4a, and a pitch band (median ~85–120 Hz, 2–4 st spread, no rising terminals). An unapproved voice means partial status.
- New prompts/marketing/app-product-film-silent.txt: no narration, 4:5 30 s default, modeled on ~/Downloads/m2-res_1350p.mp4 (Quests ad): UI lifted out of the device, typing in the real input, breadth cylinder, payoff hold, icon then wordmark then typed tagline.

## Tried and ruled out
- Choosing a voice on metrics alone: measurements filter out broken takes but cannot judge fit.

## Watch out
- Prompts are pasted into other repos, so the silent prompt is self-contained and duplicates v2's truth and render rules on purpose.
